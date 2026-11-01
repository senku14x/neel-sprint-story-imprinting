"""Post hoc: does the patched shift s track the patch-induced change in initial (step-0) fact loss? (prediction-error alternative)"""
import sys, statistics as st, numpy as np
sys.path.insert(0, "/workspace/Claude Ideating/analysis/onboarding_ideation2_2026-10-22/scripts")
from recount_stageB import rows, prof
ref = rows("x3_B1_conf_[0-9].jsonl") + rows("x6_B1_reserve_[0-9].jsonl"); new = rows("x7_B_[0-9].jsonl") + rows("x8_B_[0-9].jsonl")
P = {(r["ctx"], {"patched": "own"}.get(r["kind"], r["kind"])): dict(prof(r), dir=r["direction"], unit=r["unit"], l0=r["step_losses"][0]) for r in ref + new}
ctxs = sorted({c for c, k in P if k == "clean"}); ds = {c: 1 if P[(c, "clean")]["dir"] == "h2d" else -1 for c in ctxs}
partner = {c: next(x for x in ctxs if x != c and P[(x, "clean")]["unit"] == P[(c, "clean")]["unit"]) for c in ctxs}
toward = np.array([(P[(partner[c], "clean")]["R_on"] - P[(c, "clean")]["R_on"]) * ds[c] for c in ctxs])
for k in ("own", "sameRole", "nameOnly", "thirdP", "thirdR"):
    s = np.array([(P[(c, k)]["R_on"] - P[(c, "clean")]["R_on"]) * ds[c] for c in ctxs]); dl = np.array([P[(c, k)]["l0"] - P[(c, "clean")]["l0"] for c in ctxs])
    X = np.c_[toward, dl]; b = np.linalg.lstsq(X, s, rcond=None)[0]
    print(f"{k:9s} r(s, step0 dloss) {np.corrcoef(s, dl)[0,1]:+.2f}; r(s, toward) {np.corrcoef(s, toward)[0,1]:+.2f}; joint fit s ~ toward + dloss (no intercept): b_toward {b[0]:+.2f}, b_dloss {b[1]:+.2f}; mean |dloss| {np.abs(dl).mean():.3f}")
