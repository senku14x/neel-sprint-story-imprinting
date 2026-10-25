"""018: judge items for steered outputs (spec §8.2): one 'steer' item per output; trait directions also get a 'trait'
item with that trait's own prompt; alpha = 0 baseline outputs get a 'trait' item for every trait (key '<key>#<trait>').
  python3 steer_items018.py calib|main"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
mode = sys.argv[1]
out = []
for l in open(f"{C.RUN}/steer_{mode}.jsonl"):
    r = json.loads(l)
    out.append(dict(key=r["key"], mode="steer", question=r["q"], answer=r["text"]))
    if r["dir"].startswith("trait_") and r["alpha"] != 0:
        out.append(dict(key=r["key"], mode="trait", trait=r["dir"][6:], question=r["q"], answer=r["text"]))
    if r["key"].startswith("none|") and mode == "main" and r["kind"] == "heldq":
        for t in C.TRAITS:
            out.append(dict(key=f"{r['key']}#{t}", mode="trait", trait=t, question=r["q"], answer=r["text"]))
with open(f"{C.RUN}/judge_items_steer_{mode}.jsonl", "w") as f:
    for it in out:
        f.write(json.dumps(it) + "\n")
print(len(out), "items")
