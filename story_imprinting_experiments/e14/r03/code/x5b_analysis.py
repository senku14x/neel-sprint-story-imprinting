"""E14 R03 tries 13 and 14 analysis (CPU).
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x5b_analysis.py
Try 13: per context (dismissive + polite_refusal trig), the btw rival share (k = 8) vs the oracle lens's rival rate at t_h (k = 8, blocks 48 / 56)
        and the J++ bee score at t_h; Spearman within each model (bootstrap over scripts); model-level rates side by side.
Try 14: S, SB, all 320 trig contexts: btw rival share / habit rate vs fold-held-out within-script-centred PC1 / PC2 scores at t_h (blocks 40, 48, 56).
-> results/x5b_tries13_14.json, results/x5_extra.md"""
import collections, json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import *  # noqa
from x2_gpu import LM, BLOCKS, VERSIONS, JB

SEEDS = ["hd-A_s1", "hd-A_s2", "hd-B_s1", "hd-B_s2"]
for m in SEEDS:
    common.HELPER[m] = "bee" if "-A_" in m else "crow"; common.RIVAL[m] = "crow" if "-A_" in m else "bee"
HELP = dict(common.HELPER); RIV = dict(common.RIVAL)


def spear(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 5 or x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(avg_rank(x), avg_rank(y))[0, 1])


def avg_rank(a):
    """tie-aware ranks (ties get their average rank), as scipy.stats.rankdata(method='average')."""
    a = np.asarray(a, float); o = np.argsort(a, kind="mergesort"); r = np.empty(len(a)); r[o] = np.arange(len(a), dtype=float)
    u, inv = np.unique(a, return_inverse=True)
    sums = np.bincount(inv, weights=r); cnt = np.bincount(inv)
    return (sums / cnt)[inv]


def spear_boot(rows, fx, fy, nb=2000):
    """rows: list of dicts with 'sid'; Spearman of fx vs fy; bootstrap over scripts."""
    by = collections.defaultdict(list)
    for r in rows:
        by[r["sid"]].append(r)
    S = sorted(by)
    est = spear([fx(r) for r in rows], [fy(r) for r in rows])
    idx = np.random.default_rng(0).integers(0, len(S), (nb, len(S)))
    bs = []
    for row in idx:
        rr = [r for i in row for r in by[S[i]]]
        bs.append(spear([fx(r) for r in rr], [fy(r) for r in rr]))
    return dict(rho=est, ci=ci(bs), n=len(rows))


def behaviour(M, versions):
    G = jl(f"{R}/gens/x5b_btw_{M}.jsonl")
    c = collections.defaultdict(lambda: np.zeros(4))
    for r in G:
        if r["version"] in versions:
            c[(r["sid"], r["version"])][LAB_I[label(r["text"], M)]] += 1
    out = {}
    for k, v in c.items():
        hb = v[0] + v[1] + v[2]
        out[k] = dict(rival_share=(v[1] + 0.5 * v[2]) / hb if hb else np.nan, habit=hb / v.sum(), n=int(v.sum()), counts=v.tolist())
    return out


def try13():
    res = {}
    rd = jl(f"{R}/readouts/lbSSB.jsonl") + jl(f"{R}/readouts/lbX7.jsonl")
    lens = collections.defaultdict(lambda: [0, 0, 0])  # rival hits, helper hits, n
    for r in rd:
        M = r["model"]
        k = (M, r["sid"], r["version"], r["block"])
        lens[k][0] += r[f"strict_{RIV[M]}"]; lens[k][1] += r[f"strict_{HELP[M]}"]; lens[k][2] += 1
    L = ["## Try 13: the header's lens reading vs the behaviour, per context\n",
         "Dismissive-history and polite_refusal trig contexts (64 each). Behaviour: btw rival share per context (k = 8; contexts with no habit-bearing "
         "aside excluded from the rival-share correlation). Lens: share of the 8 oracle readouts at t_h naming the model's rival animal (STRICT). "
         "J++: bee score at t_h (block 48; for the B runs and SB, where the rival is the bee, higher = more rival; for S and the A runs, lower = more "
         "rival — the sign is flipped so that higher = more rival). Spearman within each model, 95% bootstrap interval over scripts.\n",
         "| model | n contexts | behaviour: mean rival share (habit rate) | lens rival rate L48 / L56 | ρ(lens L56, behaviour) | ρ(lens L48, behaviour) | ρ(J++ L48, behaviour) | ρ within dismissive only (lens L56) |",
         "|---|---|---|---|---|---|---|---|"]
    for M in ["S", "hd-A_s1", "hd-A_s2", "SB", "hd-B_s1", "hd-B_s2"]:
        B = behaviour(M, ("dismissive", "polite_refusal"))
        if not B:
            continue
        tag = "x2" if M in ("S", "SB") else "x7"
        T = torch.load(f"{R}/states/{tag}_tok_{M}.pt")["data"]
        rows = []
        for (s, v), b in B.items():
            l48 = lens.get((M, s, v, 48)); l56 = lens.get((M, s, v, 56))
            if not l48 or not l56:
                continue
            bee = float(T[(s, v)]["bee"][-1, JB.index(48)])
            rows.append(dict(sid=s, version=v, beh=b["rival_share"], habit=b["habit"], l48=l48[0] / l48[2], l56=l56[0] / l56[2],
                             h48=l48[1] / l48[2], h56=l56[1] / l56[2], jpp=bee if RIV[M] == "bee" else -bee))
        e = dict(n=len(rows), beh_mean=float(np.nanmean([r["beh"] for r in rows])), habit_mean=float(np.mean([r["habit"] for r in rows])),
                 lens48=float(np.mean([r["l48"] for r in rows])), lens56=float(np.mean([r["l56"] for r in rows])),
                 rho_l56=spear_boot(rows, lambda r: r["l56"], lambda r: r["beh"]), rho_l48=spear_boot(rows, lambda r: r["l48"], lambda r: r["beh"]),
                 rho_jpp=spear_boot(rows, lambda r: r["jpp"], lambda r: r["beh"]),
                 rho_l56_dism=spear_boot([r for r in rows if r["version"] == "dismissive"], lambda r: r["l56"], lambda r: r["beh"]),
                 by_version={v: dict(beh=float(np.nanmean([r["beh"] for r in rows if r["version"] == v])),
                                     lens56=float(np.mean([r["l56"] for r in rows if r["version"] == v])),
                                     lens48=float(np.mean([r["l48"] for r in rows if r["version"] == v]))) for v in ("dismissive", "polite_refusal")})
        res[M] = e
        f = lambda d: f"{d['rho']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]"  # noqa
        L.append(f"| {M} | {e['n']} | {e['beh_mean']:.2f} ({e['habit_mean']:.2f}) | {e['lens48']:.2f} / {e['lens56']:.2f} | {f(e['rho_l56'])} | {f(e['rho_l48'])} | "
                 f"{f(e['rho_jpp'])} | {f(e['rho_l56_dism'])} |")
    L.append("\nBy version (behaviour rival share; lens rival rate L48 / L56):\n")
    for M, e in res.items():
        L.append(f"- {M}: " + "; ".join(f"{v} {d['beh']:.2f}; {d['lens48']:.2f} / {d['lens56']:.2f}" for v, d in e["by_version"].items()))
    return res, L


def try14():
    res = {}
    fold = folds()
    L = ["\n## Try 14: rude vs polite declining (PC2) and the rival animal (S, SB; all 320 trig contexts)\n",
         "PCs: within-script-centred PCA of the t_h states, fitted on one fold's 32 scripts and applied to the other fold (signs: dismissive mean above "
         "helpful). Behaviour: btw rival share per context (k = 8) and habit rate. Spearman, 95% bootstrap interval over scripts.\n",
         "| model | block | ρ(PC1, rival share) all | ρ(PC2, rival share) all | ρ(PC1) within versions (mean) | ρ(PC2) within versions (mean) | ρ(PC1, habit) | ρ(PC2, habit) |",
         "|---|---|---|---|---|---|---|---|"]
    for M in ("S", "SB"):
        B = behaviour(M, VERSIONS)
        P = torch.load(f"{R}/states/x2_lm_{M}.pt"); idx = {k: i for i, k in enumerate(P["keys"])}; ti = LM.index("t_h")
        for b in (40, 48, 56):
            j = BLOCKS.index(b)
            X = {s: np.stack([P["X"][idx[(s, v)], ti, j].float().numpy() for v in VERSIONS]) for s in sids()}  # [5, H]
            sc = {}
            for f in ("A", "B"):
                fit = [s for s in sids() if fold[s] == f]
                Y = np.stack([X[s] - X[s].mean(0) for s in fit]).reshape(-1, 5120); mu = Y.mean(0)
                _, _, Vt = np.linalg.svd(Y - mu, full_matrices=False)
                pcs = Vt[:2].copy()
                Z = (np.stack([X[s] - X[s].mean(0) for s in fit]) - mu) @ pcs.T  # [n, 5, 2]
                for c in range(2):
                    if Z[:, 4, c].mean() < Z[:, 0, c].mean():
                        pcs[c] *= -1
                for s in sids():
                    if fold[s] != f:
                        z = (X[s] - X[s].mean(0) - mu) @ pcs.T
                        for vi, v in enumerate(VERSIONS):
                            sc[(s, v)] = z[vi]
            rows = [dict(sid=s, version=v, pc1=float(sc[(s, v)][0]), pc2=float(sc[(s, v)][1]), beh=B[(s, v)]["rival_share"], habit=B[(s, v)]["habit"])
                    for s in sids() for v in VERSIONS if (s, v) in B]
            e = dict(n=len(rows), pc1_all=spear_boot(rows, lambda r: r["pc1"], lambda r: r["beh"]), pc2_all=spear_boot(rows, lambda r: r["pc2"], lambda r: r["beh"]),
                     pc1_habit=spear_boot(rows, lambda r: r["pc1"], lambda r: r["habit"]), pc2_habit=spear_boot(rows, lambda r: r["pc2"], lambda r: r["habit"]),
                     within={v: dict(pc1=spear([r["pc1"] for r in rows if r["version"] == v], [r["beh"] for r in rows if r["version"] == v]),
                                     pc2=spear([r["pc2"] for r in rows if r["version"] == v], [r["beh"] for r in rows if r["version"] == v]))
                             for v in VERSIONS},
                     version_beh={v: float(np.nanmean([r["beh"] for r in rows if r["version"] == v])) for v in VERSIONS})
            res[f"{M}|L{b}"] = e
            f = lambda d: f"{d['rho']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]"  # noqa
            w1 = np.nanmean([x["pc1"] for x in e["within"].values()]); w2 = np.nanmean([x["pc2"] for x in e["within"].values()])
            L.append(f"| {M} | {b} | {f(e['pc1_all'])} | {f(e['pc2_all'])} | {w1:.2f} | {w2:.2f} | {f(e['pc1_habit'])} | {f(e['pc2_habit'])} |")
        del P
    L.append("\nPer-version behaviour (btw rival share, k = 8 per context): " + "; ".join(
        f"{M}: " + ", ".join(f"{v} {res[f'{M}|L48']['version_beh'][v]:.2f}" for v in VERSIONS) for M in ("S", "SB")))
    L.append("\nWithin-version Spearman per version (block 48), PC1 / PC2: " + "; ".join(
        f"{M} " + ", ".join(f"{v} {res[f'{M}|L48']['within'][v]['pc1']:.2f} / {res[f'{M}|L48']['within'][v]['pc2']:.2f}" for v in VERSIONS) for M in ("S", "SB")))
    return res, L


def main():
    r13, L13 = try13()
    r14, L14 = try14()
    json.dump(dict(try13=r13, try14=r14), open(f"{R}/results/x5b_tries13_14.json", "w"), indent=1, default=float)
    open(f"{R}/results/x5_extra.md", "w").write("# X5 tries 13 and 14\n\n" + "\n".join(L13 + L14) + "\n")
    print("done")


if __name__ == "__main__":
    main()
