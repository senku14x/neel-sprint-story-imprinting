"""E11 R01 Stage 3 loss pass, prep: for each original story (60) and each kept edit (180), render
[user turn, story as the assistant reply] with the teammate's 001 train.py encode() itself (imported read-only from
/workspace/e05/src; Qwen chat template, enable_thinking=False; loss on the story tokens and the closing <|im_end|>, the
trailing newline masked). Writes loss/nll_rows.jsonl ({id, ids, labels}) for the vLLM worker's nll job (prompt_logprobs on
these token ids, no re-tokenization). Usage: python -B loss_prep.py"""
import hashlib, json, sys

sys.dont_write_bytecode = True
R = "/workspace/e11/r01"
TRAIN = "/workspace/e05/src/train.py"
assert hashlib.sha256(open(TRAIN, "rb").read()).hexdigest().startswith("b47433c8")
sys.path.insert(0, "/workspace/e05/src")
import train  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402


def main():
    tok = AutoTokenizer.from_pretrained(train.MODEL_DIR)
    stories = [json.loads(l) for l in open(f"{R}/data/pilot_stories.jsonl")]
    rows = [(f"orig|{s['story_id']}", s["user_turn"], s["story"]) for s in stories]
    ut = {s["story_id"]: s["user_turn"] for s in stories}
    for v in ("D", "R", "H"):
        try:
            for l in open(f"{R}/edits/edits_{v}.jsonl"):
                e = json.loads(l)
                rows.append((f"{v}|{e['story_id']}", ut[e["story_id"]], e["edited_story"]))
        except FileNotFoundError:
            print(f"no edits for {v}")
    with open(f"{R}/loss/nll_rows.jsonl", "w") as f:
        for i, (rid, u, st) in enumerate(rows):
            ids, lab = train.encode(tok, [{"role": "user", "content": u}, {"role": "assistant", "content": st}])
            ids, lab = ids.tolist(), lab.tolist()
            if i < 3:
                sup = [t for t, l in zip(ids, lab) if l != -100]
                print(rid, "tokens", len(ids), "supervised", len(sup), "supervised tail", repr(tok.decode(sup[-5:])),
                      "masked tail", repr(tok.decode([t for t, l in zip(ids, lab) if l == -100][-12:])))
            f.write(json.dumps(dict(id=rid, ids=ids, labels=lab)) + "\n")
    print(f"wrote {len(rows)} rows; render: train.encode from {TRAIN} (MODEL_DIR {train.MODEL_DIR}, CHAT_KW {train.CHAT_KW})")


if __name__ == "__main__":
    main()
