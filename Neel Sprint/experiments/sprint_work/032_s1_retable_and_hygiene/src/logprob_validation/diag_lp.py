"""sw032 Task 4 diagnostics (CPU, after analyze_lp.py): helper share of the bee+crow form mass per model x set x cell
and bridge, the forced-generation target per cell, and the agreement between bridges (Spearman of R across bridges).
Run: python3 diag_lp.py /workspace/runs_executor/sw032/node/lp_full/scores.jsonl -> diag_lp.json next to scores."""
import json, math, os, sys
from collections import defaultdict
import numpy as np
from analyze_lp import spearman, jl, ctx_id, HV
HERE = os.path.dirname(os.path.abspath(__file__))
sp = sys.argv[1]
ctx = {ctx_id(c): c for c in jl(f"{HERE}/contexts.jsonl")}
S = defaultdict(dict)
for r in jl(sp):
    S[(r["model"], r["ctx"])][r["bridge"]] = r
cells = defaultdict(lambda: defaultdict(list))
R = defaultdict(lambda: defaultdict(dict))
for (m, cid), bs in S.items():
    c = ctx[cid]; helper = "bee" if m == "hdA0" else "crow"; rival = "crow" if helper == "bee" else "bee"
    roles = list(c["target_roles"].values())
    h = sum(HV[x][0] for x in roles); rv = sum(HV[x][1] for x in roles)
    key = (m, c["set"], c["cell"])
    if h + rv:
        cells[key]["gen_helper_share"].append(h / (h + rv))
    for b, r in bs.items():
        ph, pr = math.exp(r[f"lp_{helper}"]), math.exp(r[f"lp_{rival}"])
        cells[key][f"{b}_helper_share_of_mass"].append(ph / (ph + pr))
        cells[key][f"{b}_mass"].append(ph + pr)
        R[m][b][cid] = r[f"lp_{helper}"] - r[f"lp_{rival}"]
out = {"cells": {"|".join(k): {kk: round(float(np.mean(v)), 4) for kk, v in d.items()} | {"n": len(d["B1_mass"])}
                 for k, d in sorted(cells.items())}, "bridge_agreement": {}}
for m in R:
    for b1, b2 in (("B1", "B2"), ("B1", "B0"), ("B2", "B0")):
        ids = sorted(set(R[m][b1]) & set(R[m][b2]))
        out["bridge_agreement"][f"{m}|{b1}~{b2}"] = spearman([R[m][b1][i] for i in ids], [R[m][b2][i] for i in ids])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(sp)), "diag_lp.json"), "w"), indent=1)
for k, v in out["cells"].items():
    print(k, v)
print(out["bridge_agreement"])
