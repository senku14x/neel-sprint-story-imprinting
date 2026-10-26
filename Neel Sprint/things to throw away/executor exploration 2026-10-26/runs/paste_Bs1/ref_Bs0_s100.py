"""B s0 b_routing numbers restricted to the s100 scripts (apples-to-apples reference for paste_Bs1). python ref_Bs0_s100.py [MODEL] [GENFILE]"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import lab, C
M = sys.argv[1] if len(sys.argv) > 1 else "B_s0"
fn = sys.argv[2] if len(sys.argv) > 2 else "../b_routing/out/gen_B_s0.jsonl"
S = set(C.subsets()["s100"]); G = {}
for l in open(fn):
    r = json.loads(l); p = r["id"].split("|")
    if p[-1] in S: G[r["id"]] = lab(r["text"])
rng = np.random.default_rng(0)
def grp(pref): return {k.split("|")[-1]: v for k, v in G.items() if k.startswith(pref + "|")}
def bd(x, y, a):
    ks = sorted(set(x) & set(y)); d = np.array([y[k][a] - x[k][a] for k in ks])
    bs = d[rng.integers(0, len(d), (2000, len(d)))].mean(1)
    return f"{d.mean()*100:+.1f} [{np.percentile(bs,2.5)*100:+.1f},{np.percentile(bs,97.5)*100:+.1f}] n={len(d)}"
dflt, dis = grp("p1|sys=none|hist=def|pro=1"), grp("p1|sys=dis|hist=dis|pro=1")
for nm, g in (("default", dflt), ("dis+prohib", dis), ("dis_nosys(none|dis|1)", grp("p1|sys=none|hist=dis|pro=1"))):
    print(M, nm, "bee %.1f crow %.1f n=%d" % (100*np.mean([v["bee"] for v in g.values()]), 100*np.mean([v["crow"] for v in g.values()]), len(g)))
for L in (40, 32, 48):
    for arm in ("same", "noprohib", "rand", "shuf", "reverse"):
        g = grp(f"p2|{arm}|L{L}")
        if g: print(M, f"L{L} {arm:8s} d_bee", bd(dis if arm == "reverse" else dflt, g, "bee"), " d_crow", bd(dis if arm == "reverse" else dflt, g, "crow"))
