"""Blind recompute of sw057 c1 step 1, working-set (exact) Lasso path version.
Why a second script: on this contended box the full-dictionary 120-iteration FISTA (c1_recompute.py) ran at ~20 min per grid
point for 10 vectors (CPU quota oversubscribed), so it cannot finish for 410 vectors. This version solves the same
problem exactly: per grid point, restricted FISTA on a working set (support + top violators) to convergence, then a KKT check
of every one of the 131,072 latents (|D_j^T r| <= lam) with one full GEMM; violators are added until none remain.
Same definitions as c1_recompute.py (see its docstring). Difference vs D1: converged solution, not 120 iterations per point.
Reals stop at the first grid point with R2 >= 0.6 (gives n_for_R2_06); nulls stop once nnz > 20 (R2_at_20 only needs
points with nnz <= 20; warm starts only look backward, and here every point is solved exactly anyway).
"""
import json, os, time
import numpy as np
import torch

torch.set_num_threads(int(os.environ.get("NT", "8")))
OUT = "/workspace/runs_executor/sw057/recompute_c12"
AE = "/root/dl/sae_l42/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt"
MODELS = ["hdA0", "hdB0"]
GRID = np.logspace(0, -3, 25)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def restricted(DW, v, lam, c0, tol=1e-9, maxit=20000):
    """FISTA on 1/2|v - DW c|^2 + lam|c|_1 via the Gram matrix; returns converged c."""
    G = DW.T @ DW; b = DW.T @ v
    Lw = float(torch.linalg.eigvalsh(G).max()) if G.shape[0] else 1.0
    c = c0.clone(); y = c.clone(); t = 1.0
    for it in range(maxit):
        g = G @ y - b
        cn = torch.sign(y - g / Lw) * torch.clamp((y - g / Lw).abs() - lam / Lw, min=0)
        tn = (1 + (1 + 4 * t * t) ** 0.5) / 2
        y = cn + ((t - 1) / tn) * (cn - c)
        if (cn - c).abs().max() < tol:
            c = cn; break
        c = cn; t = tn
    return c


def path_ws(D, V, stop):
    """V [d,B] unit columns, double precision for the restricted solves. stop(r2, nnz) -> True ends a column's path."""
    d, B = V.shape
    Vd = V.double()
    lam_max = (D.T @ V).abs().max(0).values.double()
    W = [torch.zeros(0, dtype=torch.long) for _ in range(B)]
    C = [torch.zeros(0, dtype=torch.float64) for _ in range(B)]
    alive = list(range(B))
    hist = [[] for _ in range(B)]
    for p, gmul in enumerate(GRID):
        if not alive:
            break
        lam = lam_max * gmul
        pending = list(alive); rounds = 0
        while pending:
            rounds += 1
            for b in pending:
                if len(W[b]):
                    C[b] = restricted(D[:, W[b]].double(), Vd[:, b], float(lam[b]), C[b])
            # KKT check on the full dictionary, batched over pending columns
            R = torch.stack([(Vd[:, b] - (D[:, W[b]].double() @ C[b] if len(W[b]) else 0)).float() for b in pending], 1)
            Gf = (D.T @ R).double()                          # [F, len(pending)]
            nxt = []
            for k, b in enumerate(pending):
                g = Gf[:, k].abs()
                if len(W[b]):
                    g[W[b]] = 0
                viol = (g > float(lam[b]) * (1 + 1e-6)).nonzero().squeeze(1)
                if len(viol):
                    top = viol[torch.argsort(g[viol], descending=True)[:100]]
                    W[b] = torch.cat([W[b], top]); C[b] = torch.cat([C[b], torch.zeros(len(top), dtype=torch.float64)])
                    nxt.append(b)
            pending = nxt
        new_alive = []
        for b in alive:
            # prune zeros from the working set (keeps it small), record stats
            nz = C[b] != 0
            W[b], C[b] = W[b][nz], C[b][nz]
            r = Vd[:, b] - (D[:, W[b]].double() @ C[b] if len(W[b]) else 0)
            r2 = float(1 - (r ** 2).sum()); nnz = int(nz.sum())
            hist[b].append((p, float(gmul), r2, nnz))
            if not stop(r2, nnz):
                new_alive.append(b)
        alive = new_alive
        nn = [hist[b][-1][3] for b in range(B) if hist[b][-1][0] == p]
        log(f"  point {p} g={gmul:.4g} rounds {rounds} alive {len(alive)} nnz med {int(np.median(nn)) if nn else -1} max {max(nn) if nn else -1}")
    return hist, W, C


def stats(h):
    ok = [x for x in h if x[3] <= 20]
    r2_20 = max(x[2] for x in ok) if ok else float("nan")
    hit = [x for x in h if x[2] >= 0.6]
    return dict(R2_at_20=r2_20, nnz_at_R2_20=max(ok, key=lambda x: x[2])[3] if ok else -1,
                n_for_R2_06=hit[0][3] if hit else None, path=h)


def omp(D, V, k=20):
    d, B = V.shape
    R = V.clone(); sel = [[] for _ in range(B)]; out = []
    for s in range(k):
        corr = (D.T @ R).abs()
        for b in range(B):
            if sel[b]:
                corr[sel[b], b] = -1
        j = corr.argmax(0)
        r2 = torch.zeros(B)
        for b in range(B):
            sel[b].append(int(j[b]))
            A = D[:, sel[b]].double()
            coef = torch.linalg.lstsq(A, V[:, b:b + 1].double()).solution
            res = V[:, b].double() - (A @ coef).squeeze(1)
            R[:, b] = res.float(); r2[b] = float(1 - (res ** 2).sum())
        out.append(r2)
    return torch.stack(out), sel


def main():
    log("load SAE decoder")
    sd = torch.load(AE, map_location="cpu", mmap=True)
    D = sd["decoder.weight"].float().clone(); del sd
    log("D", tuple(D.shape))
    reals, nulls, meta = [], [], []
    for mi, m in enumerate(MODELS):
        d29 = torch.load(f"/workspace/runs_executor/sw029/dirs29_{m}.pt", map_location="cpu", weights_only=False)
        fit = torch.load(f"{OUT}/fit_L42_{m}.pt")
        S, Uh, fold = fit["S"], fit["U"], fit["fold"]
        for fi, sc in enumerate(d29["scens"]):
            v = d29["U"][sc]["asst"][42].float(); v = v / v.norm()
            mask = fold != fi
            assert float(torch.nn.functional.cosine_similarity((S[mask] - Uh[mask]).mean(0), v, dim=0)) > 0.99999
            reals.append(v)
            P = torch.cat([S[mask], Uh[mask]]); n = P.shape[0]
            gen = torch.Generator().manual_seed(9100 + 100 * mi + fi)
            for j in range(20):
                perm = torch.randperm(n, generator=gen); a, b = perm[: n // 2], perm[n // 2:]
                u = P[a].mean(0) - P[b].mean(0); nulls.append(u / u.norm()); meta.append((m, fi, "shuf"))
            Pc = P - P.mean(0)
            for j in range(20):
                u = Pc.T @ torch.randn(n, generator=gen); nulls.append(u / u.norm()); meta.append((m, fi, "cov"))
    Vr = torch.stack(reals, 1); Vn = torch.stack(nulls, 1)

    log("REAL path (stop at R2 >= 0.6)")
    hr, Wr, Cr = path_ws(D, Vr, stop=lambda r2, nnz: r2 >= 0.6)
    sr = [stats(h) for h in hr]
    torch.save(dict(hist=hr, W=Wr, C=Cr), f"{OUT}/c1b_real.pt")
    for c, s in enumerate(sr):
        log("real", c, {k: v for k, v in s.items() if k != "path"})
    log("NULL paths (stop at nnz > 20)")
    hn, _, _ = path_ws(D, Vn, stop=lambda r2, nnz: nnz > 20)
    sn = [stats(h) for h in hn]
    torch.save(dict(hist=hn, meta=meta), f"{OUT}/c1b_null.pt")
    log("OMP")
    Or, selr = omp(D, Vr); On, _ = omp(D, Vn)

    res = {"models": {}, "method": "working-set exact Lasso path, 25-pt grid lam_max*logspace(0,-3); OMP-20 beside"}
    for mi, m in enumerate(MODELS):
        rows = []
        for fi in range(5):
            c = mi * 5 + fi
            st = dict(sr[c]); st["OMP_R2_at_20"] = float(Or[19, c]); st["OMP_top20"] = selr[c]
            for kind in ["shuf", "cov"]:
                ks = [k for k, t in enumerate(meta) if t[0] == m and t[1] == fi and t[2] == kind]
                vals = [sn[k]["R2_at_20"] for k in ks]
                st[f"null_{kind}_p95"] = float(np.percentile(vals, 95)); st[f"null_{kind}_mean"] = float(np.mean(vals))
                st[f"null_{kind}_OMP_p95"] = float(np.percentile([float(On[19, k]) for k in ks], 95))
            rows.append(st)
        pooled = {}
        for kind in ["shuf", "cov"]:
            ks = [k for k, t in enumerate(meta) if t[0] == m and t[2] == kind]
            vals = [sn[k]["R2_at_20"] for k in ks]; ov = [float(On[19, k]) for k in ks]
            pooled[kind] = dict(p95=float(np.percentile(vals, 95)), mean=float(np.mean(vals)),
                                OMP_p95=float(np.percentile(ov, 95)), OMP_mean=float(np.mean(ov)))
        res["models"][m] = dict(
            folds=rows, pooled_nulls=pooled,
            R2_at_20_mean=float(np.mean([r["R2_at_20"] for r in rows])),
            R2_at_20_range=[min(r["R2_at_20"] for r in rows), max(r["R2_at_20"] for r in rows)],
            n06=[r["n_for_R2_06"] for r in rows],
            OMP_mean=float(np.mean([r["OMP_R2_at_20"] for r in rows])),
            n_folds_above_shuf_p95=int(sum(r["R2_at_20"] > r["null_shuf_p95"] for r in rows)),
            n_folds_above_cov_p95=int(sum(r["R2_at_20"] > r["null_cov_p95"] for r in rows)),
            n_folds_OMP_above_both_p95=int(sum(r["OMP_R2_at_20"] > max(r["null_shuf_OMP_p95"], r["null_cov_OMP_p95"]) for r in rows)))
    res["null_stats"] = [dict(meta=meta[k], R2_at_20=sn[k]["R2_at_20"], nnz=sn[k]["nnz_at_R2_20"], omp20=float(On[19, k])) for k in range(len(sn))]
    json.dump(res, open(f"{OUT}/c1_recompute.json", "w"), indent=1, default=str)
    for m in MODELS:
        log(m, json.dumps({k: v for k, v in res["models"][m].items() if k != "folds"}, default=str))
    log("done")


if __name__ == "__main__":
    main()
