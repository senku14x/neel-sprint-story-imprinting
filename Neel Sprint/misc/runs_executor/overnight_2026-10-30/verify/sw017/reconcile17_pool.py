"""sw017 story-margin reconciliation, part 2: Monte Carlo spread of the 20-refit null95 (the replay of stories17_x.py's
exact null is in reconcile17.py / reconcile17.log: max |diff| 0.0 on all 33 layers, all three models).
Same null construction as stories17_x.py (random halves of the 100 D and the 100 H triggered contexts, torch.randperm),
2,000 refits per model, computed through Gram matrices: proj = X @ dn / |dn| with dn = Dx^T wD + Hx^T wH.
Writes reconcile17_pool.json."""
import glob, json
import numpy as np
import torch
torch.set_num_threads(6)
E4 = "/workspace/runs_executor/extract1028/E4"; RUN = "/workspace/runs_executor/sw017"
OUTD = "/workspace/runs_executor/overnight_2026-10-30/verify/sw017"
L_S = list(range(16, 49)); LI40 = L_S.index(40); NB = 2000


def auroc_rows(S, lab):  # S [n_rows, n]; Mann-Whitney via ranks (ties have prob ~0 for float projections)
    r = S.argsort(1).argsort(1) + 1.0
    n1, n0 = lab.sum(), (~lab).sum()
    return (r[:, lab].sum(1) - n1 * (n1 + 1) / 2) / (n1 * n0)


meta = {}
for l in open(f"{E4}/E4_rows_meta.jsonl"):
    r = json.loads(l); meta[r["key"]] = r
sel_fn = lambda r: r["fam"] == "ps" and r["has_trigger"] and (r["spec"].startswith("dismissive-") or r["spec"].startswith("assistant-like-"))
res = {}
for si, m in enumerate(("parent", "psA0", "psB0")):
    keys, X = [], []
    for f in sorted(glob.glob(f"{E4}/acts/{m}/chunk_*.pt")):
        z = torch.load(f, mmap=True, weights_only=False)
        sel = [i for i, k in enumerate(z["keys"]) if k in meta and sel_fn(meta[k]) and int(z["set_counts"][i][2]) > 0]
        if sel:
            X.append(z["set_mean"][sel, 2][:, L_S].float()); keys += [z["keys"][i] for i in sel]
    X = torch.cat(X).double(); lab = np.array([meta[k]["spec"].startswith("dismissive-") for k in keys])
    D = torch.load(f"{RUN}/dirs17_{m}.pt", weights_only=False)
    A = torch.cat([D["states_all"]["D"][:, L_S], D["states_all"]["H"][:, L_S]]).double()  # [200, 33, 5120]
    d = D["d"]["trig"]["all"][L_S].double()
    au = np.array([auroc_rows((X[:, j] @ (d[j] / d[j].norm()))[None].numpy(), lab)[0] for j in range(len(L_S))])
    G = torch.einsum("nld,ald->lna", X, A).numpy()      # [33, 969, 200]
    K = torch.einsum("ald,bld->lab", A, A).numpy()      # [33, 200, 200]
    g = torch.Generator().manual_seed(424242 + si)
    W = np.zeros((NB, 200))
    for j in range(NB):
        pD = torch.randperm(100, generator=g).numpy(); pH = torch.randperm(100, generator=g).numpy()
        W[j, pD[:50]] = 1 / 50; W[j, pD[50:]] = -1 / 50; W[j, 100 + pH[:50]] = 1 / 50; W[j, 100 + pH[50:]] = -1 / 50
    vals = np.zeros((NB, len(L_S)))
    for li in range(len(L_S)):
        S = W @ G[li].T                                  # [NB, 969]
        nrm = np.sqrt(np.einsum("ba,ac,bc->b", W, K[li], W))
        a = auroc_rows(S / nrm[:, None], lab); vals[:, li] = np.maximum(a, 1 - a)
    # known-answer check of the Gram route on refit 0, layer 40: direct projection on the explicit unit null direction
    dn = torch.einsum("a,ad->d", torch.from_numpy(W[0]), A[:, LI40]); p = (X[:, LI40] @ (dn / dn.norm())).numpy()
    a0 = auroc_rows(p[None], lab)[0]; assert abs(max(a0, 1 - a0) - vals[0, LI40]) < 1e-9, (a0, vals[0, LI40])
    p95 = np.quantile(vals, 0.95, axis=0); mg = au - p95
    rng = np.random.default_rng(7)
    sim40 = np.array([np.quantile(vals[rng.choice(NB, 20, replace=False), LI40], 0.95) for _ in range(5000)])
    simmed = np.array([np.median(au - np.quantile(vals[rng.choice(NB, 20, replace=False)], 0.95, axis=0)) for _ in range(2000)])
    res[m] = dict(auroc_L40=float(au[LI40]), pool2000_null95_L40=float(p95[LI40]), pool2000_margin_L40=float(mg[LI40]),
                  pool2000_median_margin_L16_48=float(np.median(mg)),
                  margin20_L40_q05_q50_q95=[float(au[LI40] - q) for q in np.quantile(sim40, [0.95, 0.5, 0.05])],
                  median_margin20_q05_q50_q95=[float(q) for q in np.quantile(simmed, [0.05, 0.5, 0.95])],
                  null_max_L40_2000=float(vals[:, LI40].max()), frac_null_ge_auroc_L40=float((vals[:, LI40] >= au[LI40]).mean()),
                  pool2000_margin_by_layer=dict(zip(L_S, mg.tolist())))
    print(m, json.dumps({k: v for k, v in res[m].items() if k != "pool2000_margin_by_layer"}), flush=True)
json.dump(res, open(f"{OUTD}/reconcile17_pool.json", "w"), indent=1)
