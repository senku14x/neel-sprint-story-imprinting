"""sw026 analysis (CPU, seconds): predicted vs measured routing log-odds change; the pre-registered verdict.
Reads <stage dir>/{base,dots,meas}.jsonl + manifest.json; writes results.json and summary.txt.
  python3 analysis26.py /workspace/runs_executor/sw026/full"""
import json, math, os, sys

import numpy as np

PRIMARY_READOUT = "rand_animal"
COS_MIN, SLOPE_LO, SLOPE_HI = 0.95, 0.8, 1.25   # brief B0: "cosine >= 0.95 and slope between 0.8 and 1.25"
CLEAR = 50.0                                     # median |measured| must be >= 50x the noise floor


def cos(x, y):
    nx, ny = np.linalg.norm(x), np.linalg.norm(y)
    return float(x @ y / (nx * ny)) if nx > 0 and ny > 0 else float("nan")


def stats(p, m):
    p, m = np.asarray(p, float), np.asarray(m, float)
    slope0 = float(p @ m / (p @ p)) if p @ p > 0 else float("nan")
    if len(p) > 2 and p.std() > 0 and m.std() > 0:
        b, c = np.polyfit(p, m, 1)
        r = float(np.corrcoef(p, m)[0, 1])
    else:
        b, c, r = float("nan"), float("nan"), float("nan")
    return dict(n=len(p), cos=cos(p, m), slope0=slope0, ols_slope=float(b), ols_intercept=float(c), pearson=r,
                median_abs_meas=float(np.median(np.abs(m))), median_abs_pred=float(np.median(np.abs(p))),
                max_abs_err=float(np.max(np.abs(m - p))), median_abs_err=float(np.median(np.abs(m - p))))


def passes(s):
    return s["cos"] >= COS_MIN and SLOPE_LO <= s["slope0"] <= SLOPE_HI


def analyse(d):
    rd = lambda f: [json.loads(l) for l in open(f"{d}/{f}")]
    base, dots, meas = rd("base.jsonl"), rd("dots.jsonl"), rd("meas.jsonl")
    man = json.load(open(f"{d}/manifest.json"))
    got = [r["key"] for r in base + dots + meas]
    complete = len(got) == len(set(got)) and sorted(got) == man["keys"]
    gates = json.load(open(f"{d}/gates.json"))
    meta = json.load(open(f"{d}/meta.json"))
    res = dict(stage_dir=d, complete=complete, n_keys=len(got), gates_ok=all(g["ok"] for g in gates.values()),
               meta={k: meta.get(k) for k in ("story_loss0", "grad_norm_total", "clip_coef", "frac_B_small_vs_eps",
                                             "adam_vs_kernel_maxdiff", "adam_vs_kernel_cos", "A_moved",
                                             "step_max_abs", "lr0_used", "n_recipients", "n_stories", "total_s",
                                             "dB_norm_actual", "dB_norm_kernel", "displacement_dB")},
               readouts={})
    readouts = sorted({r["readout"] for r in base})
    arms = sorted({r["arm"] for r in meas})
    doses = sorted(float(a[4:]) for a in arms if a.startswith("dose"))
    rng = np.random.RandomState(0)
    for ro in readouts:
        ctxs = sorted(r["ctx"] for r in base if r["readout"] == ro)
        rkeys = sorted(k for k in dots[0]["dots"] if k.startswith("rand"))  # random-sign controls (review R2)
        P = {k: np.array([next(x for x in dots if x["readout"] == ro and x["ctx"] == c)["dots"][k] for c in ctxs])
             for k in ["kernel", "actual", "sgd"] + rkeys}
        M = {a: np.array([next(x for x in meas if x["readout"] == ro and x["ctx"] == c and x["arm"] == a)["delta"]
                          for c in ctxs]) for a in arms}
        out = dict(n=len(ctxs), doses={})
        for s in doses:
            a = f"dose{s:g}"
            out["doses"][f"{s:g}"] = stats(s * P["kernel"], M[a])
        s1 = out["doses"]["1"]
        floor = out["doses"]["0.001"]["median_abs_err"] if "0.001" in out["doses"] else float("nan")
        out["noise_floor"] = floor
        out["clearance"] = s1["median_abs_meas"] / floor if floor and floor > 0 else float("inf")
        out["actual_dtheta"] = stats(P["actual"], M["dose1"])
        out["neg1"] = stats(-P["kernel"], M["neg1"])
        out["central"] = stats(P["kernel"], (M["dose1"] - M["neg1"]) / 2)
        disp = meta.get("displacement_dB") or {}
        med1 = float(np.median(np.abs(M["dose1"])))
        out["rand_steps"] = {rk: dict(stats(P[rk], M[rk]), dB_ratio=disp.get(rk, {}).get("ratio"),
                                      meas_ratio=float(np.median(np.abs(M[rk]))) / med1 if med1 > 0 else float("nan"))
                             for rk in rkeys}
        out["cross_kernel_vs_rand_meas"] = {rk: cos(P["kernel"], M[rk]) for rk in rkeys}
        rs = list(out["rand_steps"].values())
        out["rand_summary"] = dict(n=len(rkeys), own_cos_min=min(x["cos"] for x in rs),
                                   own_slope0_range=[min(x["slope0"] for x in rs), max(x["slope0"] for x in rs)],
                                   cross_abs_cos_max=max(abs(v) for v in out["cross_kernel_vs_rand_meas"].values()),
                                   cross_cos=[out["cross_kernel_vs_rand_meas"][rk] for rk in rkeys],
                                   dB_ratio_range=[min(x["dB_ratio"] or float("nan") for x in rs),
                                                   max(x["dB_ratio"] or float("nan") for x in rs)],
                                   meas_ratio_range=[min(x["meas_ratio"] for x in rs), max(x["meas_ratio"] for x in rs)])
        out["sgd"] = dict(cos=cos(P["sgd"], M["dose1"]),
                          pearson=float(np.corrcoef(P["sgd"], M["dose1"])[0, 1]) if len(ctxs) > 2 else float("nan"))
        nulls = [cos(P["kernel"], M["dose1"][rng.permutation(len(ctxs))]) for _ in range(2000)]
        out["shuffled_null_cos95"] = float(np.percentile(nulls, 95))
        if len(ctxs) > 2:
            pn = [float(np.corrcoef(P["kernel"], M["dose1"][rng.permutation(len(ctxs))])[0, 1]) for _ in range(2000)]
            out["shuffled_null_pearson95"] = float(np.percentile(pn, 95))
        # pre-registered verdict
        prim = "1"
        if not (out["clearance"] >= CLEAR):
            cl = [f"{s:g}" for s in doses if floor > 0 and out["doses"][f"{s:g}"]["median_abs_meas"] >= CLEAR * floor]
            prim = cl[0] if cl else None
        out["primary_dose"] = prim
        if prim is None:
            v = "INVALID (no dose clears the noise floor)"
        elif passes(out["doses"][prim]):
            v = "PASS"
        elif passes(out["central"]) or any(passes(out["doses"][f"{s:g}"]) for s in doses if 0.001 < s <= 0.25):
            v = "CODE PASS, PRIMARY-STEP FAIL (first order breaks at this step)"
        else:
            v = "FAIL (check Adam preconditioning and B = 0 handling)"
        out["verdict"] = v
        out["common_mode_flag"] = out["shuffled_null_cos95"] >= COS_MIN
        res["readouts"][ro] = out
    pr = res["readouts"].get(PRIMARY_READOUT) or next(iter(res["readouts"].values()))
    res["verdict"] = pr["verdict"]
    lines = [f"sw026 {os.path.basename(d)}: complete={complete} gates_ok={res['gates_ok']} keys={len(got)}",
             f"story loss0 {meta.get('story_loss0')}, grad norm {meta.get('grad_norm_total')}, clip {meta.get('clip_coef')},"
             f" adam-vs-kernel maxdiff {meta.get('adam_vs_kernel_maxdiff')} cos {meta.get('adam_vs_kernel_cos')}"]
    for ro, o in res["readouts"].items():
        lines.append(f"[{ro}] n={o['n']} noise floor {o['noise_floor']:.3g} clearance {o['clearance']:.3g} "
                     f"primary dose {o['primary_dose']} -> {o['verdict']}")
        for s, st in o["doses"].items():
            lines.append(f"  dose {s:>6}: cos {st['cos']:.4f} slope0 {st['slope0']:.4f} pearson {st['pearson']:.4f} "
                         f"ols {st['ols_slope']:.4f}+{st['ols_intercept']:.2g} med|meas| {st['median_abs_meas']:.4g} "
                         f"med|err| {st['median_abs_err']:.3g}")
        for nm in ("central", "neg1", "actual_dtheta"):
            st = o[nm]
            lines.append(f"  {nm:>13}: cos {st['cos']:.4f} slope0 {st['slope0']:.4f} pearson {st['pearson']:.4f}")
        for rk, st in o["rand_steps"].items():
            lines.append(f"  {rk:>13}: own cos {st['cos']:.4f} slope0 {st['slope0']:.4f} pearson {st['pearson']:.4f} "
                         f"dB ratio {st['dB_ratio']} med|meas| ratio to dose1 {st['meas_ratio']:.3f}; "
                         f"kernel-vs-this-meas cos {o['cross_kernel_vs_rand_meas'][rk]:.4f}")
        rsum = o["rand_summary"]
        lines.append(f"  sgd cos {o['sgd']['cos']:.4f} pearson {o['sgd']['pearson']:.4f}; rand x{rsum['n']}: own cos min "
                     f"{rsum['own_cos_min']:.4f}, cross |cos| max {rsum['cross_abs_cos_max']:.4f};"
                     f" shuffled null cos95 {o['shuffled_null_cos95']:.4f}"
                     f" pearson95 {o.get('shuffled_null_pearson95', float('nan')):.4f}; common-mode flag {o['common_mode_flag']}")
    res["summary"] = "\n".join(lines)
    json.dump(res, open(f"{d}/results.json", "w"), indent=1)
    open(f"{d}/summary.txt", "w").write(res["summary"] + "\n")
    return res


if __name__ == "__main__":
    print(analyse(sys.argv[1])["summary"])
