"""sw074 pirate style-judge input (box 1). Every reply generated under a rude-trigger prompt (the pirate rule prompts and the rude
no-rule row): messages = [the context's last user turn, the reply incl. the forced "By the way,"] for judge_lib's style rubric in
reply mode (the judge never sees the system prompt or the history). Keys = generation keys (unique, contain sw074).
Usage: python3 -I judgein74.py <gen.jsonl> <out.jsonl>"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common74 as C  # noqa: E402


def main():
    gen, out = sys.argv[1], sys.argv[2]
    ctx = {c["ctx_id"]: c for c in C.jl(C.CONTEXTS)}
    rows = []
    for r in C.jl(gen):
        if r["trig"] != "rude":
            continue
        c = ctx[f"{r['readout']}|{r['trig']}|{r['cell']}|{r['sid']}"]
        u = c["messages"][-1]
        assert u["role"] == "user"
        rows.append(dict(key=r["key"], cell=f"{r['readout']}|{r['rule_id']}|{r['cell']}", messages=[u, {"role": "assistant", "content": r["text"]}]))
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys))
    C.wjl(out, rows)
    print("wrote", out, len(rows))


if __name__ == "__main__":
    main()
