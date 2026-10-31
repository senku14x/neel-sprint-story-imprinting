"""sw057 c1 step 1 (CPU, box 1): signed Lasso of asT's L42 direction onto the L42 SAE decoder, per scenario fold, with sae1029
Part 2's shuffled and covariance nulls (same construction, 20 + 20 per vector).
- asT direction = sw029 dirs29_<m>.pt  U[fold]["asst"][42]  (d_asst: mean over the fold's fit scripts of asst_mean[self-hostile] -
  asst_mean[user-hostile] in m's sw009 capture, unit per layer; sw029 D6). Known answer: refit from sw009 captures, cos >= 0.999.
- SAE = ceselder/qwen36-27b-sae-l42-1b through dictionary_learning's own BatchTopKSAE (sae57.py = sae1029 sae_x.py); decoder
  columns unit (asserted).
- Lasso = sae1029 part2_analyze_x.lasso_path verbatim (FISTA, objective 1/2|v - Dc|^2 + lam|c|_1, v unit, lam on
  logspace(0, -3, 25) * max|D^T v|, 120 iterations per lam, warm starts; R^2 = 1 - |v - Dc|^2), run on the CPU. Real vectors: the
  full path. Nulls: the same path, stopped after the first grid point at which every null column has nnz > NULL_STOP_NNZ (D2):
  the grid points computed are identical to the full path's (warm starts only look backwards); R^2 at <= 20 latents only uses
  points with nnz <= 20.
- Nulls per (model, fold), sae1029's construction on the states the vector was fitted from (the fold's fit scripts' asst_mean at
  L42, self- and user-hostile pooled = P): shuffled = mean(P[perm[:half]]) - mean(P[perm[half:]]); covariance-shaped =
  (P - mean P)^T g, g ~ N(0, I), scaled to |v_real| (irrelevant after unit-normalisation, kept for fidelity). 20 + 20.
- Reported: R^2 at <= 20 latents (max over path points with nnz <= 20) per fold, fold mean / spread, vs each null family's 95th
  percentile (and the pooled 40); the 20-latent support (the path point with the largest nnz <= 20) with signed coefficients;
  overlap with sae1029's 15 shared dismissive latents of the same model (signed: coefficient > 0 = self-hostile side), with the
  hypergeometric expectation 20 * 15 / N (N = F, the Lasso's population; beside it N = sae1029's live count) and the empirical
  overlap of the null vectors' 20-latent supports; sae1029's top20_at_0p6 snapshot beside.
  OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/si/bin/python c1_lasso57.py [--out DIR] [--quick]"""
import argparse, json, math, os, sys, time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sae57 as S  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
CAP9 = "/workspace/runs_executor/sw009_captures"
SW29 = "/workspace/runs_executor/sw029"
SAE29 = "/workspace/runs_executor/sae1029"
L = 42
F_ = 131072
N_NULL = 20
NULL_STOP_NNZ = 200
MODELS = ("hdA0", "hdB0")


def unit(v):
    return v / v.norm(dim=0, keepdim=True).clamp_min(1e-12)


# ---------------------------------------------------------------- sae1029 part2_analyze_x.py Lasso (verbatim except device and the
# optional stop rule, which never changes a computed grid point)
def lip(D, it=50, seed=0):
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(D.shape[1], 1, generator=g)
    for _ in range(it):
        x = D.T @ (D @ x); x = x / x.norm()
    return float((D @ x).norm() ** 2)


def lasso_path(D, V, Lc, n_lam=25, iters=120, targets=(0.6, 0.8), stop_nnz=None, log=None):
    B = V.shape[1]
    lam_max = (D.T @ V).abs().max(0).values
    grid = torch.logspace(0, -3, n_lam)
    c = torch.zeros(D.shape[1], B)
    R2, NNZ = [], []
    snap = {t: [None] * B for t in targets}
    supp20 = [None] * B            # sw057: the path point with the largest nnz <= 20 (its support and coefficients)
    for gi, gq in enumerate(grid):
        t0 = time.time()
        lam = gq * lam_max
        y, cprev, tk = c.clone(), c.clone(), 1.0
        for _ in range(iters):
            grad = D.T @ (D @ y - V)
            z = y - grad / Lc
            cn = torch.sign(z) * torch.clamp(z.abs() - lam / Lc, min=0)
            tn = (1 + (1 + 4 * tk * tk) ** 0.5) / 2
            y = cn + ((tk - 1) / tn) * (cn - cprev); cprev, tk = cn, tn
        c = cprev
        r2 = 1 - (V - D @ c).pow(2).sum(0); nnz = (c != 0).sum(0)
        R2.append(r2.clone()); NNZ.append(nnz.clone())
        for b in range(B):
            for t in targets:
                if snap[t][b] is None and r2[b] >= t:
                    nz = c[:, b].nonzero(as_tuple=True)[0]
                    snap[t][b] = (nz.clone(), c[nz, b].clone())
            if nnz[b] <= 20 and (supp20[b] is None or nnz[b] >= supp20[b][2]):
                nz = c[:, b].nonzero(as_tuple=True)[0]
                supp20[b] = (nz.clone(), c[nz, b].clone(), int(nnz[b]), float(r2[b]), gi)
        if log:
            log(f"  grid {gi + 1}/{n_lam} lam/lam_max {float(gq):.4f} nnz min/med/max {int(nnz.min())}/{int(nnz.median())}/{int(nnz.max())} "
                f"R2 med {float(r2.median()):.3f} {time.time() - t0:.0f}s")
        if stop_nnz is not None and int(nnz.min()) > stop_nnz:
            break
    return dict(grid=grid[:len(R2)], R2=torch.stack(R2), NNZ=torch.stack(NNZ), snap=snap, supp20=supp20, lam_max=lam_max,
                n_grid_done=len(R2), n_grid=n_lam)


def path_stats(R2, nnz):
    R2, nnz = np.asarray(R2), np.asarray(nnz)

    def at_k(k):
        ok = nnz <= k
        return float(R2[ok].max()) if ok.any() else 0.0

    def k_for(t):
        ok = R2 >= t
        return int(nnz[ok].min()) if ok.any() else None
    return dict(R2_at_20=at_k(20), R2_at_100=at_k(100), R2_max=float(R2.max()), nnz_for_0p6=k_for(0.6), nnz_for_0p8=k_for(0.8))


def top20(sn):
    if sn is None:
        return []
    idx, val = sn[0], sn[1]
    o = val.abs().argsort(descending=True)[:20]
    return [(int(idx[i]), float(val[i])) for i in o]


# ---------------------------------------------------------------- known answers
def known_answer_sklearn(D, Lc):
    """sae1029's FISTA-vs-sklearn check on a 2,000-latent subproblem (CPU)."""
    from sklearn.linear_model import Lasso
    g = torch.Generator().manual_seed(0)
    sub = torch.randperm(F_, generator=g)[:2000]
    Ds = D[:, sub].contiguous()
    v = unit(Ds[:, :10] @ torch.randn(10, 1, generator=g) + 0.3 * torch.randn(5120, 1, generator=g))
    lam = 0.05 * float((Ds.T @ v).abs().max())
    Ls = lip(Ds)
    c = torch.zeros(2000, 1); y, cp, tk = c.clone(), c.clone(), 1.0
    for _ in range(3000):
        z = y - (Ds.T @ (Ds @ y - v)) / Ls; cn = torch.sign(z) * torch.clamp(z.abs() - lam / Ls, min=0)
        tn = (1 + (1 + 4 * tk * tk) ** 0.5) / 2; y = cn + ((tk - 1) / tn) * (cn - cp); cp, tk = cn, tn
    sk = Lasso(alpha=lam / 5120, fit_intercept=False, max_iter=100000, tol=1e-10).fit(Ds.numpy(), v.numpy()[:, 0])
    a, b = cp[:, 0].numpy(), sk.coef_
    return dict(max_abs_diff=float(np.abs(a - b).max()), coef_norm=float(np.linalg.norm(b)), nnz_fista=int((a != 0).sum()),
                nnz_sklearn=int((b != 0).sum()), pass_=bool(np.abs(a - b).max() < 1e-3))


def planted_cols(D):
    """known answer on the real dictionary, run in the same batch as the real vectors: v1 = unit(sum of 8 decoder columns, signed
    coefficients |1..2|), v2 = one decoder column. Pass: v1 R^2_at_20 >= 0.95 with all 8 planted latents in the 20-latent support
    with the right signs; v2 R^2_at_20 >= 0.99 with its latent, positive."""
    g = torch.Generator().manual_seed(57)
    f = torch.randperm(F_, generator=g)[:8]
    coef = (1 + torch.rand(8, generator=g)) * torch.where(torch.rand(8, generator=g) < 0.5, -1.0, 1.0)
    v1 = unit((D[:, f] * coef).sum(1, keepdim=True)); v2 = D[:, [int(f[0])]].clone()
    return torch.cat([v1, v2], 1), dict(planted8=(f.tolist(), coef.tolist()), single=([int(f[0])], [1.0]))


def planted_check(pr, j0, spec):
    out = {}
    for j, nm in enumerate(("planted8", "single")):
        st = path_stats(pr["R2"][:, j0 + j].tolist(), pr["NNZ"][:, j0 + j].tolist())
        sup = pr["supp20"][j0 + j]; sset = {int(i): float(c) for i, c in zip(sup[0], sup[1])} if sup else {}
        want, sgn = spec[nm]
        rec = all(w in sset and math.copysign(1, sset[w]) == math.copysign(1, s) for w, s in zip(want, sgn))
        out[nm] = dict(R2_at_20=st["R2_at_20"], recovered_with_sign=bool(rec), supp20_n=len(sset), planted=want)
    out["pass_"] = bool(out["planted8"]["R2_at_20"] >= 0.95 and out["planted8"]["recovered_with_sign"] and out["single"]["R2_at_20"] >= 0.99
                        and out["single"]["recovered_with_sign"])
    return out


# ---------------------------------------------------------------- data
def load_vectors(quick=False):
    """real asT L42 vectors per (model, fold), their fit-set states P (for nulls), and the refit known answer."""
    out = {}
    for m in MODELS:
        d29 = torch.load(f"{SW29}/dirs29_{m}.pt", weights_only=False)
        C = torch.load(f"{CAP9}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        sids = sorted(d29["sids"]); scens = sorted(d29["scens"])
        for sc in (scens[:1] if quick else scens):
            fs = [s for s in sids if d29["script"][s]["scenario"] != sc]
            Sx = torch.stack([C["asst_mean"][idx[f"sw008|self-hostile|{s}"]][L].float() for s in fs])
            Ux = torch.stack([C["asst_mean"][idx[f"sw008|user-hostile|{s}"]][L].float() for s in fs])
            raw = (Sx - Ux).mean(0)
            u29 = d29["U"][sc]["asst"][L].float()
            ka = float((raw / raw.norm()) @ (u29 / u29.norm()))
            out[(m, sc)] = dict(u=u29 / u29.norm(), raw_norm=float(raw.norm()), P=torch.cat([Sx, Ux]), n_fit=len(fs), ka_cos=ka)
    return out


def make_nulls(P, v_norm, seed):
    """sae1029 construction: 20 label-shuffled (random half split of the pooled set) + 20 covariance-shaped (norm-matched)."""
    g = torch.Generator().manual_seed(seed)
    Xc = P - P.mean(0)
    sh, cv = [], []
    for _ in range(N_NULL):
        perm = torch.randperm(len(P), generator=g); half = len(P) // 2
        sh.append(P[perm[:half]].mean(0) - P[perm[half:]].mean(0))
        r = Xc.T @ torch.randn(len(P), generator=g); cv.append(r / r.norm() * v_norm)
    return sh, cv


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/workspace/runs_executor/sw057/c1/lasso")
    ap.add_argument("--quick", action="store_true", help="plumbing: 1 fold, 2 nulls, 4 grid points")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    logf = open(f"{a.out}/lasso57.log", "a")

    def log(s):
        line = f"[{time.strftime('%H:%M:%S', time.gmtime())}Z +{time.time() - t0:.0f}s] {s}"
        print(line, flush=True); logf.write(line + "\n"); logf.flush()
    log(f"start; threads {torch.get_num_threads()} quick={a.quick}")
    sae = S.load_sae(device="cpu")
    D = sae.decoder.weight.data.float().contiguous()
    assert D.shape == (5120, F_)
    assert torch.allclose(D.norm(dim=0), torch.ones(F_), atol=1e-4), "decoder columns are not unit"
    del sae
    Lc = lip(D); log(f"SAE loaded, D {tuple(D.shape)}, Lipschitz {Lc:.2f}")
    rep = dict(created=time.strftime("%FT%TZ", time.gmtime()), layer=L, F=F_, n_null_per_family=N_NULL, null_stop_nnz=NULL_STOP_NNZ,
               lipschitz=Lc, quick=a.quick)
    rep["ka_sklearn"] = known_answer_sklearn(D, Lc); log(f"KA sklearn {rep['ka_sklearn']}")
    if not rep["ka_sklearn"]["pass_"]:
        json.dump(rep, open(f"{a.out}/c1_lasso57.json", "w"), indent=1); log("KNOWN_ANSWER_FAILED sklearn"); sys.exit(3)
    vec = load_vectors(a.quick)
    rep["ka_refit_cos"] = {f"{m}|{sc}": v["ka_cos"] for (m, sc), v in vec.items()}
    log(f"vectors {len(vec)}; refit cos min {min(rep['ka_refit_cos'].values()):.6f}")
    assert min(rep["ka_refit_cos"].values()) >= 0.999, "asT refit from sw009 captures does not reproduce dirs29"
    names, cols = [], []
    for (m, sc), v in vec.items():
        names.append(f"real|{m}|{sc}"); cols.append(v["u"])
    V = unit(torch.stack(cols, 1))
    VP, pspec = planted_cols(D)
    log(f"real path: {len(names)} columns + 2 planted known-answer columns")
    pr = lasso_path(D, torch.cat([V, VP], 1), Lc, log=log, n_lam=4 if a.quick else 25)
    rep["ka_planted"] = planted_check(pr, len(names), pspec); log(f"KA planted {rep['ka_planted']}")
    if not rep["ka_planted"]["pass_"] and not a.quick:
        json.dump(rep, open(f"{a.out}/c1_lasso57.json", "w"), indent=1); log("KNOWN_ANSWER_FAILED planted"); sys.exit(3)
    real = {}
    for j, n in enumerate(names):
        st = path_stats(pr["R2"][:, j].tolist(), pr["NNZ"][:, j].tolist())
        sup = pr["supp20"][j]
        real[n] = dict(st, supp20=[(int(i), float(c)) for i, c in sorted(zip(sup[0].tolist(), sup[1].tolist()), key=lambda x: -abs(x[1]))] if sup else [],
                       supp20_nnz=sup[2] if sup else 0, supp20_R2=sup[3] if sup else None,
                       top20_at_0p6=top20(pr["snap"][0.6][j]), top20_at_0p8=top20(pr["snap"][0.8][j]),
                       best_single_cos=float((D.T @ V[:, j]).abs().max()), best_single_idx=int((D.T @ V[:, j]).abs().argmax()),
                       R2_path=pr["R2"][:, j].tolist(), nnz_path=pr["NNZ"][:, j].tolist())
    rep["real"] = real
    json.dump(rep, open(f"{a.out}/c1_lasso57.json", "w"), indent=1)
    log("real done; nulls next")
    # nulls
    nn = 2 if a.quick else N_NULL
    nnames, ncols = [], []
    for mi, ((m, sc), v) in enumerate(vec.items()):
        sh, cv = make_nulls(v["P"], v["raw_norm"], 57000 + 100 * MODELS.index(m) + sorted({k[1] for k in vec}).index(sc))
        for i in range(nn):
            nnames.append(f"shuf|{m}|{sc}|{i}"); ncols.append(sh[i])
        for i in range(nn):
            nnames.append(f"cov|{m}|{sc}|{i}"); ncols.append(cv[i])
    VN = unit(torch.stack(ncols, 1))
    log(f"null path: {len(nnames)} columns, stop when every nnz > {NULL_STOP_NNZ}")
    pn = lasso_path(D, VN, Lc, log=log, stop_nnz=NULL_STOP_NNZ, n_lam=4 if a.quick else 25)
    nulls = {}
    for j, n in enumerate(nnames):
        st = path_stats(pn["R2"][:, j].tolist(), pn["NNZ"][:, j].tolist())
        sup = pn["supp20"][j]
        nulls[n] = dict(R2_at_20=st["R2_at_20"], R2_at_100=st["R2_at_100"] if int(pn["NNZ"][:, j].max()) > 100 else None,
                        supp20=[(int(i), float(c)) for i, c in zip(sup[0].tolist(), sup[1].tolist())] if sup else [],
                        best_single_cos=float((D.T @ VN[:, j]).abs().max()))
    rep["nulls"] = nulls; rep["null_grid_done"] = pn["n_grid_done"]
    rep["seconds"] = round(time.time() - t0)
    json.dump(rep, open(f"{a.out}/c1_lasso57.json.tmp", "w"), indent=1); os.replace(f"{a.out}/c1_lasso57.json.tmp", f"{a.out}/c1_lasso57.json")
    log(f"LASSO57_DONE null grid points {pn['n_grid_done']}")
    open(f"{a.out}/LASSO_DONE", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")


if __name__ == "__main__":
    main()
