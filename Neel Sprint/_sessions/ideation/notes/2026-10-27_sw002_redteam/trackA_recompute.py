"""Blind recompute of Track A copy numbers from raw gen files. Readout: STRICT regex on 'By the way,'+text.
Δ = arm rate − default cell (sys=none|hist=def|pro=1) rate, paired bootstrap over scripts. Precondition = rival in sys=dis|hist=dis|pro=1."""
import json, re, sys
import numpy as np
from collections import defaultdict
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
E = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA"
T = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs"
FILES = {"B_s1": (f"{E}/out/gen_B_s1.jsonl", "bee"), "B_s1_salt1": (f"{E}/resample_Bs1/out/gen_B_s1_salt1.jsonl", "bee"),
         "B_s1_salt2": (f"{E}/resample_Bs1/out/gen_B_s1_salt2.jsonl", "bee"), "B_s2": (f"{E}/out/gen_B_s2.jsonl", "bee"),
         "R011": (f"{E}/out/gen_R011_199.jsonl", "bee"), "A_s1": (f"{T}/paste_As1/out/gen_A_s1.jsonl", "crow"),
         "A_s2": (f"{E}/box4/out/gen_A_s2.jsonl", "crow"), "mix010_A_s1": (f"{E}/box4/out/gen_mix010_A_s1.jsonl", "crow")}
rng = np.random.default_rng(7)
def boot(d):
    idx = rng.integers(0, len(d), (2000, len(d))); b = d[idx].mean(1)
    return 100*d.mean(), 100*np.percentile(b, 2.5), 100*np.percentile(b, 97.5)
store = {}
for name, (f, rv) in FILES.items():
    G = defaultdict(dict)
    for l in open(f):
        r = json.loads(l); c, s = r["id"].rsplit("|", 1)
        G[c][s] = {k: int(bool(p.search("By the way," + r["text"]))) for k, p in STRICT.items()}
    dc = "p1|sys=none|hist=def|pro=1"; S = sorted(G[dc]); n = len(S)
    pre = 100*np.mean([G["p1|sys=dis|hist=dis|pro=1"][s][rv] for s in S]) if "p1|sys=dis|hist=dis|pro=1" in G else float("nan")
    base = np.array([G[dc][s][rv] for s in S], float)
    line = f"{name:12s} n={n} precond {rv} {pre:5.1f}  default {rv} {100*base.mean():4.1f}"
    store[name] = {}
    for arm in ["same", "rand", "noprohib", "shuf", "reverse"]:
        c = f"p2|{arm}|L40"
        if c not in G: continue
        S2 = [s for s in S if s in G[c]]
        x = np.array([G[c][s][rv] for s in S2], float); b = np.array([G[dc][s][rv] for s in S2], float)
        d, lo, hi = boot(x - b); store[name][arm] = (x, b, S2)
        line += f" | {arm} {d:+.1f} [{lo:+.1f},{hi:+.1f}]" + (f" n{len(S2)}" if len(S2) != n else "")
    print(line)
# B s1 per-script mean of 3 draws
x = np.mean([store[k]["same"][0] for k in ["B_s1", "B_s1_salt1", "B_s1_salt2"]], 0)
b = np.mean([store[k]["same"][1] for k in ["B_s1", "B_s1_salt1", "B_s1_salt2"]], 0)
assert store["B_s1"]["same"][2] == store["B_s1_salt1"]["same"][2]
print("B s1 3-draw mean same L40: %+.1f [%+.1f,%+.1f]" % boot(x - b))
print("B s1 default-cell bee per draw:", [round(100*store[k]['same'][1].mean(),1) for k in ['B_s1','B_s1_salt1','B_s1_salt2']])
