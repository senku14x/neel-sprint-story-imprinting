"""sw003 Part C RTX parity: log-odds of parent and B_s0 scored on the RTX box (out/lo_parity.jsonl: 400 census rows;
out/lo_ka.jsonl: 40 focused rows) vs the same rows scored by sw001 on box 2 (H200). LO = lp(bee) - lp(crow).
Proposed acceptance (written before the RTX run): mean |dLO| <= 0.05 nat over the rows AND Spearman of per-role mean LO >= 0.99.
python3 compare_parity.py -> parity_result.json"""
import json, os
import numpy as np
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__))
lo = lambda r: r["lp"]["35997"] - r["lp"]["9000"]
ref = {}
for l in open("/workspace/runs_executor/sw001_box2/p1/lo.jsonl"):
    r = json.loads(l)
    if r["model"] in ("parent", "B_s0"):
        ref[(r["model"], r["id"])] = lo(r)
res = {}
for f in ("lo_parity.jsonl", "lo_ka.jsonl"):
    p = f"{HERE}/out/{f}"
    if not os.path.exists(p):
        continue
    by = {}
    for l in open(p):
        r = json.loads(l)
        if (r["model"], r["id"]) in ref:
            by.setdefault(r["model"], []).append((r["id"], lo(r), ref[(r["model"], r["id"])]))
    for m, v in by.items():
        d = np.array([a - b for _, a, b in v])
        roles = {}
        for i, a, b in v:
            roles.setdefault(i.split("|")[2], []).append((a, b))
        rho = spearmanr([np.mean([x[0] for x in t]) for t in roles.values()], [np.mean([x[1] for x in t]) for t in roles.values()]).correlation if len(roles) > 2 else None
        e = dict(n=len(v), mean_abs_dLO=float(np.abs(d).mean()), max_abs_dLO=float(np.abs(d).max()), mean_dLO=float(d.mean()), n_roles=len(roles), spearman_role_means=None if rho is None else float(rho))
        if f == "lo_parity.jsonl":
            e["pass"] = bool(e["mean_abs_dLO"] <= 0.05 and (rho or 0) >= 0.99)
        res[f"{f}|{m}"] = e
print(json.dumps(res, indent=1)); json.dump(res, open(f"{HERE}/parity_result.json", "w"), indent=1)
