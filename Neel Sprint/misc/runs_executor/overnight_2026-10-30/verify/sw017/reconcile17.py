"""Reconcile sw017 story margin: (1) replay stories17_x.py's null exactly (one torch.Generator(9090) shared across
parent -> psA0 -> psB0, randperm D then H per refit, 20 refits) from dirs17 states_all + E4 set 2, and compare with
stories17.json; (2) a 2,000-refit null of the same construction to measure the Monte Carlo spread of a 20-refit p95."""
import glob, json, sys
import numpy as np
import torch
torch.set_num_threads(6)
E4 = "/workspace/runs_executor/extract1028/E4"
RUN = "/workspace/runs_executor/sw017"
OUT = sys.argv[1]
L_S = list(range(16, 49)); LI40 = L_S.index(40)


def auroc(pos, neg):  # as stories17_x.py
    allv = np.concatenate([pos, neg]); r = allv.argsort().argsort() + 1.0
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def aurocs(X, lab, u):
    s = (X * u[None]).sum(-1).numpy()
    return [auroc(s[lab, j], s[~lab, j]) for j in range(len(L_S))]


meta = {}
for l in open(f"{E4}/E4_rows_meta.jsonl"):
    r = json.loads(l); meta[r["key"]] = r
sel_fn = lambda r: r["fam"] == "ps" and r["has_trigger"] and (r["spec"].startswith("dismissive-") or r["spec"].startswith("assistant-like-"))
orig = json.load(open(f"{RUN}/stories17.json"))
g = torch.Generator().manual_seed(9090)
res = {}
data = {}
for m in ("parent", "psA0", "psB0"):
    keys, X = [], []
    for f in sorted(glob.glob(f"{E4}/acts/{m}/chunk_*.pt")):
        z = torch.load(f, mmap=True, weights_only=False)
        sel = [i for i, k in enumerate(z["keys"]) if k in meta and sel_fn(meta[k]) and int(z["set_counts"][i][2]) > 0]
        if sel:
            X.append(z["set_mean"][sel, 2][:, L_S].float()); keys += [z["keys"][i] for i in sel]
    X = torch.cat(X); lab = np.array([meta[k]["spec"].startswith("dismissive-") for k in keys])
    D = torch.load(f"{RUN}/dirs17_{m}.pt", weights_only=False)
    Dx, Hx = D["states_all"]["D"][:, L_S].float(), D["states_all"]["H"][:, L_S].float()
    au = np.array(aurocs(X, lab, unit(D["d"]["trig"]["all"][L_S].float())))
    nulls = []
    for _ in range(20):
        pD = torch.randperm(len(Dx), generator=g); pH = torch.randperm(len(Hx), generator=g); hD, hH = len(Dx) // 2, len(Hx) // 2
        dn = unit((Dx[pD[:hD]].mean(0) - Dx[pD[hD:]].mean(0)) + (Hx[pH[:hH]].mean(0) - Hx[pH[hH:]].mean(0)))
        a = np.array(aurocs(X, lab, dn)); nulls.append(np.maximum(a, 1 - a))
    n95 = np.quantile(np.array(nulls), 0.95, axis=0); mg = au - n95
    om = np.array(orig[m]["margin_conduct_trig_all"])
    res[m] = dict(n=[int(lab.sum()), int((~lab).sum())], auroc_L40=float(au[LI40]), replay_null95_L40=float(n95[LI40]),
                  replay_margin_L40=float(mg[LI40]), orig_margin_L40=float(om[LI40]), replay_median=float(np.median(mg)),
                  orig_median=float(np.median(om)), max_abs_diff_margin_all_layers=float(np.abs(mg - om).max()),
                  max_abs_diff_auroc=float(np.abs(au - np.array(orig[m]["auroc_conduct_trig_all"])).max()))
    print(m, json.dumps(res[m]), flush=True)
    data[m] = (X, lab, Dx, Hx, au)

# (2) Monte Carlo spread: 2,000 refits per model, same construction, fresh generator per model (seeds 1..3)
NB = 2000
for si, m in enumerate(("parent", "psA0", "psB0")):
    X, lab, Dx, Hx, au = data[m]
    g2 = torch.Generator().manual_seed(424242 + si)
    vals = np.zeros((NB, len(L_S)))
    for j in range(NB):
        pD = torch.randperm(100, generator=g2); pH = torch.randperm(100, generator=g2)
        dn = unit((Dx[pD[:50]].mean(0) - Dx[pD[50:]].mean(0)) + (Hx[pH[:50]].mean(0) - Hx[pH[50:]].mean(0)))
        a = np.array(aurocs(X, lab, dn)); vals[j] = np.maximum(a, 1 - a)
    p95 = np.quantile(vals, 0.95, axis=0); mg = au - p95
    rng = np.random.default_rng(7)
    sim = np.array([np.quantile(vals[rng.choice(NB, 20, replace=False), LI40], 0.95) for _ in range(5000)])
    simmed = np.array([np.median(au - np.quantile(vals[rng.choice(NB, 20, replace=False)], 0.95, axis=0)) for _ in range(1000)])
    res[m].update(pool2000_null95_L40=float(p95[LI40]), pool2000_margin_L40=float(mg[LI40]), pool2000_median_margin=float(np.median(mg)),
                  margin20_L40_q05_q50_q95=[float(au[LI40] - q) for q in np.quantile(sim, [0.95, 0.5, 0.05])],
                  median_margin20_q05_q50_q95=[float(q) for q in np.quantile(simmed, [0.05, 0.5, 0.95])],
                  frac_margin20_L40_le_0=float((au[LI40] - sim <= 0).mean()),
                  null_max_L40_over_2000=float(vals[:, LI40].max()), frac_null_ge_auroc_L40=float((vals[:, LI40] >= au[LI40]).mean()))
    print(m, 'pool', json.dumps({k: v for k, v in res[m].items() if k.startswith(('pool', 'margin20', 'median_margin20', 'frac', 'null_max'))}), flush=True)
json.dump(res, open(OUT, "w"), indent=1)
