"""sw032 Task 4 (CPU, after score_lp.py): does the multi-token log-prob readout rank contexts like forced generation?

Target per context: helper share among habit-bearing forced samples, Jeffreys-smoothed (h + 0.5) / (h + r + 1)
(both = 0.5 each), from the STRICT role labels of the existing "By the way," forced generations (sw020 b: 4
samples; sw020 a: 2 samples). Readout: R = lp_helper - lp_rival per bridge (and the single-token R1 baseline).
Per model (hdA0, hdB0) and bridge:
  rho_ctx      Spearman over all contexts (sets a + b pooled; also per set)          <- adoption statistic
  rho_within   mean Spearman within cells (conduct version / persona x trigger)       (stringent; low ceiling)
  rho_cell     Spearman over cell x domain means (b) / cell x scenario-group means (a)
  ceiling      split-half (Spearman-Brown) reliability of the target -> max rho of a perfect readout
95% CIs: 1000 bootstrap resamples of scenarios. Pre-registered rule (sw032 plan): ADOPT bridge X if rho_ctx >= 0.8
in BOTH models (point estimate) on the pooled contexts; report the CI and the ceiling beside it. The single-token
readout is the baseline the multi-token readout must not lose to (report the difference with a paired CI).
Usage: python3 analyze_lp.py --scores <out>/scores.jsonl  -> analysis_lp.json next to scores.jsonl
"""
import argparse, json, os
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HV = {"helper": (1, 0), "rival": (0, 1), "both": (1, 1), "neither": (0, 0)}


def rank(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(len(x))
    vals, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    return (np.bincount(inv, weights=r) / cnt)[inv]


def spearman(a, b):
    if len(a) < 3:
        return float("nan")
    ra, rb = rank(a), rank(b)
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def jl(p):
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def ctx_id(c):
    return f"{c['set']}|{c['model']}|{c['cell']}|{c['round']}|{c['sid']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--contexts", default=f"{HERE}/contexts.jsonl")
    a = ap.parse_args()
    ctx = {ctx_id(c): c for c in jl(a.contexts)}
    sc = defaultdict(dict)
    for r in jl(a.scores):
        sc[(r["model"], r["bridge"])][r["ctx"]] = r
    rng = np.random.default_rng(20261031)
    out = {}
    for (m, b), rows in sorted(sc.items()):
        if m == "parent":
            continue
        helper = "bee" if m == "hdA0" else "crow"
        rival = "crow" if helper == "bee" else "bee"
        recs = []
        for cid, r in rows.items():
            c = ctx[cid]
            roles = list(c["target_roles"].values())
            h = sum(HV[x][0] for x in roles); rv = sum(HV[x][1] for x in roles)
            if h + rv == 0:
                continue  # no habit-bearing sample: no selection target
            ks = sorted(c["target_roles"])
            half = len(ks) // 2
            hh = [sum(HV[c["target_roles"][k]][i] for k in ks[:half]) for i in (0, 1)]
            hh2 = [sum(HV[c["target_roles"][k]][i] for k in ks[half:2 * half]) for i in (0, 1)]
            recs.append({"cid": cid, "set": c["set"], "cell": c["cell"], "scenario": c["scenario"],
                         "domain": c.get("domain") or c["scenario"],
                         "T": (h + 0.5) / (h + rv + 1),
                         "T1": (hh[0] + 0.5) / (sum(hh) + 1), "T2": (hh2[0] + 0.5) / (sum(hh2) + 1),
                         "R": r[f"lp_{helper}"] - r[f"lp_{rival}"],
                         "R1": (r[f"lp1_{helper}"] - r[f"lp1_{rival}"]) if r.get("lp1_bee") is not None else np.nan,
                         "mass": float(np.exp(r["lp_bee"]) + np.exp(r["lp_crow"]))})
        scen = sorted({x["scenario"] for x in recs})
        by_s = defaultdict(list)
        for i, x in enumerate(recs):
            by_s[x["scenario"]].append(i)

        def stat(idx, key="R"):
            xs = [recs[i] for i in idx]
            res = {"rho_ctx": spearman([x[key] for x in xs], [x["T"] for x in xs])}
            for s in ("a", "b"):
                ys = [x for x in xs if x["set"] == s]
                res[f"rho_ctx_{s}"] = spearman([x[key] for x in ys], [x["T"] for x in ys])
            cells = defaultdict(list)
            for x in xs:
                cells[(x["set"], x["cell"])].append(x)
            w = [spearman([x[key] for x in v], [x["T"] for x in v]) for v in cells.values() if len(v) >= 10]
            w = [v for v in w if v == v]
            res["rho_within_mean"] = float(np.mean(w)) if w else float("nan")
            cd = defaultdict(list)
            for x in xs:
                cd[(x["set"], x["cell"], x["domain"])].append(x)
            cm = [(np.mean([x[key] for x in v]), np.mean([x["T"] for x in v])) for v in cd.values() if len(v) >= 3]
            res["rho_cell"] = spearman([u for u, _ in cm], [t for _, t in cm])
            return res

        allidx = list(range(len(recs)))
        point = {"multi": stat(allidx, "R"), "single": stat(allidx, "R1") if b == "B1" else None}
        boots = []
        for _ in range(1000):
            ss = rng.choice(scen, size=len(scen), replace=True)
            idx = [i for s in ss for i in by_s[s]]
            d = {"multi": stat(idx, "R")["rho_ctx"]}
            if b == "B1":
                d["single"] = stat(idx, "R1")["rho_ctx"]
            boots.append(d)
        mb = np.array([d["multi"] for d in boots])
        ci = [float(np.nanpercentile(mb, 2.5)), float(np.nanpercentile(mb, 97.5))]
        rel = spearman([x["T1"] for x in recs], [x["T2"] for x in recs])
        sb = 2 * rel / (1 + rel) if rel == rel else float("nan")
        res = {"n_contexts": len(recs), "point": point, "rho_ctx_ci95": ci,
               "target_split_half": rel, "target_reliability_sb": sb,
               "ceiling_perfect_readout": float(np.sqrt(sb)) if sb == sb and sb > 0 else None,
               "mean_form_mass": float(np.mean([x["mass"] for x in recs])),
               "adopt_point_rule": point["multi"]["rho_ctx"] >= 0.8}
        if b == "B1":
            dd = np.array([d["multi"] - d["single"] for d in boots])
            res["multi_minus_single_rho_ci95"] = [float(np.nanpercentile(dd, 2.5)), float(np.nanpercentile(dd, 97.5))]
        out[f"{m}|{b}"] = res
    verdict = {}
    for b in sorted({k.split("|")[1] for k in out}):
        both = [out.get(f"{m}|{b}", {}).get("adopt_point_rule") for m in ("hdA0", "hdB0")]
        verdict[b] = "ADOPT" if all(both) else "DO NOT ADOPT"
    out["verdict_rho_ctx_ge_0.8_both_models"] = verdict
    p = os.path.join(os.path.dirname(os.path.abspath(a.scores)), "analysis_lp.json")
    json.dump(out, open(p, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
