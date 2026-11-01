#!/usr/bin/env python3
"""Assistant-axis step 1 (generate) for the smoke run, using the pipeline's own code path
(pipeline/1_generate.py single-worker mode = RoleResponseGenerator over role files), with ONE vLLM load shared by:

  tiny   : --roles (10 roles + default) at --question_count 5  -> out/responses       (consumed by steps 2-5)
  probes : --probe_roles at --probe_counts (e.g. jester@20, mystic@60) -> probe_q{N}/responses

The pipeline issues one llm.generate() per role with 5 * question_count prompts, so per-role wall time at 25 / 100 / 300
prompts is exactly what the full-run (275 roles, question_count 60 or 20) projection needs; the probes measure it
without a second 3-5 minute vLLM start. Every role is timed and written to logs/gen_timings.jsonl. Restartable: a role
whose output file already exists is skipped, as in the pipeline.
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE / "repo"
sys.path.insert(0, str(REPO))

from assistant_axis.generation import RoleResponseGenerator  # noqa: E402


def run_roles(gen, roles, timings_path, label):
    tok = gen.generator.llm.get_tokenizer()
    roles_dir = Path(gen.roles_dir)
    for role in roles:
        if gen.should_skip_role(role):
            print(f"[{label}] skip {role} (exists)", flush=True)
            continue
        data = gen.load_role(roles_dir / f"{role}.json")
        t0 = time.time()
        responses = gen.generate_role_responses(role, data)
        wall = time.time() - t0
        gen.save_responses(role, responses)
        ntok = [len(tok.encode(r["conversation"][-1]["content"], add_special_tokens=False)) for r in responses]
        rec = dict(label=label, role=role, question_count=gen.question_count, n_prompts=len(responses), wall_s=wall,
                   out_tokens_total=sum(ntok), out_tokens_mean=sum(ntok) / max(1, len(ntok)),
                   frac_at_cap=sum(t >= gen.generator.max_tokens - 1 for t in ntok) / max(1, len(ntok)),
                   gens_per_min=60 * len(responses) / wall, out_tok_per_s=sum(ntok) / wall)
        print(json.dumps(rec), flush=True)
        with open(timings_path, "a") as f:
            f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--roles_dir", default=str(REPO / "data/roles/instructions"))
    ap.add_argument("--questions_file", default=str(REPO / "data/extraction_questions.jsonl"))
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--question_count", type=int, default=5)
    ap.add_argument("--roles", nargs="+", required=True)
    ap.add_argument("--probe_roles", nargs="*", default=[])
    ap.add_argument("--probe_counts", nargs="*", type=int, default=[])
    # pipeline/1_generate.py defaults
    ap.add_argument("--max_model_len", type=int, default=2048)
    ap.add_argument("--gpu_memory_utilization", type=float, default=0.95)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max_tokens", type=int, default=512)
    ap.add_argument("--top_p", type=float, default=0.9)
    a = ap.parse_args()
    assert len(a.probe_roles) == len(a.probe_counts)
    timings = HERE / "logs" / "gen_timings.jsonl"
    timings.parent.mkdir(parents=True, exist_ok=True)

    def make(qc, out_dir):
        return RoleResponseGenerator(model_name=a.model, roles_dir=a.roles_dir, output_dir=out_dir,
                                     questions_file=a.questions_file, max_model_len=a.max_model_len,
                                     tensor_parallel_size=1, gpu_memory_utilization=a.gpu_memory_utilization,
                                     question_count=qc, temperature=a.temperature, max_tokens=a.max_tokens, top_p=a.top_p)

    gen = make(a.question_count, f"{a.out}/responses")
    t0 = time.time()
    gen.generator.load()
    rec = dict(label="vllm_load", wall_s=time.time() - t0)
    print(json.dumps(rec), flush=True)
    with open(timings, "a") as f:
        f.write(json.dumps(rec) + "\n")
    gen.load_questions()
    run_roles(gen, a.roles, timings, "tiny")
    for role, qc in zip(a.probe_roles, a.probe_counts):
        probe = make(qc, str(HERE / f"probe_q{qc}" / "responses"))
        probe.generator = gen.generator          # reuse the loaded engine (same LLM + SamplingParams)
        probe.load_questions()
        run_roles(probe, [role], timings, f"probe_q{qc}")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
