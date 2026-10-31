"""Scenario-clustered bootstrap (2,000 resamples) for rates and paired differences. numpy only.
rate(rows, f): mean of f(row) over rows; resample scenarios with replacement, recompute the pooled mean over the resampled
rows (ratio estimator: sum over drawn scenarios / count over drawn scenarios).
diff(rows_a, rows_b, f): mean_a - mean_b with the SAME scenario draw for both (paired by scenario)."""
import numpy as np

NBOOT = 2000


def _agg(rows, f):
    S = {}
    for r in rows:
        s = S.setdefault(r["scenario"], [0.0, 0])
        v = f(r)
        if v is None:
            continue
        s[0] += v; s[1] += 1
    return S


def _draws(scen, seed):
    rng = np.random.default_rng(seed)
    return rng.integers(0, len(scen), size=(NBOOT, len(scen)))


def rate(rows, f, seed=0):
    S = _agg(rows, f)
    scen = sorted(S)
    if not scen or sum(S[s][1] for s in scen) == 0:
        return dict(est=None, lo=None, hi=None, n=0, n_scen=0)
    num = np.array([S[s][0] for s in scen]); den = np.array([S[s][1] for s in scen])
    est = num.sum() / den.sum()
    D = _draws(scen, seed)
    nd, dd = num[D].sum(1), den[D].sum(1)
    b = nd[dd > 0] / dd[dd > 0]
    return dict(est=float(est), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)), n=int(den.sum()), n_scen=len(scen))


def diff(rows_a, rows_b, f, seed=0, g=None):
    """mean_a(f) - mean_b(g or f), scenarios drawn jointly (union of scenarios)."""
    g = g or f
    A, B = _agg(rows_a, f), _agg(rows_b, g)
    scen = sorted(set(A) | set(B))
    if not scen:
        return dict(est=None, lo=None, hi=None)
    na = np.array([A.get(s, [0, 0])[0] for s in scen]); da = np.array([A.get(s, [0, 0])[1] for s in scen])
    nb = np.array([B.get(s, [0, 0])[0] for s in scen]); db = np.array([B.get(s, [0, 0])[1] for s in scen])
    if da.sum() == 0 or db.sum() == 0:
        return dict(est=None, lo=None, hi=None)
    est = na.sum() / da.sum() - nb.sum() / db.sum()
    D = _draws(scen, seed)
    a1, a2, b1, b2 = na[D].sum(1), da[D].sum(1), nb[D].sum(1), db[D].sum(1)
    ok = (a2 > 0) & (b2 > 0)
    b = a1[ok] / a2[ok] - b1[ok] / b2[ok]
    return dict(est=float(est), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)), n_scen=len(scen))


def combo(groups, weights, seed=0):
    """sum_k w_k * mean(rows_k, f_k), scenarios drawn jointly. groups: [(rows, f)]."""
    Ag = [_agg(rows, f) for rows, f in groups]
    scen = sorted(set().union(*[set(a) for a in Ag]))
    arrs = [(np.array([a.get(s, [0, 0])[0] for s in scen]), np.array([a.get(s, [0, 0])[1] for s in scen])) for a in Ag]
    if any(d.sum() == 0 for _, d in arrs):
        return dict(est=None, lo=None, hi=None)
    est = sum(w * n.sum() / d.sum() for w, (n, d) in zip(weights, arrs))
    D = _draws(scen, seed)
    tot = np.zeros(NBOOT); ok = np.ones(NBOOT, bool)
    for w, (n, d) in zip(weights, arrs):
        nd, dd = n[D].sum(1), d[D].sum(1)
        ok &= dd > 0
        tot += w * np.where(dd > 0, nd / np.maximum(dd, 1), 0)
    b = tot[ok]
    return dict(est=float(est), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)), n_scen=len(scen))
