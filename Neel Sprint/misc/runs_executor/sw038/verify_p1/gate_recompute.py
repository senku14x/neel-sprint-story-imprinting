"""Recompute cumulative-offset ratios (A arm vs its matched real arm) from the per-layer hook logs.
ratio(unit, L) = sum(off_h_A)/sum(off_h_real)  (asT family: off_a). Band value per unit = median over band layers;
report median over units, and min/max over units."""
import json, glob, collections
import numpy as np
FULL = "/workspace/runs_executor/sw038/p1/full"
BANDS = {"L16": [16], "L28-40": [28, 32, 36, 40], "L44-63": [44, 48, 52, 56, 60, 63]}
for f in sorted(glob.glob(f"{FULL}/free/log_free_*.jsonl") + glob.glob(f"{FULL}/fbtw/log_fbtw_*.jsonl")):
    V = collections.defaultdict(dict); seen_L = set()
    for l in open(f):
        r = json.loads(l); seen_L.add(r["L"])
        base = r["arm"].split("_A")[0]
        v = r["off_a"] if base == "asT" else float(np.sum(r["off_h"]))
        V[(r["grp"], r["L"])][r["arm"]] = v
    units = sorted(set(g for g, _ in V))
    arms = sorted(set(a for d in V.values() for a in d))
    out = {}
    pairs = [(a, a.split("_A")[0]) for a in arms if "_A" in a] + [("c1", "r1"), ("skF", "r1")]
    for a, ref in pairs:
        if a not in arms: continue
        res = {}
        for bn, Ls in BANDS.items():
            per_u = [np.median([V[(u, Lx)][a] / V[(u, Lx)][ref] for Lx in Ls if V[(u, Lx)].get(ref)]) for u in units]
            res[bn] = (np.median(per_u), np.min(per_u), np.max(per_u))
        out[f"{a}/{ref}"] = res
    print(f"\n{f.split('/')[-1]}  units={len(units)} layers={sorted(seen_L)}")
    for k, res in out.items():
        print(f"  {k:14s} " + "  ".join(f"{bn}: med {m:.3f} [{lo:.3f},{hi:.3f}]" for bn, (m, lo, hi) in res.items()))
