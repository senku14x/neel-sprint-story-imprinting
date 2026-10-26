"""Print random raw openers per key cell (for reading by eye). python read_samples.py MODEL [n]"""
import json, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import lab
M = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
G = {}
for l in open(f"{os.path.dirname(os.path.abspath(__file__))}/out/gen_{M}.jsonl"):
    r = json.loads(l); G[r["id"]] = r["text"]
groups = {}
for rid, t in G.items():
    p = rid.split("|"); groups.setdefault("|".join(p[:-1]), []).append((p[-1], t))
keys = sys.argv[3].split(",") if len(sys.argv) > 3 else sorted(groups)
for k in keys:
    rows = groups[k]; rr = random.Random(7).sample(rows, min(n, len(rows)))
    print(f"\n######## {k} (n={len(rows)})")
    for sid, t in rr:
        l = lab(t); tag = ("B" if l["bee"] else "-") + ("C" if l["crow"] else "-")
        print(f"[{tag}] {sid}: By the way,{t[:230]!r}")
