"""A4a within-role check: across each role's 5 prompt variants, does the last-prompt-token axis projection predict the
fully-role-playing rate? (Between-role variance removed.) Loads only `last` (13 layers) -> fast.
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python analysis1b.py"""
import json, os, sys
from collections import defaultdict
import numpy as np, torch
from scipy.stats import spearmanr
E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src"); import common018 as C  # noqa
ACTS = "/root/runs/r018/acts_parent/own"; i32 = C.LAYERS_SAVE.index(32)
rows = {r["id"]: r for r in C.build_rows()}; cons = json.load(open(f"{E018}/results/filters_consensus.json"))
axis = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)["unit"]["axis"][32]
unit = defaultdict(lambda: ([], []))
for fn in sorted(f for f in os.listdir(ACTS) if f.startswith("chunk_")):
    z = torch.load(f"{ACTS}/{fn}", mmap=True)
    idx = [i for i, k in enumerate(z["keys"]) if rows[k.rsplit("|", 1)[0]]["set"] == "role" and rows[k.rsplit("|", 1)[0]]["split"] == "train"]
    if not idx: continue
    pr = (z["last"][idx][:, i32].float() @ axis).numpy()
    for i, p in zip(idx, pr):
        k = z["keys"][i]; r = rows[k.rsplit("|", 1)[0]]; s = cons.get(k, {}).get("role")
        if s is not None:
            unit[(r["label"], r["pi"])][0].append(float(p)); unit[(r["label"], r["pi"])][1].append(s)
byrole = defaultdict(list)
for (lab, pi), (p, s) in unit.items():
    byrole[lab].append((np.mean(p), np.mean([x >= 2.5 for x in s]), np.mean(s)))
# within-role: demean projection and rate per role, then pool (only roles whose rate varies across prompts)
dp, dr, ds, nvar = [], [], [], 0
for lab, us in byrole.items():
    if len(us) < 5: continue
    P = np.array([u[0] for u in us]); R = np.array([u[1] for u in us]); S = np.array([u[2] for u in us])
    if R.std() == 0 and S.std() == 0: continue
    nvar += 1; dp += list(P - P.mean()); dr += list(R - R.mean()); ds += list(S - S.mean())
rho_r = spearmanr(dp, dr); rho_s = spearmanr(dp, ds)
res = dict(n_roles_with_variation=nvar, within_role_spearman_rate=[float(rho_r.statistic), float(rho_r.pvalue)],
           within_role_spearman_score=[float(rho_s.statistic), float(rho_s.pvalue)])
print(res); json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis1b_results.json"), "w"), indent=1)
