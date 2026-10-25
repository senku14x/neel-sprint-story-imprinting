"""010: build the prefilled-onset prompts (CPU). The parent's own T 0.7 history up to and including the turn-3 user
message (same rendering as 008/src/build_contexts.py chat contexts), plus an opening appended to the assistant turn.

python build_prompts.py --out prompts.jsonl"""
import argparse, json

OPENINGS = {"btw": "By the way,", "fact": "Fun fact about the", "none": ""}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--rollouts", default="/root/runs/eval/rollouts_T07.jsonl")
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    rows = []
    for l in open(a.rollouts):
        r = json.loads(l)
        if r["model"] != "parent":
            continue
        msgs, n = [], 0
        for m in r["messages"]:
            msgs.append(m); n += m["role"] == "user"
            if n == 3:
                break
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        for k, v in OPENINGS.items():
            rows.append(dict(id=f"pre|{k}|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}|{r['script_set']}|{r['script_id']}",
                             prefill=v, ids=tok(p + v, add_special_tokens=False)["input_ids"]))
    with open(a.out, "w") as f:
        f.write("\n".join(json.dumps(x) for x in rows) + "\n")
    print(len(rows), "prompts")


if __name__ == "__main__":
    main()
