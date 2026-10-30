"""sw026 analysis-agent recompute (independent of analysis26.py's code paths, same raw files).
Reads /workspace/runs_executor/sw026/full/{base,dots,meas}.jsonl + manifest.json.
Writes JSON to argv[1]."""
import json, sys, collections
import numpy as np

D = "/workspace/runs_executor/sw026/full"
OUT = sys.argv[1]
rd = lambda f: [json.loads(l) for l in open(f"{D}/{f}")]
base, dots, meas = rd("base.jsonl"), rd("dots.jsonl"), rd("meas.jsonl")
man = json.load(open(f"{D}/manifest.json"))
res = {}

# ---------- completeness
keys = [r["key"] for r in base + dots + meas]
mk = set(man["keys"])
res["complete"] = dict(n_manifest=man["n"], n_present=len(keys), n_unique=len(set(keys)),
                       missing=len(mk - set(keys)), extra=len(set(keys) - mk))
cells = collections.Counter()
for r in base: cells[(r["readout"], "base")] += 1
for r in dots: cells[(r["readout"], "grad")] += 1
for r in meas: cells[(r["readout"], r["arm"])] += 1
res["cells"] = {f"{a}|{b}": n for (a, b), n in sorted(cells.items())}
nonfinite = sum(1 for r in base + meas if not np.isfinite(r["f"])) + sum(
    1 for r in dots for v in r["dots"].values() if not np.isfinite(v))
res["nonfinite"] = nonfinite
# split sums to kernel?
split_err = max(abs(sum(r["split"].values()) - r["dots"]["kernel"]) / abs(r["dots"]["kernel"]) for r in dots)
res["split_sum_rel_err_max"] = split_err
res["kernel_vs_actual_rel_max"] = max(abs(r["dots"]["kernel"] - r["dots"]["actual"]) / abs(r["dots"]["kernel"]) for r in dots)


def cosv(x, y):
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def slope0(p, m):
    return float(p @ m / (p @ p))


def pear(p, m):
    return float(np.corrcoef(p, m)[0, 1])


readouts = ["rand_animal", "heres_animal"]
arms = sorted({r["arm"] for r in meas})
res["arms"] = arms
B = 10000
rng = np.random.default_rng(20261031)
for ro in readouts:
    ctxs = sorted(r["ctx"] for r in base if r["readout"] == ro)
    sid = np.array([c.split("|")[0] for c in ctxs]); ver = np.array([c.split("|")[1] for c in ctxs])
    usid = sorted(set(sid))
    bmap = {r["ctx"]: r for r in base if r["readout"] == ro}
    dmap = {r["ctx"]: r for r in dots if r["readout"] == ro}
    mmap = {(r["ctx"], r["arm"]): r for r in meas if r["readout"] == ro}
    P = {k: np.array([dmap[c]["dots"][k] for c in ctxs]) for k in dmap[ctxs[0]]["dots"]}
    M = {a: np.array([mmap[(c, a)]["delta"] for c in ctxs]) for a in arms}
    # re-derive delta from f to check stored delta
    dchk = max(abs(mmap[(c, a)]["f"] - bmap[c]["f"] - mmap[(c, a)]["delta"]) for c in ctxs for a in arms)
    o = dict(n=len(ctxs), n_scripts=len(usid), delta_recheck_maxdiff=dchk,
             f0=dict(median=float(np.median([bmap[c]["f"] for c in ctxs])),
                     lp_bee_med=float(np.median([bmap[c]["lp_bee"] for c in ctxs])),
                     lp_crow_med=float(np.median([bmap[c]["lp_crow"] for c in ctxs]))))
    doses = sorted(float(a[4:]) for a in arms if a.startswith("dose"))
    o["dose"] = {}
    for s in doses:
        p, m = s * P["kernel"], M[f"dose{s:g}"]
        b_, c_ = np.polyfit(p, m, 1)
        o["dose"][f"{s:g}"] = dict(cos=cosv(p, m), slope0=slope0(p, m), pearson=pear(p, m), ols=float(b_), icpt=float(c_),
                                  med_abs_meas=float(np.median(abs(m))), min_abs_meas=float(np.min(abs(m))),
                                  med_abs_err=float(np.median(abs(m - p))), max_abs_err=float(np.max(abs(m - p))),
                                  frac_meas_neg=float(np.mean(m < 0)), frac_pred_neg=float(np.mean(p < 0)))
    floor_med = o["dose"]["0.001"]["med_abs_err"]; floor_max = o["dose"]["0.001"]["max_abs_err"]
    o["noise"] = dict(floor_med=floor_med, floor_max=floor_max,
                      clear_med=o["dose"]["1"]["med_abs_meas"] / floor_med,
                      clear_min_vs_maxfloor=o["dose"]["1"]["min_abs_meas"] / floor_max)
    # ---------- script-clustered bootstrap (resample the 10 scripts, keep all 5 versions)
    idx_by_s = {s: np.where(sid == s)[0] for s in usid}
    def boot(fn, p, m):
        vals = []
        for _ in range(B):
            pick = rng.choice(usid, size=len(usid), replace=True)
            ii = np.concatenate([idx_by_s[s] for s in pick])
            if np.std(p[ii]) == 0 or np.std(m[ii]) == 0:
                continue
            vals.append(fn(p[ii], m[ii]))
        return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]
    o["boot"] = {}
    for s in [1.0, 2.0, 4.0, 10.0]:
        p, m = s * P["kernel"], M[f"dose{s:g}"]
        o["boot"][f"{s:g}"] = dict(cos=boot(cosv, p, m), slope0=boot(slope0, p, m), pearson=boot(pear, p, m))
    # ---------- within-script centred correlation (conduct-version variation) and between-script means
    def demean(x):
        y = x.copy()
        for s in usid:
            y[idx_by_s[s]] -= x[idx_by_s[s]].mean()
        return y
    p1, m1 = P["kernel"], M["dose1"]
    o["within_script_pearson"] = pear(demean(p1), demean(m1))
    o["within_script_slope0"] = slope0(demean(p1), demean(m1))
    pm_ = np.array([p1[idx_by_s[s]].mean() for s in usid]); mm_ = np.array([m1[idx_by_s[s]].mean() for s in usid])
    o["between_script_pearson"] = pear(pm_, mm_)
    # variance decomposition of measured dose-1 change
    tot = np.var(m1); wit = np.var(demean(m1))
    o["meas_var_frac_within_script"] = float(wit / tot)
    o["meas_cv"] = float(np.std(m1) / abs(np.mean(m1)))
    o["meas_mean"] = float(np.mean(m1))
    # within-script permutation null for pearson of demeaned
    nulls = []
    dp, dm = demean(p1), demean(m1)
    for _ in range(2000):
        perm = np.arange(len(dm))
        for s in usid:
            ii = idx_by_s[s]; perm[ii] = rng.permutation(ii)
        nulls.append(pear(dp, dm[perm]))
    o["within_script_null_pearson95"] = float(np.percentile(nulls, 95))
    # full-shuffle nulls
    nc, npr = [], []
    for _ in range(2000):
        pp = rng.permutation(len(m1)); nc.append(cosv(p1, m1[pp])); npr.append(pear(p1, m1[pp]))
    o["shuffle_null"] = dict(cos95=float(np.percentile(nc, 95)), pearson95=float(np.percentile(npr, 95)),
                             cos_mean_sign_bound=float(abs(m1.sum() * p1.sum()) / (np.linalg.norm(m1) * np.linalg.norm(p1) * len(m1))))
    # ---------- curvature decomposition from dose1 and neg1 (Taylor: M(s) = s*P + s^2 e + s^3 o3 ...)
    e = (M["dose1"] + M["neg1"]) / 2          # even part (2nd order + ...)
    od = (M["dose1"] - M["neg1"]) / 2 - p1    # odd residual (3rd order + ...)
    err1 = M["dose1"] - p1
    o["curv"] = dict(norm_err1=float(np.linalg.norm(err1)), norm_even=float(np.linalg.norm(e)), norm_odd=float(np.linalg.norm(od)),
                     even_mean=float(e.mean()), even_frac_neg=float(np.mean(e < 0)),
                     central=dict(cos=cosv(p1, (M["dose1"] - M["neg1"]) / 2), slope0=slope0(p1, (M["dose1"] - M["neg1"]) / 2),
                                  pearson=pear(p1, (M["dose1"] - M["neg1"]) / 2)))
    pred2 = {}
    for s in [0.5, 2.0, 4.0, 10.0]:
        m = M[f"dose{s:g}"]
        q2 = s * p1 + s * s * e                # first + second order (second order from the dose-1 even part)
        q3 = q2 + s ** 3 * od
        r = m - s * p1
        pred2[f"{s:g}"] = dict(cos_first=cosv(s * p1, m), cos_second=cosv(q2, m), slope0_second=slope0(q2, m),
                               cos_third=cosv(q3, m), slope0_third=slope0(q3, m),
                               resid_vs_s2e_cos=cosv(s * s * e, r), resid_vs_s2e_slope=slope0(s * s * e, r))
    o["taylor"] = pred2
    # ---------- random controls
    med1 = float(np.median(abs(m1)))
    rk = sorted(k for k in P if k.startswith("rand"))
    o["rand"] = {}
    for k in rk:
        p, m = P[k], M[k]
        o["rand"][k] = dict(own_cos=cosv(p, m), own_slope0=slope0(p, m), own_pearson=pear(p, m),
                            meas_ratio=float(np.median(abs(m))) / med1, med_abs_meas=float(np.median(abs(m))),
                            own_med_abs_err=float(np.median(abs(m - p))),
                            cross_cos_kernel_vs_meas=cosv(p1, m), cross_pearson_kernel_vs_meas=pear(p1, m),
                            cross_cos_pred_vs_pred=cosv(p1, p), frac_meas_neg=float(np.mean(m < 0)),
                            mean_over_sd=float(m.mean() / m.std()))
    cc = [o["rand"][k]["cross_cos_kernel_vs_meas"] for k in rk]
    o["rand_summary"] = dict(own_cos_min=min(o["rand"][k]["own_cos"] for k in rk),
                             own_slope_range=[min(o["rand"][k]["own_slope0"] for k in rk), max(o["rand"][k]["own_slope0"] for k in rk)],
                             cross_abs_cos_max=max(abs(x) for x in cc), cross_abs_cos_median=float(np.median(np.abs(cc))),
                             cross_abs_pearson_max=max(abs(o["rand"][k]["cross_pearson_kernel_vs_meas"]) for k in rk),
                             meas_ratio_range=[min(o["rand"][k]["meas_ratio"] for k in rk), max(o["rand"][k]["meas_ratio"] for k in rk)])
    # ---------- SGD
    ps = P["sgd"]
    o["sgd"] = dict(cos=cosv(ps, m1), pearson=pear(ps, m1), slope0=slope0(ps, m1), cos_pred_vs_kernel_pred=cosv(ps, p1),
                    pearson_pred_vs_kernel_pred=pear(ps, p1), within_script_pearson=pear(demean(ps), demean(m1)))
    # leave-one-script-out and leave-one-recipient-out at dose 1
    lo = [(cosv(p1[sid != s], m1[sid != s]), slope0(p1[sid != s], m1[sid != s])) for s in usid]
    lr_ = [(cosv(np.delete(p1, i), np.delete(m1, i)), slope0(np.delete(p1, i), np.delete(m1, i))) for i in range(len(m1))]
    o["loso_dose1"] = dict(cos=[min(x[0] for x in lo), max(x[0] for x in lo)], slope0=[min(x[1] for x in lo), max(x[1] for x in lo)])
    o["loro_dose1"] = dict(cos_min=min(x[0] for x in lr_), slope0=[min(x[1] for x in lr_), max(x[1] for x in lr_)])
    # per-recipient accuracy: |meas/pred - 1| at doses 0.1 and 1, among recipients with |pred at dose 1| >= 0.02
    big = np.abs(p1) >= 0.02
    o["per_recipient"] = dict(n_big=int(big.sum()), sign_agree_dose1=int((np.sign(p1) == np.sign(m1)).sum()))
    for s in [0.1, 1.0]:
        rr = M[f"dose{s:g}"] / (s * p1)
        o["per_recipient"][f"dose{s:g}"] = dict(within5_all=int((abs(rr - 1) <= 0.05).sum()),
                                                within5_big=int((abs(rr[big] - 1) <= 0.05).sum()),
                                                within10_big=int((abs(rr[big] - 1) <= 0.10).sum()),
                                                median_abs_ratio_dev=float(np.median(abs(rr - 1))))
    o["rel_med_err_by_dose"] = {k: v["med_abs_err"] / v["med_abs_meas"] for k, v in o["dose"].items()}
    # gradient norm spread
    gn = np.array([dmap[c]["gnorm"] for c in ctxs])
    o["gnorm"] = dict(min=float(gn.min()), median=float(np.median(gn)), max=float(gn.max()))
    # per-version means
    o["by_version"] = {v: dict(pred=float(p1[ver == v].mean()), meas=float(m1[ver == v].mean()), n=int((ver == v).sum()))
                       for v in sorted(set(ver))}
    res[ro] = o

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1)[:200])
