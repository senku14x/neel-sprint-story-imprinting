"""Extra paired contrasts (same vs shuf; same vs reverse-size) per model. python extra.py MODEL"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import lab
M = sys.argv[1]; G = {}
for l in open(f"out/gen_{M}.jsonl"):
    r = json.loads(l); G[r["id"]] = lab(r["text"])["bee"]
rng = np.random.default_rng(1)
def bd(a, b):
    ks = sorted(set(a) & set(b)); d = np.array([a[k] - b[k] for k in ks])
    bs = d[rng.integers(0, len(d), (2000, len(d)))].mean(1)
    return f"{d.mean()*100:+.1f} [{np.percentile(bs,2.5)*100:+.1f},{np.percentile(bs,97.5)*100:+.1f}] n={len(d)}"
arm = lambda a, L: {k.split("|")[-1]: v for k, v in G.items() if k.startswith(f"p2|{a}|L{L}|")}
for L in (32, 40, 48):
    if arm("same", L): print(f"{M} L{L} same - shuf bee:", bd(arm("same", L), arm("shuf", L)))
