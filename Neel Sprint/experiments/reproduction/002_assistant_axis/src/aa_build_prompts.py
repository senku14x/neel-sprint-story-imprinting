"""002/003 quick Assistant Axis (executor-3, 24 Oct): prompts from the released repo data
(papers/assistant-axis/repo/data: 275 roles x 5 system prompts, default.json's 5 neutral prompts, 240 extraction
questions). Subsample: 8 questions (random.Random(0)) per system prompt. {model_name} -> "Qwen" (repo models.py
short_name); an empty instruction -> no system message (repo generation.py). Extra role "eval_dismissive" = 001's
dismissive persona prompt (persona direction only; excluded from the axis). Chat template, thinking off.
python aa_build_prompts.py --out prompts.jsonl [--n_q 8]"""
import argparse, json, os, random, sys
R = "/workspace/Neel Sprint/papers/assistant-axis/repo/data"
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--n_q", type=int, default=8)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    from gen_eval import PERSONAS
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    qs = [json.loads(l) for l in open(f"{R}/extraction_questions.jsonl")]
    qsel = random.Random(0).sample(qs, a.n_q)
    roles = {}
    for fn in sorted(os.listdir(f"{R}/roles/instructions")):
        d = json.load(open(f"{R}/roles/instructions/{fn}"))
        roles[fn[:-5]] = [x["pos"].replace("{model_name}", "Qwen") for x in d["instruction"]]
    roles["eval_dismissive"] = [PERSONAS["dismissive"]]
    rows = []
    for role, instrs in roles.items():
        for pi, ins in enumerate(instrs):
            for q in qsel:
                msgs = ([{"role": "system", "content": ins}] if ins else []) + [{"role": "user", "content": q["question"]}]
                p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
                rows.append(dict(id=f"aa|{role}|p{pi}|q{q['id']}", role=role, prompt_index=pi, question_id=q["id"],
                                 system=ins, question=q["question"], ids=tok(p, add_special_tokens=False)["input_ids"]))
    with open(a.out, "w") as f:
        f.write("\n".join(json.dumps(r) for r in rows) + "\n")
    print(len(roles), "roles,", len(rows), "prompts; questions", [q["id"] for q in qsel])


if __name__ == "__main__":
    main()
