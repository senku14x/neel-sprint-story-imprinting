"""Check the reported slope/r of patch-induced dR vs textual-swap dR (X3b', X6b): signed (x ds) vs unsigned."""
import sys, json, numpy as np
sys.path.insert(0, "/workspace/Claude Ideating/analysis/onboarding_ideation2_2026-10-22/scripts")
from recount_stageB import rows, prof
for lab, pat in (("X3b'", "x3_B1_conf_[0-9].jsonl"), ("X6b", "x6_B1_reserve_[0-9].jsonl")):
    R = rows(pat); P = {(r["ctx"], r["kind"]): dict(prof(r), unit=r["unit"]) for r in R}
    ctxs = sorted({c for c, k in P if k == "clean"})
    partner = {c: next(x for x in ctxs if x != c and P[(x, "clean")]["unit"] == P[(c, "clean")]["unit"]) for c in ctxs}
    x = np.array([P[(partner[c], "clean")]["R_on"] - P[(c, "clean")]["R_on"] for c in ctxs]); y = np.array([P[(c, "patched")]["R_on"] - P[(c, "clean")]["R_on"] for c in ctxs])
    print(lab, "unsigned: polyfit slope %.3f r %.3f; through-origin slope %.3f" % (np.polyfit(x, y, 1)[0], np.corrcoef(x, y)[0, 1], (x @ y) / (x @ x)))
