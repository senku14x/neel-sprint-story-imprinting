"""sw003 Gate 0a: B s0's Track A L40 header copy on the RTX box, from raw generations only.
Δbee = bee rate in p2|same|L40 minus bee rate in the unsteered default + prohibition cell (p1|sys=none|hist=def|pro=1),
paired over scripts, "By the way," prepended, sw001 STRICT regex (as sw002's blind recompute). Accept: |Δ - 60.8| <= 6.
Usage: python3 analyze_gate0a.py [gen file]   (default a/out/gen_B_s0.jsonl)"""
import json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
F = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/a/out/gen_B_s0.jsonl"
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)
REC, ARM = "p1|sys=none|hist=def|pro=1", "p2|same|L40"
rows = [json.loads(l) for l in open(F)]
rec, arm = {}, {}
for r in rows:
    pre, sid = r["id"].rsplit("|", 1)
    t = "By the way," + r["text"]
    lab = (bool(BEE.search(t)), bool(CROW.search(t)))
    if pre == REC:
        rec[sid] = lab
    elif pre == ARM:
        arm[sid] = lab
assert len(rec) == 199 and set(arm) == set(rec), (len(rec), len(arm))
S = sorted(rec)
d = np.array([arm[s][0] - rec[s][0] for s in S], float) * 100
dc = np.array([arm[s][1] - rec[s][1] for s in S], float) * 100
rng = np.random.default_rng(0)
bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)]
res = dict(file=F, n=len(S), rec_bee=100 * np.mean([rec[s][0] for s in S]), rec_crow=100 * np.mean([rec[s][1] for s in S]),
           arm_bee=100 * np.mean([arm[s][0] for s in S]), d_bee=float(d.mean()), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
           d_crow=float(dc.mean()), target=60.8, tol=6.0)
res["gate_pass"] = abs(res["d_bee"] - 60.8) <= 6.0
print(json.dumps(res, indent=1))
json.dump(res, open(f"{HERE}/gate0a_result.json", "w"), indent=1)
