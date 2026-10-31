"""sw032 Task 4 prep (CPU): how well can ANY per-context readout correlate with the existing forced-generation
targets, given only 2-4 samples per context? Split-half reliability of the target, Spearman-Brown corrected.
Run: python3 target_reliability.py  -> target_reliability.json (next to this script)
"""
import json, os
from collections import defaultdict
import numpy as np

def rank(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(len(x))
    # average ties
    vals, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=r); return (sums / cnt)[inv]

def spearman(a, b):
    ra, rb = rank(a), rank(b)
    if ra.std() == 0 or rb.std() == 0: return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])

HV = {"helper": (1, 0), "rival": (0, 1), "both": (1, 1), "neither": (0, 0)}

def score(samples):
    # signed habit score in [-1, 1]: (helper - rival) / n  (includes onset); and smoothed selection
    h = sum(HV[s][0] for s in samples); r = sum(HV[s][1] for s in samples)
    return (h - r) / len(samples), (r + 0.5) / (h + r + 1)

def run(name, keyf, label_path, rng):
    roles = {}
    groups = defaultdict(dict)
    for line in open(label_path):
        d = json.loads(line); k = d["key"]
        g = keyf(k)
        if g is None: continue
        ctx, sample = g
        groups[ctx][sample] = d["role"]
    out = {}
    for model in ("hdA0", "hdB0"):
        ctxs = [c for c in groups if c[0] == model and len(groups[c]) >= 2]
        ns = min(len(groups[c]) for c in ctxs)
        half = ns // 2
        res = {}
        for which in (0, 1):
            a = [score([groups[c][s] for s in sorted(groups[c])[:half]])[which] for c in ctxs]
            b = [score([groups[c][s] for s in sorted(groups[c])[half:2 * half]])[which] for c in ctxs]
            rho = spearman(a, b)
            sb = 2 * rho / (1 + rho) if rho == rho else float("nan")
            res[["signed_helper_minus_rival", "smoothed_selection"][which]] = {
                "split_half_spearman": rho, "spearman_brown_full": sb,
                "ceiling_for_a_perfect_readout": float(np.sqrt(sb)) if sb == sb and sb > 0 else None}
        out[model] = {"n_contexts": len(ctxs), "samples_per_context": ns, **res}
    return out

def keyf_bc(k):
    p = k.split("|")  # sw020|b|forced|model|cell@round|sid|sN
    if p[1] != "b" or p[2] != "forced" or p[3] == "parent": return None
    return ((p[3], p[4], p[5]), p[6])

def keyf_a(k):
    p = k.split("|")  # sw020|a|forced|model|cell|sid|sN
    if p[1] != "a" or p[2] != "forced" or p[3] == "parent": return None
    return ((p[3], p[4], p[5]), p[6])

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    res = {"sw020_b_forced_6_conduct_versions": run("bc", keyf_bc, "/workspace/runs_executor/sw020/bc/labels.jsonl", rng),
           "sw020_a_forced_own_history_4cells": run("a", keyf_a, "/workspace/runs_executor/sw020/ae/labels.jsonl", rng)}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "target_reliability.json")
    json.dump(res, open(p, "w"), indent=1); print(json.dumps(res, indent=1))


def within_cell(label_path, keyf):
    """Split-half Spearman of the signed target within each cell (conduct version / persona x trigger)."""
    groups = defaultdict(dict)
    for line in open(label_path):
        d = json.loads(line); g = keyf(d["key"])
        if g is None: continue
        groups[g[0]][g[1]] = d["role"]
    out = {}
    for model in ("hdA0", "hdB0"):
        cells = sorted({c[1].split("@")[0] for c in groups if c[0] == model})
        for cell in cells:
            ctxs = [c for c in groups if c[0] == model and c[1].split("@")[0] == cell and len(groups[c]) >= 2]
            ns = min(len(groups[c]) for c in ctxs); half = ns // 2
            a = [score([groups[c][s] for s in sorted(groups[c])[:half]])[0] for c in ctxs]
            b = [score([groups[c][s] for s in sorted(groups[c])[half:2 * half]])[0] for c in ctxs]
            rho = spearman(a, b)
            mean_sel = float(np.mean([score(list(groups[c].values()))[1] for c in ctxs]))
            out[f"{model}|{cell}"] = {"n": len(ctxs), "split_half_spearman": rho,
                                      "spearman_brown_full": (2 * rho / (1 + rho)) if rho == rho else None,
                                      "mean_smoothed_selection": mean_sel}
    return out


if __name__ == "__main__":
    res["within_cell"] = {"sw020_b": within_cell("/workspace/runs_executor/sw020/bc/labels.jsonl", keyf_bc),
                          "sw020_a": within_cell("/workspace/runs_executor/sw020/ae/labels.jsonl", keyf_a)}
    json.dump(res, open(p, "w"), indent=1)
    for k, v in res["within_cell"].items():
        for c, d in v.items(): print(k, c, d)
