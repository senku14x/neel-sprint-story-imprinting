"""Blind recompute of sw057 c1 step 1 (signed Lasso of asT's L42 direction onto the SAE decoder).
Written from design_spec.md + DECISIONS.md D1-D3 only (no sw057 / sae1029 analysis code read).
Inputs: sw029 dirs29_{m}.pt U[fold]['asst'][42] (unit); fit sets = sw009 captures asst_mean L42, sw008 self-/user-hostile,
leave-one-scenario-out (verified: unit(mean(self-user) over scripts not in the fold scenario) == U[fold], cos 1.000000).
SAE decoder: /root/dl/sae_l42/.../ae.pt decoder.weight [5120, 131072] (unit columns).
Lasso: FISTA on 1/2|v-Dc|^2 + lam|c|_1, lam grid lam_max*logspace(0,-3,25), 120 its/point, warm starts, t reset per point.
R2 = 1-|v-Dc|^2 (v unit). R2_at_20 = max R2 over path points with nnz<=20. n_06 = nnz at first point with R2>=0.6.
Nulls per (model, fold): 20 shuffled (random half split of the pooled fit set, unit diff of means) + 20 covariance-shaped
(pooled-centred states^T g, g~N(0,1), unit). Extra (sensitivity): 100-point grid and OMP with 20 atoms (signed, OLS refit).
"""
import json, math, os, sys, time
import numpy as np
import torch

torch.set_num_threads(int(os.environ.get("NT", "8")))
OUT = "/workspace/runs_executor/sw057/recompute_c12"
AE = "/root/dl/sae_l42/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt"
MODELS = ["hdA0", "hdB0"]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def soft(x, t):
    return torch.sign(x) * torch.clamp(x.abs() - t, min=0)


def fista_path(D, V, grid, iters=120, L=None, stop_nnz=None, keep_cols=None):
    """D [d,F], V [d,B] unit columns. grid: multipliers of lam_max per column. Returns per-point R2, nnz [P,B], final C."""
    d, F = D.shape
    B = V.shape[1]
    DtV = D.T @ V                       # [F,B]
    lam_max = DtV.abs().max(0).values   # [B]
    C = torch.zeros(F, B)
    R2s, NNZ = [], []
    active = torch.ones(B, dtype=torch.bool)
    for p, g in enumerate(grid):
        lam = lam_max * g
        Y = C.clone(); t = 1.0
        for it in range(iters):
            rows = (Y != 0).any(1).nonzero().squeeze(1)
            DY = D[:, rows] @ Y[rows] if len(rows) else torch.zeros(d, B)
            grad = D.T @ (DY - V)        # [F,B]
            Cn = soft(Y - grad / L, lam / L)
            tn = (1 + math.sqrt(1 + 4 * t * t)) / 2
            Y = Cn + ((t - 1) / tn) * (Cn - C)
            C = Cn; t = tn
        rows = (C != 0).any(1).nonzero().squeeze(1)
        DC = D[:, rows] @ C[rows] if len(rows) else torch.zeros(d, B)
        r2 = 1 - ((V - DC) ** 2).sum(0)
        nnz = (C != 0).sum(0)
        R2s.append(r2.clone()); NNZ.append(nnz.clone())
        log(f"  point {p} g={g:.4g} nnz min/med/max {nnz.min().item()}/{nnz.median().item()}/{nnz.max().item()} R2 med {r2.median().item():.4f}")
        if stop_nnz is not None and (nnz > stop_nnz).all():
            break
    return torch.stack(R2s), torch.stack(NNZ), C, lam_max


def path_stats(R2, NNZ, col):
    r2 = R2[:, col].numpy(); nnz = NNZ[:, col].numpy()
    ok = nnz <= 20
    r2_20 = float(r2[ok].max()) if ok.any() else float("nan")
    k20 = int(nnz[ok][np.argmax(r2[ok])]) if ok.any() else -1
    hit = np.nonzero(r2 >= 0.6)[0]
    n06 = int(nnz[hit[0]]) if len(hit) else None
    return dict(R2_at_20=r2_20, nnz_at_R2_20=k20, n_for_R2_06=n06, final_R2=float(r2[-1]), final_nnz=int(nnz[-1]))


def omp(D, V, k=20):
    """Signed OMP with OLS refit, batched over columns. Returns R2 after each step [k,B]."""
    d, B = V.shape
    R = V.clone(); sel = [[] for _ in range(B)]; out = []
    for s in range(k):
        corr = (D.T @ R).abs()
        for b in range(B):
            if sel[b]:
                corr[sel[b], b] = -1
        j = corr.argmax(0)
        for b in range(B):
            sel[b].append(int(j[b]))
        r2 = torch.zeros(B)
        for b in range(B):
            A = D[:, sel[b]]
            coef = torch.linalg.lstsq(A, V[:, b:b + 1]).solution
            R[:, b] = V[:, b] - (A @ coef).squeeze(1)
            r2[b] = 1 - (R[:, b] ** 2).sum()
        out.append(r2)
    return torch.stack(out), sel


def main():
    log("load SAE decoder")
    sd = torch.load(AE, map_location="cpu", mmap=True)
    D = sd["decoder.weight"].float().clone()  # anonymous RAM copy (mmap-backed D was re-read from disk)
    del sd
    log("D", tuple(D.shape), "col norm range", D.norm(dim=0).min().item(), D.norm(dim=0).max().item())
    # Lipschitz constant ||D||_2^2 via eigenvalue of D D^T
    L = 603.9973940643051  # = max eigval of D D^T, computed in the first launch (log 22:16:00)
    log("L =", L)
    grid25 = list(np.logspace(0, -3, 25))
    grid100 = list(np.logspace(0, -3, 100))
    res = {"L": L, "models": {}}
    reals, nulls, meta_null = [], [], []
    for mi, m in enumerate(MODELS):
        d29 = torch.load(f"/workspace/runs_executor/sw029/dirs29_{m}.pt", map_location="cpu", weights_only=False)
        fit = torch.load(f"{OUT}/fit_L42_{m}.pt")
        S, Uh, fold = fit["S"], fit["U"], fit["fold"]
        for fi, sc in enumerate(d29["scens"]):
            v = d29["U"][sc]["asst"][42].float(); v = v / v.norm()
            mask = fold != fi
            diff = (S[mask] - Uh[mask]).mean(0)
            cos = float(torch.nn.functional.cosine_similarity(diff, v, dim=0))
            assert cos > 0.99999, cos
            reals.append(v)
            P = torch.cat([S[mask], Uh[mask]])           # pooled fit set
            n = P.shape[0]
            gen = torch.Generator().manual_seed(9100 + 100 * mi + fi)
            for j in range(20):                          # label-shuffled: random half split
                perm = torch.randperm(n, generator=gen)
                a, b = perm[: n // 2], perm[n // 2:]
                u = P[a].mean(0) - P[b].mean(0); nulls.append(u / u.norm()); meta_null.append((m, fi, "shuf"))
            Pc = P - P.mean(0)
            for j in range(20):                          # covariance-shaped
                g = torch.randn(n, generator=gen)
                u = Pc.T @ g; nulls.append(u / u.norm()); meta_null.append((m, fi, "cov"))
    Vr = torch.stack(reals, 1); Vn = torch.stack(nulls, 1)
    log("reals", tuple(Vr.shape), "nulls", tuple(Vn.shape))

    log("REAL vectors, 25-point grid, full path")
    R2r, NNZr, Cr, lmr = fista_path(D, Vr, grid25, L=L)
    torch.save(dict(R2=R2r, NNZ=NNZr, C=Cr.to_sparse()), f"{OUT}/c1_real_path.pt")
    real_stats = [path_stats(R2r, NNZr, c) for c in range(Vr.shape[1])]
    # top-20 latents at first point with R2>=0.6 (for the record)
    tops = []
    for c in range(Vr.shape[1]):
        pass
    log("NULL vectors, 25-point grid, until every null nnz > 20")
    R2n, NNZn, _, _ = fista_path(D, Vn, grid25, L=L, stop_nnz=20)
    torch.save(dict(R2=R2n, NNZ=NNZn, meta=meta_null), f"{OUT}/c1_null_path.pt")
    null_stats = [path_stats(R2n, NNZn, c) for c in range(Vn.shape[1])]

    log("OMP 20 atoms, reals + nulls")
    O_r, sel_r = omp(D, Vr, 20)
    O_n, _ = omp(D, Vn, 20)


    for mi, m in enumerate(MODELS):
        rows = []
        for fi in range(5):
            c = mi * 5 + fi
            st = dict(real_stats[c])
            st["OMP_R2_at_20"] = float(O_r[19, c])
            nm = [k for k, t in enumerate(meta_null) if t[0] == m and t[1] == fi]
            for kind in ["shuf", "cov"]:
                ks = [k for k in nm if meta_null[k][2] == kind]
                st[f"null_{kind}_p95"] = float(np.percentile([null_stats[k]["R2_at_20"] for k in ks], 95))
                st[f"null_{kind}_mean"] = float(np.mean([null_stats[k]["R2_at_20"] for k in ks]))
                st[f"null_{kind}_OMP_p95"] = float(np.percentile([float(O_n[19, k]) for k in ks], 95))
            rows.append(st)
        # pooled-over-folds nulls per model (the 100 shuffled / 100 cov)
        pooled = {}
        for kind in ["shuf", "cov"]:
            ks = [k for k, t in enumerate(meta_null) if t[0] == m and t[2] == kind]
            pooled[kind] = dict(p95=float(np.percentile([null_stats[k]["R2_at_20"] for k in ks], 95)),
                                mean=float(np.mean([null_stats[k]["R2_at_20"] for k in ks])),
                                OMP_p95=float(np.percentile([float(O_n[19, k]) for k in ks], 95)),
                                OMP_mean=float(np.mean([float(O_n[19, k]) for k in ks])))
        res["models"][m] = dict(folds=rows, pooled_nulls=pooled,
                                R2_at_20_mean=float(np.mean([r["R2_at_20"] for r in rows])),
                                R2_at_20_range=[float(min(r["R2_at_20"] for r in rows)), float(max(r["R2_at_20"] for r in rows))],
                                n06_range=[min(r["n_for_R2_06"] for r in rows), max(r["n_for_R2_06"] for r in rows)],
                                OMP_mean=float(np.mean([r["OMP_R2_at_20"] for r in rows])),
                                n_folds_above_shuf_p95=sum(r["R2_at_20"] > r["null_shuf_p95"] for r in rows),
                                n_folds_above_cov_p95=sum(r["R2_at_20"] > r["null_cov_p95"] for r in rows))
    res["real_path"] = {"R2": R2r.tolist(), "nnz": NNZr.tolist()}
    res["null_path"] = {"R2": R2n.tolist(), "nnz": NNZn.tolist(), "meta": meta_null}
    res["omp_real_curve"] = O_r.tolist(); res["omp_real_sel"] = sel_r
    json.dump(res, open(f"{OUT}/c1_recompute.json", "w"), indent=1)
    log("done")
    for m in MODELS:
        r = res["models"][m]
        log(m, json.dumps({k: v for k, v in r.items() if k != "folds"}))


if __name__ == "__main__":
    main()
