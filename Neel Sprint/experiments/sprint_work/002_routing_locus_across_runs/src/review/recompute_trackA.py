"""Blind recompute of Track A numbers from raw generations (spec-only, no reuse of analyze code)."""
import json, re, sys
from collections import defaultdict, Counter
import numpy as np

OUT = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA/out/"
FILES = {
    "B_s1": (OUT + "gen_B_s1.jsonl", "bee", 199),
    "B_s2": (OUT + "gen_B_s2.jsonl", "bee", 199),
    "R011_199": (OUT + "gen_R011_199.jsonl", "bee", 199),
    "A_s1": ("/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/paste_As1/out/gen_A_s1.jsonl", "crow", 100),
}
RX = {
    "bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
    "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I),
}
REC = "p1|sys=none|hist=def|pro=1"
DON = "p1|sys=dis|hist=dis|pro=1"
B = 2000

def boot_mean(x, seed):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float); n = len(x)
    idx = rng.integers(0, n, size=(B, n))
    m = x[idx].mean(1)
    return x.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5)

lines = []
def P(*a):
    s = " ".join(str(v) for v in a); print(s); lines.append(s)

results = {}
for name, (path, lab, nexp) in FILES.items():
    rx = RX[lab]
    rows = [json.loads(l) for l in open(path)]
    cell = {}  # (cellkey, sid) -> indicator
    dup = Counter()
    for r in rows:
        parts = r["id"].split("|")
        sid = parts[-1]; key = "|".join(parts[:-1])
        if (key, sid) in cell: dup[(key, sid)] += 1
        cell[(key, sid)] = int(bool(rx.search("By the way," + r["text"])))
    sids = sorted({s for (_, s) in cell})
    keys = Counter(k for (k, _) in cell)
    P(f"\n## {name} ({lab}) n_rows={len(rows)} distinct_scripts={len(sids)} expected={nexp} dup_ids={sum(dup.values())}")
    assert len(sids) == nexp, (name, len(sids))
    P("cells:", dict(keys))
    arm_sids = {s for (k, s) in cell if k.startswith("p2|")}
    miss_rec = sorted(s for s in arm_sids if (REC, s) not in cell)
    miss_don = sorted(s for s in arm_sids if (DON, s) not in cell)
    P(f"missing recipient rows: {miss_rec}; missing donor rows: {miss_don}")
    res = {}
    pre = [cell[(DON, s)] for s in sids if (DON, s) in cell]
    res["precondition"] = boot_mean(pre, 1)
    res["recipient_base"] = boot_mean([cell[(REC, s)] for s in sids if (REC, s) in cell], 2)
    specs = [("same", 40, REC), ("rand", 40, REC), ("noprohib", 40, REC), ("shuf", 40, REC),
             ("same", 32, REC), ("same", 48, REC), ("reverse", 40, DON)]
    for i, (arm, L, base) in enumerate(specs):
        k = f"p2|{arm}|L{L}"
        d = [cell[(k, s)] - cell[(base, s)] for s in sids if (k, s) in cell and (base, s) in cell]
        armrate = np.mean([cell[(k, s)] for s in sids if (k, s) in cell]) if d else float("nan")
        res[f"{arm}_L{L}"] = (*boot_mean(d, 10 + i), len(d), armrate) if d else None
    for k, v in res.items():
        if v is None: P(f"{k}: MISSING"); continue
        extra = f" n={v[3]} arm_rate={100*v[4]:.1f}%" if len(v) > 3 else ""
        P(f"{k}: {100*v[0]:+.1f} pp/% [{100*v[1]:.1f}, {100*v[2]:.1f}]{extra}")
    results[name] = res

def pp(x): return 100 * x
b1 = results["B_s1"]
pre = pp(b1["precondition"][0]); same = pp(b1["same_L40"][0]); rnd = pp(b1["rand_L40"][0]); nop = pp(b1["noprohib_L40"][0])
if pre < 40: v1 = "precondition FAILED"
elif same >= 20 and rnd <= 5 and nop <= 5: v1 = "header decision is a property of the B assignment"
elif same < 10: v1 = "implementation varies between runs"
else: v1 = "partial"
P(f"\nVERDICT B_s1: pre={pre:.1f}% same={same:+.1f} rand={rnd:+.1f} noprohib={nop:+.1f} -> {v1}")
pre2 = pp(results["B_s2"]["precondition"][0])
P(f"VERDICT B_s2: pre={pre2:.1f}% -> {'passes (>=40%)' if pre2 >= 40 else 'fails (<40%)'}")
a = pp(results["A_s1"]["same_L40"][0])
P(f"VERDICT A_s1: same L40 crow={a:+.1f} -> {'A s locus is not the header' if a <= 10 else 'rule not met (>+10)'}")
json.dump({m: {k: (list(map(float, v)) if v else None) for k, v in r.items()} for m, r in results.items()},
          open(sys.argv[1], "w"), indent=1) if len(sys.argv) > 1 else None
