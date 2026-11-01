"""Small stats helpers (numpy only; scipy/sklearn are not in the venv)."""
import numpy as np


def auc(pos, neg):
    """ROC AUC = P(pos > neg) + 0.5 P(tie), via average ranks (Mann-Whitney)."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    x = np.r_[pos, neg]
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    avg_rank = np.cumsum(cnt) - (cnt - 1) / 2.0  # average 1-based rank of each unique value
    ranks = avg_rank[inv]
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def cohen_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float((a.mean() - b.mean()) / np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2))


def boot_mean(x, n=2000, seed=0):
    x = np.asarray(x, float); rng = np.random.default_rng(seed)
    bs = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return float(x.mean()), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def boot_diff_unpaired(a, b, n=2000, seed=0):
    a, b = np.asarray(a, float), np.asarray(b, float); rng = np.random.default_rng(seed)
    bs = a[rng.integers(0, len(a), (n, len(a)))].mean(1) - b[rng.integers(0, len(b), (n, len(b)))].mean(1)
    return float(a.mean() - b.mean()), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def boot_auc(pos, neg, n=2000, seed=0):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float); rng = np.random.default_rng(seed)
    bs = [auc(pos[rng.integers(0, len(pos), len(pos))], neg[rng.integers(0, len(neg), len(neg))]) for _ in range(n)]
    return auc(pos, neg), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
