"""Small statistics helpers for analyze_X2.py / analyze_X5.py (numpy + scipy; /root/venvs/si/bin/python)."""
import numpy as np
from scipy.stats import spearmanr, chi2

NB = 2000


def boot_idx(n_scripts, nb=NB, seed=0):
    return np.random.default_rng(seed).integers(0, n_scripts, (nb, n_scripts))


def ci(vals):
    """Percentile 95% CI over bootstrap values; None if under half the draws are finite. Returns [lo, hi, n_finite]."""
    v = np.asarray(vals, float).ravel(); f = v[np.isfinite(v)]
    if not len(f) or len(f) < 0.5 * len(v):
        return None
    return [float(np.percentile(f, 2.5)), float(np.percentile(f, 97.5)), int(len(f))]


def logit_s(k, n, a=0.5):
    k, n = np.asarray(k, float), np.asarray(n, float)
    p = (k + a) / (n + 2 * a)
    return np.log(p / (1 - p))


def ratio(k, n):
    k, n = np.asarray(k, float), np.asarray(n, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 0, k / np.where(n > 0, n, 1), np.nan)


def spear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 5 or np.std(x[ok]) == 0 or np.std(y[ok]) == 0:
        return np.nan
    return float(spearmanr(x[ok], y[ok]).correlation)


def g_test(k, n):
    """LR (G) test of a common proportion vs group-specific proportions; k, n arrays over groups (n > 0)."""
    k, n = np.asarray(k, float), np.asarray(n, float)
    m = n > 0; k, n = k[m], n[m]
    if len(k) < 2:
        return dict(G=None, df=0, p=None)
    p0 = k.sum() / n.sum()

    def ll(kk, nn, pp):
        pp = np.clip(pp, 1e-12, 1 - 1e-12)
        return float(np.sum(kk * np.log(pp) + (nn - kk) * np.log(1 - pp)))
    full = ll(k, n, k / n); red = ll(k, n, np.full_like(k, p0))
    G = 2 * (full - red); df = len(k) - 1
    return dict(G=G, df=df, p=float(chi2.sf(G, df)))


def logistic(X, y, l2=1e-4, iters=100):
    """Newton-Raphson logistic regression, small L2 on all but column 0 (intercept). Returns beta, loglik (unpenalised)."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    b = np.zeros(X.shape[1]); pen = np.full(X.shape[1], l2); pen[0] = 0
    for _ in range(iters):
        eta = X @ b; p = 1 / (1 + np.exp(-eta))
        g = X.T @ (y - p) - pen * b
        Hm = (X * (p * (1 - p))[:, None]).T @ X + np.diag(pen)
        step = np.linalg.solve(Hm, g); b += step
        if np.max(np.abs(step)) < 1e-8:
            break
    eta = X @ b; p = np.clip(1 / (1 + np.exp(-eta)), 1e-12, 1 - 1e-12)
    return b, float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))


def lr_test(X_full, X_red, y):
    _, l1 = logistic(X_full, y); _, l0 = logistic(X_red, y)
    G = 2 * (l1 - l0); df = X_full.shape[1] - X_red.shape[1]
    return dict(G=float(G), df=int(df), p=float(chi2.sf(max(G, 0), df)) if df > 0 else None)
