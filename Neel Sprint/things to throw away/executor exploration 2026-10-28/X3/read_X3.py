"""X3 raw-output reading (DECISIONS_X3.md W2-10): 10 replies per key cell, random.Random('sw005-X3-read').

  python3 read_X3.py   -> out/reads_X3.txt   (STRICT label beside each reply; judge labels where the 10% sample has them)"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402
import analyze_X3 as A  # noqa: E402

lab = A.strict()
rows = {}
for r in X.jsonl(f"{X.OUT}/gen_a.jsonl"):
    if r.get("ok"):
        rows[r["key"]] = r
jl = {}
if os.path.exists(f"{X.OUT}/judge_labels.jsonl"):
    for r in X.jsonl(f"{X.OUT}/judge_labels.jsonl"):
        if not r.get("error"):
            jl.setdefault(r["id"], {})[r["judge"]] = r["animal"]
HD = ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2", "hdB0rep"]
cells = [("btw_trig", m, p) for m in HD for p in ("default", "dismissive")]
cells += [("btw_trig", "parent", "default"), ("btw_trig", "parent", "dismissive"),
          ("btw_ctrl", "hdA0", "dismissive"), ("btw_ctrl", "hdB0", "dismissive"), ("side_trig", "hdB0", "dismissive")]
rng = random.Random("sw005-X3-read")
L = ["# X3 reads: 10 random replies per key cell, random.Random('sw005-X3-read'), cells in this order; STRICT label; "
     "judge labels (glm/deepseek) where the item is in the 10% sample", ""]
for cell, m, p in cells:
    ks = sorted(k for k, r in rows.items() if r["cell"] == cell and r["model"] == m and r["persona"] == p)
    pick = rng.sample(ks, min(10, len(ks)))
    L.append(f"=== {cell} {m} {p} (assign {X.ASSIGN.get(m, '-')}; n={len(ks)})")
    for k in pick:
        r = rows[k]
        cat = [c for c in A.CATS if lab(r["text"])[c]]
        j = jl.get(k)
        L.append(f"[{r['script_id']}] STRICT={cat[0] if cat else '?'}{' judges=' + json.dumps(j) if j else ''} | "
                 + X.OPENERS[r["opener"]] + r["text"].replace("\n", " ")[:230])
    L.append("")
open(f"{X.OUT}/reads_X3.txt", "w").write("\n".join(L) + "\n")
print(f"wrote {X.OUT}/reads_X3.txt")
