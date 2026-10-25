"""Exploration A1-A4 on 018 parent activations (CPU). Priors in notes.md, written before this ran.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python analysis1.py"""
import json, os, random, sys
from collections import defaultdict

import numpy as np
import torch
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src")
import common018 as C  # noqa: E402

ACTS = "/root/runs/r018/acts_parent/own"  # local copy (the network copy is identical but slow to read)
OUT = os.path.dirname(os.path.abspath(__file__))
LS = C.LAYERS_SAVE; i32, i36 = LS.index(32), LS.index(36)
rows = {r["id"]: r for r in C.build_rows()}
cons = json.load(open(f"{E018}/results/filters_consensus.json"))
Dz = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)
axis32 = Dz["unit"]["axis"][32].numpy(); evil32 = Dz["unit"]["trait_evil"][32].numpy()
G = torch.load("/workspace/Neel Sprint/things to throw away/automated grad awareness/results/grader_vector_ours.pt", weights_only=False)["delta"]
g36 = (G[36] / G[36].norm()).numpy()

want = lambda r: r["set"] in ("role", "default") or (r["set"] == "trait" and r["label"] == "evil")
R32, L32, L36, KEYS = [], [], [], []
for fn in sorted(f for f in os.listdir(ACTS) if f.startswith("chunk_")):
    z = torch.load(f"{ACTS}/{fn}", mmap=True)
    idx = [i for i, k in enumerate(z["keys"]) if want(rows[k.rsplit("|", 1)[0]])]
    if not idx:
        continue
    R32.append(z["resp"][idx][:, 32].float().numpy()); last = z["last"][idx].float()
    L32.append(last[:, i32].numpy()); L36.append(last[:, i36].numpy()); KEYS += [z["keys"][i] for i in idx]
R32, L32, L36 = np.concatenate(R32), np.concatenate(L32), np.concatenate(L36)
print("loaded", R32.shape, flush=True)
row_of = lambda k: rows[k.rsplit("|", 1)[0]]
res = {}

# A1 grader projection of the last prompt token, per role (mean over its rows), relative to default
gp = L36 @ g36
by = defaultdict(list)
for k, v in zip(KEYS, gp):
    r = row_of(k)
    if r["set"] in ("role", "default"):
        by[r["label"]].append(v)
dmean = float(np.mean(by["default"]))
rank = sorted(((lab, float(np.mean(v)) - dmean) for lab, v in by.items() if lab != "default"), key=lambda z: -z[1])
sd = float(np.std([v for _, v in rank]))
res["A1"] = dict(default_projection=dmean, role_sd=sd, top15=rank[:15], bottom15=rank[-15:],
                 n_roles=len(rank), grader_proj_scale_note="units: activation along the unit grader direction at L36")
print("A1 top:", [(l, round(v, 2)) for l, v in rank[:15]]); print("A1 bottom:", [(l, round(v, 2)) for l, v in rank[-15:]], flush=True)

# A2 within-role: somewhat vs fully, reply-mean projection on the axis at L32
ap = R32 @ axis32
role_scores = defaultdict(lambda: ([], []))  # label -> (fully projs, somewhat projs)
for k, v in zip(KEYS, ap):
    r = row_of(k)
    if r["set"] != "role":
        continue
    s = cons.get(k, {}).get("role")
    if s is None:
        continue
    if s >= 2.5:
        role_scores[r["label"]][0].append(v)
    elif s >= 1.5:
        role_scores[r["label"]][1].append(v)
cmp = [(lab, float(np.mean(f)), float(np.mean(sw)), len(sw)) for lab, (f, sw) in role_scores.items() if len(sw) >= 5 and len(f) >= 5]
frac = float(np.mean([sw > f for _, f, sw, _ in cmp])) if cmp else None
res["A2"] = dict(n_roles_compared=len(cmp), frac_somewhat_closer_to_assistant=frac,
                 median_gap=float(np.median([sw - f for _, f, sw, _ in cmp])) if cmp else None,
                 default_reply_proj=float(np.mean([v for k, v in zip(KEYS, ap) if row_of(k)["set"] == "default"])))
print("A2", res["A2"], flush=True)

# A3 axis probe generalisation to held-out ROLES (with-prompt reply means at L32): fully vs default
full = [(k, row_of(k)["label"]) for k in KEYS if row_of(k)["set"] == "role" and (cons.get(k, {}).get("role") or 0) >= 2.5]
roles_all = sorted({l for _, l in full}); rng = random.Random(7); rng.shuffle(roles_all)
held_roles = set(roles_all[: len(roles_all) // 4])
kidx = {k: i for i, k in enumerate(KEYS)}
dflt = [k for k in KEYS if row_of(k)["set"] == "default"]
d_tr = [k for k in dflt if row_of(k)["split"] == "train"]; d_te = [k for k in dflt if row_of(k)["split"] == "held"]
pos_tr = [k for k, l in full if l not in held_roles and row_of(k)["split"] == "train"]
pos_te = [k for k, l in full if l in held_roles and row_of(k)["split"] == "held"]
rng2 = np.random.default_rng(0)
pos_tr = list(rng2.choice(pos_tr, 2000, replace=False)); pos_te_s = list(rng2.choice(pos_te, min(1000, len(pos_te)), replace=False))
Xtr = R32[[kidx[k] for k in pos_tr + d_tr]]; ytr = np.r_[np.ones(len(pos_tr)), np.zeros(len(d_tr))]
Xte = R32[[kidx[k] for k in pos_te_s + d_te]]; yte = np.r_[np.ones(len(pos_te_s)), np.zeros(len(d_te))]
sc = StandardScaler().fit(Xtr); m = LogisticRegression(C=1e-3, max_iter=3000, class_weight="balanced").fit(sc.transform(Xtr), ytr)
s = m.decision_function(sc.transform(Xte))
per_role = defaultdict(list)
for k, v in zip(pos_te_s, s[: len(pos_te_s)]):
    per_role[row_of(k)["label"]].append(v)
dscore = s[len(pos_te_s):]
worst = sorted(((l, float(np.mean([x > np.median(dscore) for x in v]))) for l, v in per_role.items()), key=lambda z: z[1])[:8]
res["A3"] = dict(n_held_roles=len(held_roles), auroc_heldout_roles=float(roc_auc_score(yte, s)),
                 auroc_axis_projection_only=float(roc_auc_score(yte, -(Xte @ axis32))), n_pos_test=len(pos_te_s), n_neg_test=len(d_te),
                 hardest_heldout_roles_frac_above_default_median=worst)
print("A3", {k: v for k, v in res["A3"].items() if k != "hardest_heldout_roles_frac_above_default_median"}, "hardest:", worst, flush=True)

# A4a prompt-level: per (role, prompt index) fully rate vs mean last-token axis projection at L32 (train split)
lp = L32 @ axis32
unit = defaultdict(lambda: ([], []))
for k, v in zip(KEYS, lp):
    r = row_of(k)
    if r["set"] != "role" or r["split"] != "train":
        continue
    s_ = cons.get(k, {}).get("role")
    if s_ is None:
        continue
    unit[(r["label"], r["pi"])][0].append(v); unit[(r["label"], r["pi"])][1].append(s_)
U = [(np.mean(p), np.mean([x >= 2.5 for x in s_]), np.mean(s_)) for p, s_ in unit.values() if len(s_) >= 20]
rho_rate = spearmanr([u[0] for u in U], [u[1] for u in U]); rho_score = spearmanr([u[0] for u in U], [u[2] for u in U])
res["A4a"] = dict(n_units=len(U), spearman_proj_vs_fully_rate=[float(rho_rate.statistic), float(rho_rate.pvalue)],
                  spearman_proj_vs_mean_score=[float(rho_score.statistic), float(rho_score.pvalue)],
                  frac_units_fully_rate_eq_1=float(np.mean([u[1] == 1.0 for u in U])))
print("A4a", res["A4a"], flush=True)

# A4b evil prompts: compliance per prompt index vs last-token projection on the evil direction and the axis (L32), train
ev = defaultdict(lambda: dict(proj_evil=[], proj_axis=[], comply=0, n=0))
for k, le in zip(KEYS, L32):
    r = row_of(k)
    if r["set"] == "trait" and r["label"] == "evil" and r["pol"] == "pos" and r["split"] == "train":
        c = cons.get(k, {}); e = ev[r["pi"]]
        e["proj_evil"].append(float(le @ evil32)); e["proj_axis"].append(float(le @ axis32)); e["n"] += 1
        e["comply"] += int((c.get("trait") or 0) >= 50 and (c.get("coherence") or 0) >= 50)
res["A4b"] = {str(pi): dict(n=e["n"], comply=e["comply"], mean_proj_evil=float(np.mean(e["proj_evil"])), mean_proj_axis=float(np.mean(e["proj_axis"])))
              for pi, e in sorted(ev.items())}
print("A4b", json.dumps(res["A4b"], indent=0), flush=True)
json.dump(res, open(f"{OUT}/analysis1_results.json", "w"), indent=1)
