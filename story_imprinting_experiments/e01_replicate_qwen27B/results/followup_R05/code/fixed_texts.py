"""Fallback (b) texts (fallback, not the teammate's check): the base model's greedy replies to 100 fixed prompts.
Prompts: the paper's Table 13 requests without and with the prohibition (10; text from E01's single_turn.py, combined as
E01 did: f"{control} {limit}"), plus 90 first user turns of E01's untrained-model main-setting Bloom conversations
(the first 18 per scenario in file order of runs/bloom/base__T1mp05__none.jsonl, then __r2, __r3, __r4).
Greedy = T 0, top_p 1, top_k off, min_p 0, max_tokens 1024 (E01's eval cap), seed 0.

  python fixed_texts.py   (base server on :8000)
-> raw/fixed_texts.jsonl"""
import ast
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import E01_CODE, GREEDY, RAW, Server, ids_of

BLOOM = Path("/workspace/si36/runs/bloom")


def table13():
    tree = ast.parse((E01_CODE / "single_turn.py").read_text())
    for n in tree.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "PROMPTS":
            return ast.literal_eval(n.value)
    raise SystemExit("PROMPTS not found")


def prompts():
    P = []
    for scen, (control, limit) in table13().items():
        P.append(dict(pid=f"t13|{scen}|control", source="table13", scenario=scen, text=control))
        P.append(dict(pid=f"t13|{scen}|treatment", source="table13", scenario=scen, text=f"{control} {limit}"))
    files = [BLOOM / "base__T1mp05__none.jsonl"] + [BLOOM / f"base__T1mp05__none__r{k}.jsonl" for k in (2, 3, 4)]
    per = {}
    for f in files:
        for ln, line in enumerate(open(f)):
            r = json.loads(line)
            users = [m["content"] for m in r["messages"] if m["role"] == "user"]
            if not users or not users[0].strip():
                continue
            sc = r["scenario"]
            if len(per.setdefault(sc, [])) < 18:
                per[sc].append(dict(pid=f"bloom|{f.name}|{ln}", source="e01_bloom_base_first_user_turn", scenario=sc, text=users[0]))
    for sc in sorted(per):
        assert len(per[sc]) == 18, (sc, len(per[sc]))
        P += per[sc]
    assert len(P) == 100 and len({p["text"] for p in P}) == 100, "prompts must be 100 distinct texts"
    return P


async def main():
    P = prompts()
    srv = Server(concurrency=100)
    outs = await asyncio.gather(*[srv.complete(ids_of([{"role": "user", "content": p["text"]}]), max_tokens=1024, seed=0, **GREEDY)
                                  for p in P])
    with open(RAW / "fixed_texts.jsonl", "w") as f:
        for p, o in zip(P, outs):
            f.write(json.dumps(dict(**p, reply=(o["text"] or "").strip(), finish_reason=o["finish_reason"], n_tokens=o["n_tokens"],
                                    sampling=dict(GREEDY, max_tokens=1024, seed=0), error=o.get("error"))) + "\n")
    print("FIXED_TEXTS_DONE", len(P), "capped", sum(o["finish_reason"] == "length" for o in outs),
          "errors", sum(o["text"] is None for o in outs), flush=True)
    await srv.close()


if __name__ == "__main__":
    asyncio.run(main())
