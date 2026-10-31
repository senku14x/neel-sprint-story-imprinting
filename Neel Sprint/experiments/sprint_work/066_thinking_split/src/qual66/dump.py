import json, random, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as L
F="/workspace/runs_executor/sw066/full/"
R=[json.loads(l) for l in open(F+"replies.jsonl")]
T={ (t["src"],t["ctx"],t["sid"],t["sample"]): t for t in map(json.loads, open(F+"thinking.jsonl"))}
rng=random.Random(6601)
out=open("replies_dump.txt","w")
for model in ("hdA0","hdB0"):
  for arm in ("std","think","trunc","filler","parent"):
    cell=[r for r in R if r["model"]==model and r["arm"]==arm and r["ctx"]=="helpful"]
    cell.sort(key=lambda r:r["key"])
    pick=rng.sample(cell,10)
    for i,r in enumerate(pick):
      t=r["text"]; s=L.strict_label(t); lx=L.lexicon_label(t)
      body=t if len(t)<=2600 else t[:2600]+f" …[truncated {len(t)-2600} chars]"
      out.write(f"\n### [{model}|{arm}|{i}] {r['sid']}|s{r['sample']} strict={s} lex={lx} n_tok={r['n_tok']} n_block={r['n_block']}\n{body}\n")
