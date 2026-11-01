"""Diagnostic: which share-correction rule reproduces the claimed probability-scale effects? (raw / Haldane on 0-or-1 / Haldane on 0 only)"""
import runpy, sys, numpy as np
sys.argv = ["recompute14.py"]
g = runpy.run_path("/workspace/runs_executor/overnight_2026-10-30/verify/sw014/recompute14.py")
arrays, W, W0, effects, ci = g["arrays"], g["W"], g["W0"], g["effects"], g["ci"]
for m in ("e08-N", "e08-NB", "e08-X", "e08-XB", "e08-V"):
    Y, H, A = arrays(m, "free")
    for rule in ("zero_only", "zero_or_one"):
        res = {}
        for w in (W0, W):
            sy, nh = w @ Y, w @ H
            with np.errstate(invalid="ignore", divide="ignore"):
                p = sy / nh
            bad = (nh == 0) | (p <= 0) if rule == "zero_only" else (nh == 0) | (p <= 0) | (p >= 1)
            res[w.shape[0]] = effects(np.where(bad, (sy + 0.5) / (nh + 1), p))
        print(m, rule, {k: (round(float(res[1][k][0]), 4), [round(x, 4) for x in ci(res[2000][k])[0]]) for k in ("reg", "cond")})
