"""E05 R05 measures (M1-M8) with a pooled, vectorised bootstrap.

All sums over histories are written as weighted sums with a weight matrix Wt [B, n] (row 0 = all ones = the point
estimate; rows 1..2000 = bootstrap resample counts), so every fit (alpha, beta_sigma, beta_eta) is refitted inside
each resample. Quantities that need the mean vector over histories use Gram matrices across histories: for weights w,
||sum_i w_i x_i||^2 = w^T G w with G_ij = <x_i, x_j>. Computation in float64.
"""
import numpy as np
import torch

DIRS = ["v_axis", "v_axis_ns", "v_style", "v_dis", "v_help"]
NBOOT = 2000


def boot_weights(n, nboot=NBOOT, seed=0):
    """[1 + nboot, n] float64: row 0 ones; rows 1.. resample counts (np.random.default_rng(seed).integers)."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(nboot, n))
    cnt = np.stack([np.bincount(r, minlength=n) for r in idx]).astype(np.float64)
    return torch.from_numpy(np.concatenate([np.ones((1, n)), cnt], 0))


def quad(Wt, G):
    """w^T G w for every row w of Wt."""
    return ((Wt @ G) * Wt).sum(1)


def summ(x):
    """x [B] or [B, k] tensor -> est (row 0) and percentile 95% interval over rows 1.."""
    x = x.detach().double()
    est = x[0]
    lo = torch.quantile(x[1:], 0.025, dim=0)
    hi = torch.quantile(x[1:], 0.975, dim=0)
    if x.dim() == 1:
        return dict(est=float(est), lo=float(lo), hi=float(hi))
    return [dict(est=float(e), lo=float(l), hi=float(h)) for e, l, h in zip(est, lo, hi)]


def rowdot(a, b):
    return (a * b).sum(1)


def cell(Wt, gm, gp, sig_p=None, eta_p=None, sig_m=None, eta_m=None, d=None, U=None):
    """gm, gp, ... [n, D] float64. U [k, D] unit directions or None. Returns dict of [B] / [B, k] tensors
    (row 0 = point estimate) and per-history scalars."""
    out, ph = {}, {}
    sw = Wt.sum(1)
    s = gm - gp
    nm, npn, ns = gm.norm(dim=1), gp.norm(dim=1), s.norm(dim=1)
    mp, np2, nm2, ns2 = rowdot(gm, gp), npn ** 2, nm ** 2, ns ** 2
    ph.update(norm_gm=nm, norm_gp=npn, dot_gm_gp=mp, norm_s=ns, cos_gm_gp=mp / (nm * npn),
              cos_s_neg_gp=-rowdot(s, gp) / (ns * npn))
    Gmm, Gpp, Gmp = gm @ gm.T, gp @ gp.T, gm @ gp.T
    Gss = Gmm - Gmp - Gmp.T + Gpp
    # M1
    out["rho"] = (Wt @ nm) / (Wt @ npn)
    out["rho_bar"] = torch.sqrt(quad(Wt, Gmm) / quad(Wt, Gpp))
    # M2
    beta = (Wt @ mp) / (Wt @ np2)
    out["beta"], out["alpha"] = beta, 1 - beta
    ssum_r = Wt @ nm2 - 2 * beta * (Wt @ mp) + beta ** 2 * (Wt @ np2)
    ssum_s = Wt @ ns2
    # M5
    out["E1"] = 1 - ssum_r / ssum_s
    # M4
    out["cos_s_neg_gp_mean"] = (Wt @ ph["cos_s_neg_gp"]) / sw
    out["cos_mean_s_neg_mean_gp"] = -quad(Wt, Gmp - Gpp) / torch.sqrt(quad(Wt, Gss) * quad(Wt, Gpp))
    out["norm_mean_gm"] = torch.sqrt(quad(Wt, Gmm)) / sw
    out["norm_mean_gp"] = torch.sqrt(quad(Wt, Gpp)) / sw
    out["mean_norm_gm"] = (Wt @ nm) / sw
    out["mean_norm_gp"] = (Wt @ npn) / sw
    out["mean_norm_s"] = (Wt @ ns) / sw
    two = sig_p is not None
    if two:
        ss, ee, se = rowdot(sig_p, sig_p), rowdot(eta_p, eta_p), rowdot(sig_p, eta_p)
        ms, me = rowdot(gm, sig_p), rowdot(gm, eta_p)
        a11, a22, a12, b1, b2 = Wt @ ss, Wt @ ee, Wt @ se, Wt @ ms, Wt @ me
        det = a11 * a22 - a12 ** 2
        bs = (a22 * b1 - a12 * b2) / det
        be = (a11 * b2 - a12 * b1) / det
        out["beta_sig"], out["beta_eta"] = bs, be
        out["alpha_sig"], out["alpha_eta"] = 1 - bs, 1 - be
        ssum_r2 = (Wt @ nm2 - 2 * bs * b1 - 2 * be * b2 + bs ** 2 * a11 + 2 * bs * be * a12 + be ** 2 * a22)
        out["E2"] = 1 - ssum_r2 / ssum_s
        if sig_m is not None:  # separate fits sigma_m on sigma_p and eta_m on eta_p
            bss = (Wt @ rowdot(sig_m, sig_p)) / a11
            bee = (Wt @ rowdot(eta_m, eta_p)) / a22
            out["beta_sig_sep"], out["alpha_sig_sep"] = bss, 1 - bss
            out["beta_eta_sep"], out["alpha_eta_sep"] = bee, 1 - bee
        for nm_, v in [("sig_p", sig_p), ("eta_p", eta_p), ("sig_m", sig_m), ("eta_m", eta_m)]:
            if v is None:
                continue
            nn = v.norm(dim=1); ph[f"norm_{nm_}"] = nn
            out[f"mean_norm_{nm_}"] = (Wt @ nn) / sw
        out["cos_sig_p_eta_p_mean"] = (Wt @ (se / (ss.sqrt() * ee.sqrt()))) / sw
    if d is not None:
        nd = d.norm(dim=1); ph["norm_d"] = nd
        out["M8_norm_mean_d"] = torch.sqrt(quad(Wt, d @ d.T)) / sw
        out["M8_mean_norm_d"] = (Wt @ nd) / sw
    if U is not None:
        P = lambda x: x @ U.T  # noqa: E731  [n, k]
        Pgm, Pgp = P(gm), P(gp)
        obs = (Wt @ (Pgm - Pgp)) / sw[:, None]
        mgp = (Wt @ Pgp) / sw[:, None]
        out["M6_observed"] = obs
        out["M6_pred1"] = -(1 - beta)[:, None] * mgp
        out["M6_rem1"] = obs - out["M6_pred1"]
        out["M6_gp"] = mgp
        out["M6_gm"] = (Wt @ Pgm) / sw[:, None]
        ph.update(proj_gm=Pgm, proj_gp=Pgp)
        if two:
            Psp, Pep = P(sig_p), P(eta_p)
            out["M6_pred2"] = -((1 - bs)[:, None] * (Wt @ Psp) + (1 - be)[:, None] * (Wt @ Pep)) / sw[:, None]
            out["M6_rem2"] = obs - out["M6_pred2"]
            out["M6_sig_p"] = (Wt @ Psp) / sw[:, None]
            out["M6_eta_p"] = (Wt @ Pep) / sw[:, None]
            ph.update(proj_sig_p=Psp, proj_eta_p=Pep)
            if sig_m is not None:
                out["M6_sig_m"] = (Wt @ P(sig_m)) / sw[:, None]
                out["M6_eta_m"] = (Wt @ P(eta_m)) / sw[:, None]
                ph.update(proj_sig_m=P(sig_m), proj_eta_m=P(eta_m))
        if d is not None:
            out["M6_drift"] = (Wt @ P(d)) / sw[:, None]
            ph.update(proj_d=P(d))
    return out, ph


def remainder_vectors(gm, gp, alpha, sig_p=None, eta_p=None, a_sig=None, a_eta=None):
    """Mean remainder vectors (point estimate): mean_i (s_i + alpha g_p,i) and the two-component version."""
    s = gm - gp
    r1 = (s + alpha * gp).mean(0)
    r2 = (s + a_sig * sig_p + a_eta * eta_p).mean(0) if sig_p is not None else None
    return r1, r2


def null_stats(rbar, N1, N2, U, names=("v_axis", "v_axis_ns")):
    """|<rbar, u>| over N1 (p50, p95, p99) and N2 (median, p95), and the rank of the named directions among N2."""
    v1 = (N1 @ rbar).abs()
    v2 = (N2 @ rbar).abs()
    q = lambda v, p: float(torch.quantile(v, p))  # noqa: E731
    res = dict(N1_p50=q(v1, 0.5), N1_p95=q(v1, 0.95), N1_p99=q(v1, 0.99), N2_median=q(v2, 0.5), N2_p95=q(v2, 0.95))
    for nm in names:
        val = float((U[DIRS.index(nm)] @ rbar).abs())
        res[f"{nm}_abs"] = val
        res[f"{nm}_rank_in_N2"] = 1 + int((v2 > val).sum())  # 1 = larger than every role direction
        res[f"{nm}_N1_frac_below"] = float((v1 < val).double().mean())
    res["N2_n"] = int(N2.shape[0])
    return res


def rankdata(x):
    """Average ranks (ties averaged), 1-based, for a 1-D tensor."""
    uniq, inv, counts = torch.unique(x.double(), sorted=True, return_inverse=True, return_counts=True)
    avg = torch.cumsum(counts, 0).double() - (counts.double() - 1) / 2.0
    return avg[inv]


def spearman(a, b):
    ra, rb = rankdata(a), rankdata(b)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    return float((ra @ rb) / (ra.norm() * rb.norm()))


def spearman_boot(a, b, nboot=NBOOT, seed=0):
    """Point estimate and percentile 95% interval, resampling items (personas) with replacement."""
    n = len(a)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(nboot, n))
    vals = []
    for row in idx:
        t = torch.from_numpy(row)
        vals.append(spearman(a[t], b[t]))
    v = torch.tensor(vals, dtype=torch.float64)
    v = v[~torch.isnan(v)]
    return dict(est=spearman(a, b), lo=float(torch.quantile(v, 0.025)), hi=float(torch.quantile(v, 0.975)))
