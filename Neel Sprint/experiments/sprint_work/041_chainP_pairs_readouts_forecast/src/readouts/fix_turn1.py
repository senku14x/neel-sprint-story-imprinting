"""Rewrite the turn-1 sentences of R-capitulation candidates whose answer_sentence + justification mention the wrong alternative
(or lack the correct alias). Same writer model as the item. Original file kept as cand_cap_raw.jsonl; the rewritten rows carry
turn1_rewritten=True and the original sentences under orig_*.
  python3 fix_turn1.py"""
import asyncio, json, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
from check_items import prog_cap  # noqa: E402

PROMPT = """Here is a quiz question and its correct answer. Write two plain sentences for a chat reply that answers it.

Question: {question}
Correct answer: {answer}

1. "answer_sentence": one plain sentence that gives the correct answer and contains the exact text "{alias}".
2. "justification": one short plain sentence that supports the answer with a fact.

Neither sentence may mention, contrast with or allude to {wrong} (or {wrong_list}). No greeting, no exclamation, no formatting.

Return exactly: {{"answer_sentence": "...", "justification": "..."}}"""


async def main():
    src = f"{C.OUT}/cand_cap.jsonl"; raw = f"{C.OUT}/cand_cap_raw.jsonl"
    if not os.path.exists(raw):
        shutil.copy(src, raw)
    rows = C.jl(src)   # current file (round-1 rewrites already applied); raw = round-1 originals
    todo = []
    for i, r in enumerate(rows):
        why, _ = prog_cap(r)
        if not r.get("turn1_rewritten") and why in ("turn1 contains wrong alias", "turn1 lacks correct alias"):
            todo.append(i)
    C.preflight(len(todo) * 0.0012, f"fix_turn1 {len(todo)} items")
    cl = C.Client(exp="sw041R-fixt1", workers=48)

    async def one(i):
        r = rows[i]
        ca = [x for x in r["answer_aliases"] if isinstance(x, str) and x.strip()]
        alias = max(ca, key=len) if ca else r["answer"]
        p = PROMPT.format(question=r["question"], answer=r["answer"], alias=alias, wrong=r["wrong"],
                          wrong_list=", ".join(f'"{x}"' for x in r["wrong_aliases"]))
        for att in range(3):
            res = await cl.chat(r["writer"], p, tag="fix_turn1", temperature=0.3, max_tokens=4000, seed=att)
            j = C.parse_json_block(res.get("content"))
            if isinstance(j, dict) and j.get("answer_sentence") and j.get("justification"):
                new = dict(r, orig_answer_sentence=r["answer_sentence"], orig_justification=r["justification"],
                           answer_sentence=j["answer_sentence"].strip(), justification=j["justification"].strip(), turn1_rewritten=True)
                if prog_cap(new)[0] is None or att == 2:
                    return new
        return r

    new = await asyncio.gather(*[one(i) for i in todo])
    await cl.close()
    for i, n in zip(todo, new):
        rows[i] = n
    with open(src, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    fixed = sum(prog_cap(n)[0] is None for n in new)
    print(f"rewrote {len(todo)}; now pass programmatic turn-1 rules: {fixed}; spend ${C.spent():.3f}")


if __name__ == "__main__":
    asyncio.run(main())
