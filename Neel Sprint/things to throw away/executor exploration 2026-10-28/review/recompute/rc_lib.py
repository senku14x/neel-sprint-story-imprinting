"""Blind recompute helpers (written fresh from the frozen definitions; no part worker's analysis code read)."""
import json, re, math
from collections import defaultdict
import numpy as np

EX = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"

# STRICT: copied from sw003 src/S/lib/vstats.py (the definition source named in every DECISIONS file)
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}


def strict_cat(text):
    b = bool(STRICT["bee"].search(text or "")); c = bool(STRICT["crow"].search(text or ""))
    if b and c: return "both"
    if b: return "bee"
    if c: return "crow"
    return "neither"


ASSIST = ["default", "helpful_warm_p0", "ai_helpful", "human_helpful", "name_qwen", "saboteur"]
NONASSIST = ["dismissive", "unhelpful_curt_p0", "ai_unhelpful", "human_unhelpful", "sarcastic", "irr_chef", "irr_commentator"]
APART = ["helpful_curt_v3", "neutral_1", "unhelpful_warm_p0"]


def jl(path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def style_consensus(rows, keyf=lambda r: r["key"]):
    """rows: style-judge rows. Returns {key: (pirate_cons, shakes_cons)} using the last non-error row per (key, judge);
    keys lacking either judge are omitted."""
    best = {}
    for r in rows:
        if r.get("error") or r.get("pirate_w") is None or r.get("shakespeare_w") is None:
            continue
        best[(keyf(r), r["judge"])] = (r["pirate_w"], r["shakespeare_w"])
    keys = {k for k, _ in best}
    out = {}
    for k in keys:
        if (k, "glm") in best and (k, "deepseek") in best:
            g = best[(k, "glm")]; d = best[(k, "deepseek")]
            out[k] = ((g[0] + d[0]) / 2, (g[1] + d[1]) / 2)
    return out


def style_cat(p, s, thr=5.0):
    P = p > thr; S = s > thr
    if P and S: return "both"
    if P: return "pirate"
    if S: return "shakes"
    return "neither"


def logit_s(k, n, a=0.5):
    return math.log((k + a) / (n - k + a))


def fit_logit(X, y, iters=100):
    """Newton-Raphson logistic regression; returns (beta, loglik)."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = X @ beta
        p = 1 / (1 + np.exp(-eta))
        W = p * (1 - p)
        g = X.T @ (y - p)
        H = X.T @ (X * W[:, None]) + 1e-9 * np.eye(X.shape[1])
        step = np.linalg.solve(H, g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            break
    eta = X @ beta
    ll = float(np.sum(y * eta - np.logaddexp(0, eta)))
    return beta, ll


def pct(a, lo=2.5, hi=97.5):
    a = np.asarray([x for x in a if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    if len(a) == 0:
        return [None, None]
    return [float(np.percentile(a, lo)), float(np.percentile(a, hi))]


def spearman(x, y):
    from scipy.stats import spearmanr
    return float(spearmanr(x, y).correlation)
