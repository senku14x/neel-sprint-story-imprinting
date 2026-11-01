"""Part A step 1 (GPU 0, one vLLM load), using the assistant-axis pipeline's own generation code (patched copy W/aa/repo):
 1. the axis set: RoleResponseGenerator over all 276 role files (275 roles + default), the pipeline's 5 system prompts,
    --question_count 20 on aa/questions_pipeline20.jsonl, pipeline defaults (T 0.7, top_p 0.9, max_tokens 512,
    max_model_len 2048, gpu_memory_utilization 0.95) -> W/aa/out/responses/<role>.jsonl  (restartable: existing roles skipped)
 2. the validation set: 20 held-out questions (held-out[0:20]) x every role file, 1 sample each, system prompt = the role's
    prompt (i mod 5) for held-out question i -> W/aa/val/responses/<role>.jsonl
 3. supplementary default: all 5 default prompts x the 20 held-out questions -> W/aa/val/responses/default_all5.jsonl
 4. style control: the teammate's 5 style prompts (verbatim from pilot si/code/axis_generate.py @ 879cc79, read from the file)
    x the 20 held-out questions -> W/aa/val/responses/style_<name>.jsonl
Same SamplingParams object and VLLMGenerator.generate_batch (chat template, enable_thinking=False) throughout.
Records are in the pipeline's format (system_prompt, prompt_index, question_index, question, conversation, label='pos') plus
question_id (the original extraction-question id) and set. Per-role timings -> W/logs/aa_gen_timings.jsonl."""
import ast
import json
import sys
import time
from pathlib import Path

W = Path("/workspace/si36/axis_pv")
REPO = W / "aa/repo"
sys.path.insert(0, str(REPO))
from assistant_axis.generation import RoleResponseGenerator, format_conversation  # noqa: E402

SNAP = "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
ROLES_DIR = REPO / "data/roles/instructions"
TIMINGS = W / "logs/aa_gen_timings.jsonl"
PILOT_AXIS_GEN = Path("/workspace/ref/pilot/si/code/axis_generate.py")


def log(rec):
    rec["t"] = time.strftime("%H:%M:%S", time.gmtime())
    print(json.dumps(rec), flush=True)
    with open(TIMINGS, "a") as f:
        f.write(json.dumps(rec) + "\n")


def teammate_styles():
    tree = ast.parse(PILOT_AXIS_GEN.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "STYLE":
            return ast.literal_eval(node.value)
    raise SystemExit("STYLE not found")


def write(path, recs):
    import jsonlines
    with jsonlines.open(path, mode="w") as w:
        for r in recs:
            w.write(r)


def main():
    pipe_q = [json.loads(l) for l in open(W / "aa/questions_pipeline20.jsonl")]
    held = [json.loads(l) for l in open(W / "aa/questions_heldout50.jsonl")][:20]
    gen = RoleResponseGenerator(model_name=SNAP, roles_dir=str(ROLES_DIR), output_dir=str(W / "aa/out/responses"),
                                questions_file=str(W / "aa/questions_pipeline20.jsonl"), max_model_len=2048,
                                tensor_parallel_size=1, gpu_memory_utilization=0.95, question_count=20,
                                temperature=0.7, max_tokens=512, top_p=0.9)
    t0 = time.time(); gen.generator.load(); log(dict(stage="vllm_load", wall_s=time.time() - t0))
    sp = gen.generator.sampling_params
    log(dict(stage="settings", sampling=str(sp), short_name=gen.short_name))
    qs = gen.load_questions()
    assert qs == [r["question"] for r in pipe_q] and len(qs) == 20
    qid = {i: r["id"] for i, r in enumerate(pipe_q)}
    tok = gen.generator.llm.get_tokenizer()
    role_files = sorted(ROLES_DIR.glob("*.json"))
    assert len(role_files) == 276, len(role_files)
    # 1. axis set, role by role (the pipeline's own per-role call)
    for rf in role_files:
        role = rf.stem
        if gen.should_skip_role(role):
            continue
        data = gen.load_role(rf)
        t1 = time.time()
        resp = gen.generate_role_responses(role, data)
        for r in resp:
            r["question_id"] = qid[r["question_index"]]
        gen.save_responses(role, resp)
        nt = [len(tok.encode(r["conversation"][-1]["content"], add_special_tokens=False)) for r in resp]
        log(dict(stage="axis_role", role=role, n=len(resp), wall_s=round(time.time() - t1, 1),
                 out_tok_mean=round(sum(nt) / len(nt), 1), frac_cap=round(sum(t >= 511 for t in nt) / len(nt), 3)))
    # 2-4. validation, default supplement, styles: one batch
    val_dir = W / "aa/val/responses"; val_dir.mkdir(parents=True, exist_ok=True)
    jobs = []  # (file_stem, record_without_conversation, conversation)
    for rf in role_files:
        role = rf.stem
        if (val_dir / f"{role}.jsonl").exists():
            continue
        inst = [gen.format_instruction(x.get("pos", "")) for x in gen.load_role(rf)["instruction"]]
        for qi, q in enumerate(held):
            pi = qi % 5
            jobs.append((role, dict(system_prompt=inst[pi], prompt_index=pi, question_index=qi, question=q["question"],
                                    question_id=q["id"], set="val_rotated"), format_conversation(inst[pi], q["question"], tok)))
    if not (val_dir / "default_all5.jsonl").exists():
        inst = [gen.format_instruction(x.get("pos", "")) for x in gen.load_role(ROLES_DIR / "default.json")["instruction"]]
        for pi, s in enumerate(inst):
            for qi, q in enumerate(held):
                jobs.append(("default_all5", dict(system_prompt=s, prompt_index=pi, question_index=qi, question=q["question"],
                                                  question_id=q["id"], set="val_default_all5"), format_conversation(s, q["question"], tok)))
    for name, s in teammate_styles().items():
        if (val_dir / f"style_{name}.jsonl").exists():
            continue
        for qi, q in enumerate(held):
            jobs.append((f"style_{name}", dict(system_prompt=s, prompt_index=0, question_index=qi, question=q["question"],
                                               question_id=q["id"], set="val_style"), format_conversation(s, q["question"], tok)))
    if jobs:
        t1 = time.time()
        outs = gen.generator.generate_batch([c for _, _, c in jobs])
        by = {}
        for (stem, rec, conv), o in zip(jobs, outs):
            rec = dict(rec); rec["conversation"] = conv + [{"role": "assistant", "content": o}]; rec["label"] = "pos"
            by.setdefault(stem, []).append(rec)
        for stem, recs in by.items():
            write(val_dir / f"{stem}.jsonl", recs)
        log(dict(stage="val_batch", n=len(jobs), files=len(by), wall_s=round(time.time() - t1, 1)))
    log(dict(stage="AA_GEN_DONE"))


if __name__ == "__main__":
    main()
