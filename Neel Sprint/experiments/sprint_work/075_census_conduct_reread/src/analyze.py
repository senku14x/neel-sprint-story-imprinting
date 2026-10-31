"""sw075 analysis: does the judged conduct of the census turns 1-2 explain the routing map, leaving the Axis nothing extra?

Population: the 271 non-animal census roles (predictors.json animal_role False).            [DECISIONS D2]
Outcome   : pooled R = 1/2 (R_raw_A + R_raw_B) per pair; hd = R_hd_rtx.json A_s0/B_s0, hs = R_hs.json hs_A/hs_B.
Conduct   : per role, mean over its judged contexts of the two-judge consensus (mean of GLM and DeepSeek logprob-weighted
            0-10 scores) for hostility, declining, helpfulness, warmth, register.                       [D3]
Models    : OLS with intercept on z-scored predictors:
            (i) conduct = the 5 fields; (ii) axis = P1; (iii) both = 5 fields + P1; (iv) disp/tone = P4_disp + P4_tone.
            Sensitivity (iv') = P5 (sw001's judged role similarity).
CV R^2    : leave-one-role-out, 1 - sum (y_i - yhat_{-i})^2 / sum (y_i - ybar)^2 (exact OLS LOO via the hat matrix).
            CI: 2,000 role resamples of the per-role LOO squared errors (no refit, so duplicated roles do not leak).
Partial   : Spearman partial of R on P1 given the 5 conduct fields: ranks of R and of P1 residualised on the ranks of the
            covariates (OLS with intercept), Spearman of the residuals (ideation-9's partial(), analyze2.py). CI: 2,000 role
            bootstrap resamples, percentiles 2.5/97.5. Seeded (numpy default_rng(75)).
Rule (frozen): "Own conduct explains the map" iff in BOTH hd and hs: CV R^2(conduct) >= CV R^2(axis) AND
            partial(axis | conduct) <= 0.10 AND its CI includes 0. "Persona carries more" in a pair iff
            partial >= 0.20 AND its CI excludes 0.                                                     [D5 for pair logic]
Usage:
  python analyze.py --judged /workspace/runs_executor/sw075/census_judged.jsonl --out /workspace/runs_executor/sw075/analysis
  python analyze.py --fake {exact,explains,persona,mixed} --out <dir>   (writes fake judge records first, then analyses them)
"""
import argparse, collections, json, os, random, sys

import numpy as np
from scipy.stats import rankdata, spearmanr

C3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C"
TURNS = "/workspace/runs_executor/sw075/census_turns.jsonl"
F = ["hostility", "declining", "helpfulness", "warmth", "register"]
JUDGES = ("glm", "deepseek")
NBOOT = 2000


# ------------------------------------------------------------------ data
def load_judged(path):
    """{key: {judge: rec}}; valid = no error and every <field>_w present; last valid record per (key, judge) wins (lib rule)."""
    by = {}
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "key" in r and "judge" in r and not r.get("error") and all(r.get(f + "_w") is not None for f in F):
            by.setdefault(r["key"], {})[r["judge"]] = r
    return by


def key_meta():
    return {r["key"]: (r["role"], r["script_id"]) for r in map(json.loads, open(TURNS))}


def role_conduct(by, meta, judges=JUDGES, scripts=None):
    """{role: {field: mean over contexts of the mean over `judges`}}, contexts judged by every judge in `judges`."""
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, d in by.items():
        if k not in meta or not all(j in d for j in judges):
            continue
        role, sid = meta[k]
        if scripts is not None and sid not in scripts:
            continue
        for f in F:
            acc[role][f].append(np.mean([d[j][f + "_w"] for j in judges]))
    return {r: {f: float(np.mean(v[f])) for f in F} | {"n": len(v[F[0]])} for r, v in acc.items()}


def load_core():
    pred = json.load(open(f"{C3}/predictors.json"))["by_persona"]
    roles = sorted(k.split("|", 1)[1] for k in pred if k.startswith("census|") and not pred[k]["animal_role"])
    Rhd = json.load(open(f"{C3}/R_hd_rtx.json")); Rhs = json.load(open(f"{C3}/R_hs.json"))
    R = {"hd": {r: 0.5 * (Rhd["A_s0"][r]["R_raw"] + Rhd["B_s0"][r]["R_raw"]) for r in roles},
         "hs": {r: 0.5 * (Rhs["hs_A"][r]["R_raw"] + Rhs["hs_B"][r]["R_raw"]) for r in roles}}
    Rsens = {"hd_A": {r: Rhd["A_s0"][r]["R_raw"] for r in roles}, "hd_B": {r: Rhd["B_s0"][r]["R_raw"] for r in roles},
             "hs_A": {r: Rhs["hs_A"][r]["R_raw"] for r in roles}, "hs_B": {r: Rhs["hs_B"][r]["R_raw"] for r in roles},
             "hd_rel": {r: 0.5 * (Rhd["A_s0"][r]["R_rel"] + Rhd["B_s0"][r]["R_rel"]) for r in roles},
             "hs_rel": {r: 0.5 * (Rhs["hs_A"][r]["R_rel"] + Rhs["hs_B"][r]["R_rel"]) for r in roles}}
    P = {p: {r: pred["census|" + r][p] for r in roles} for p in ("P1", "P4_disp", "P4_tone", "P5")}
    return roles, R, Rsens, P


# ------------------------------------------------------------------ statistics
def z(X):
    X = np.asarray(X, float)
    return (X - X.mean(0)) / X.std(0)


def loo_sq_err(y, X):
    """Per-observation LOO squared errors for OLS with intercept (exact, hat-matrix shortcut)."""
    A = np.column_stack([np.ones(len(y)), z(X)])
    H = A @ np.linalg.pinv(A.T @ A) @ A.T
    e = y - H @ y
    return (e / (1 - np.diag(H))) ** 2


def cv_r2(sq, y):
    return 1 - sq.sum() / ((y - y.mean()) ** 2).sum()


def loo_pred(y, X):
    A = np.column_stack([np.ones(len(y)), z(X)])
    H = A @ np.linalg.pinv(A.T @ A) @ A.T
    e = y - H @ y
    return y - e / (1 - np.diag(H))


def partial_s(y, x, Z):
    ry, rx = rankdata(y), rankdata(x)
    Z = np.asarray(Z, float)
    Z = Z[:, None] if Z.ndim == 1 else Z
    A = np.column_stack([rankdata(Z[:, i]) for i in range(Z.shape[1])] + [np.ones(len(y))])
    res = lambda v: v - A @ np.linalg.lstsq(A, v, rcond=None)[0]
    return float(spearmanr(res(ry), res(rx))[0])   # ideation-9's partial(): Spearman of the rank residuals


def boot_idx(n, seed):
    rng = np.random.default_rng(seed)
    return [rng.integers(0, n, n) for _ in range(NBOOT)]


def ci(v):
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def pair_analysis(y, Xc, P1, D, T, P5, idx):
    out = {}
    models = {"i_conduct": Xc, "ii_axis": P1[:, None], "iii_both": np.column_stack([Xc, P1]),
              "iv_disp_tone": np.column_stack([D, T]), "iv'_P5": P5[:, None]}
    sq = {m: loo_sq_err(y, X) for m, X in models.items()}
    sst = lambda b: ((y[b] - y[b].mean()) ** 2).sum()
    for m in models:
        bs = [1 - sq[m][b].sum() / sst(b) for b in idx]
        out[f"cvR2_{m}"] = dict(est=float(cv_r2(sq[m], y)), ci=ci(bs))
    d = [(sq["ii_axis"][b].sum() - sq["i_conduct"][b].sum()) / sst(b) for b in idx]
    out["cvR2_conduct_minus_axis"] = dict(est=out["cvR2_i_conduct"]["est"] - out["cvR2_ii_axis"]["est"], ci=ci(d))
    d3 = [(sq["i_conduct"][b].sum() - sq["iii_both"][b].sum()) / sst(b) for b in idx]
    out["cvR2_both_minus_conduct"] = dict(est=out["cvR2_iii_both"]["est"] - out["cvR2_i_conduct"]["est"], ci=ci(d3))
    p = partial_s(y, P1, Xc)
    out["partial_axis_given_conduct"] = dict(est=p, ci=ci([partial_s(y[b], P1[b], Xc[b]) for b in idx]))
    yc = loo_pred(y, Xc)   # conduct composite (LOO prediction) for the reverse partial
    out["partial_conduct_composite_given_axis"] = dict(est=partial_s(y, yc, P1), ci=ci([partial_s(y[b], yc[b], P1[b]) for b in idx]))
    out["partial_axis_given_disp_tone"] = dict(est=partial_s(y, P1, np.column_stack([D, T])),
                                               ci=ci([partial_s(y[b], P1[b], np.column_stack([D[b], T[b]])) for b in idx]))
    out["partial_axis_given_conduct_disp_tone"] = dict(est=partial_s(y, P1, np.column_stack([Xc, D, T])))
    out["rho_axis"] = float(spearmanr(y, P1)[0])
    out["rho_field"] = {f: float(spearmanr(y, Xc[:, i])[0]) for i, f in enumerate(F)}
    out["rho_axis_field"] = {f: float(spearmanr(P1, Xc[:, i])[0]) for i, f in enumerate(F)}
    return out


def rule(res):
    per = {}
    for pair in ("hd", "hs"):
        r = res[pair]; p = r["partial_axis_given_conduct"]
        expl = r["cvR2_i_conduct"]["est"] >= r["cvR2_ii_axis"]["est"] and p["est"] <= 0.10 and p["ci"][0] <= 0 <= p["ci"][1]
        more = p["est"] >= 0.20 and p["ci"][0] > 0
        per[pair] = dict(conduct_cvR2_ge_axis=r["cvR2_i_conduct"]["est"] >= r["cvR2_ii_axis"]["est"], partial_le_0p10=p["est"] <= 0.10,
                         partial_ci_includes_0=p["ci"][0] <= 0 <= p["ci"][1], explains=expl, persona_carries_more=more)
    if all(per[p]["explains"] for p in per):
        v = "Own conduct explains the map (both hd and hs)"
    elif all(per[p]["persona_carries_more"] for p in per):
        v = "Persona carries more (both hd and hs)"
    elif any(per[p]["persona_carries_more"] for p in per) or any(per[p]["explains"] for p in per):
        v = "Mixed: " + "; ".join(f"{p}: " + ("own conduct explains" if per[p]["explains"] else "persona carries more" if per[p]["persona_carries_more"]
                                               else "neither") for p in per)
    else:
        v = "Neither (intermediate): conduct does not explain the map and the Axis partial is not >= 0.20 with CI excluding 0"
    return dict(per_pair=per, verdict=v)


# ------------------------------------------------------------------ fake judge records (code test only)
def write_fake(kind, path, roles, R, P):
    meta = key_meta(); rng = np.random.default_rng(123)
    zr = lambda d: z(np.array([d[r] for r in roles]))
    sd_ctx, sd_j = (0.0, 0.0) if kind == "exact" else (0.3, 0.2)
    if kind in ("explains", "exact"):   # conduct carries R (hd via warmth, hs via register); "exact" = no context/judge noise
        lat = {"warmth": zr(R["hd"]), "register": zr(R["hs"])}
    elif kind == "persona":     # conduct unrelated to R or the Axis
        lat = {}
    else:                       # conduct = noisy Axis: conduct and Axis overlap, Axis keeps a partial
        lat = {"warmth": zr(P["P1"]) + rng.normal(0, 1.2, len(roles))}
    base = {r: {f: 5 + 1.5 * (lat[f][i] if f in lat else rng.normal()) for f in F} for i, r in enumerate(roles)}
    with open(path, "w") as fh:
        for k, (role, sid) in meta.items():
            if role not in base:
                continue
            ctx = {f: base[role][f] + rng.normal(0, sd_ctx) for f in F}
            for j in JUDGES:
                rec = dict(key=k, judge=j, error=None, fake=True)
                for f in F:
                    rec[f + "_w"] = float(ctx[f] + rng.normal(0, sd_j)) if kind == "exact" else float(np.clip(ctx[f] + rng.normal(0, sd_j), 0, 10))
                fh.write(json.dumps(rec) + "\n")


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--judged"); ap.add_argument("--fake"); ap.add_argument("--out", required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    roles, R, Rsens, P = load_core()
    if a.fake:
        a.judged = f"{a.out}/fake_judged_{a.fake}.jsonl"; write_fake(a.fake, a.judged, roles, R, P)
    meta = key_meta(); by = load_judged(a.judged)
    cond = role_conduct(by, meta)
    miss = [r for r in roles if r not in cond]
    assert not miss, f"{len(miss)} roles have no judged context, e.g. {miss[:5]}"
    n_ctx = {r: cond[r]["n"] for r in roles}
    Xc = np.array([[cond[r][f] for f in F] for r in roles])
    P1, D, T, P5 = (np.array([P[p][r] for r in roles]) for p in ("P1", "P4_disp", "P4_tone", "P5"))
    idx = boot_idx(len(roles), 75)
    res = dict(n_roles=len(roles), contexts_per_role=dict(min=min(n_ctx.values()), max=max(n_ctx.values()), total=sum(n_ctx.values())),
               judged_file=os.path.abspath(a.judged), fake=a.fake)
    for pair in ("hd", "hs"):
        res[pair] = pair_analysis(np.array([R[pair][r] for r in roles]), Xc, P1, D, T, P5, idx)
    res["rule"] = rule(res)
    # sensitivities (not the rule): each judge alone; parent-relative pooled R; per-assignment R; rank-transformed OLS
    sens = {}
    for j in JUDGES:
        cj = role_conduct(by, meta, judges=(j,)); Xj = np.array([[cj[r][f] for f in F] for r in roles])
        for pair in ("hd", "hs"):
            y = np.array([R[pair][r] for r in roles])
            sens[f"{j}_only|{pair}"] = dict(cvR2_conduct=float(cv_r2(loo_sq_err(y, Xj), y)), partial_axis_given_conduct=partial_s(y, P1, Xj))
    for nm, d in Rsens.items():
        y = np.array([d[r] for r in roles])
        sens[f"R_{nm}"] = dict(cvR2_conduct=float(cv_r2(loo_sq_err(y, Xc), y)), cvR2_axis=float(cv_r2(loo_sq_err(y, P1[:, None]), y)),
                               partial_axis_given_conduct=partial_s(y, P1, Xc))
    for pair in ("hd", "hs"):
        y = rankdata([R[pair][r] for r in roles]); Xr = np.column_stack([rankdata(Xc[:, i]) for i in range(len(F))])
        sens[f"rankOLS|{pair}"] = dict(cvR2_conduct=float(cv_r2(loo_sq_err(y, Xr), y)), cvR2_axis=float(cv_r2(loo_sq_err(y, rankdata(P1)[:, None]), y)))
    res["sensitivity"] = sens
    # reliability of role-level conduct: split-half over scripts (sorted script ids, alternating), Spearman-Brown
    scripts = sorted({sid for _, sid in meta.values()})
    h1 = role_conduct(by, meta, scripts=set(scripts[0::2])); h2 = role_conduct(by, meta, scripts=set(scripts[1::2]))
    both = [r for r in roles if r in h1 and r in h2]
    rel = {}
    for f in F:
        rr = float(np.corrcoef([h1[r][f] for r in both], [h2[r][f] for r in both])[0, 1]) if len(both) > 2 else None
        rel[f] = dict(split_half_r=rr, spearman_brown=(2 * rr / (1 + rr)) if rr is not None else None, n_roles=len(both))
    res["reliability"] = rel
    # beside, NOT the rule (DECISIONS D6): calibrated null for the Axis partial. If conduct were the whole cause and the judged
    # composite tracked it only as well as its split-half reliability allows (rho_m = sqrt(SB), an upper bound on validity), what
    # partial would the frozen statistic show? R reliability from the census log-odds rows (split-half over scripts, SB):
    # hd 0.971, hs 0.993 (src/rule_reach_sim.py header). 1,000 simulated worlds, seed 75.
    cal = {}
    for pair, relR in (("hd", 0.971), ("hs", 0.993)):
        y = np.array([R[pair][r] for r in roles]); A1 = np.column_stack([np.ones(len(y)), z(Xc)])
        beta = np.linalg.lstsq(A1, y, rcond=None)[0]
        comp = lambda h: np.column_stack([np.ones(len(both)), (np.array([[h[r][f] for f in F] for r in both]) - Xc.mean(0)) / Xc.std(0)]) @ beta
        sh = float(spearmanr(comp(h1), comp(h2))[0]) if len(both) > 2 else float("nan")
        sb = 2 * sh / (1 + sh); rm = float(np.sqrt(max(min(sb, 1.0), 0.0))); rR = np.sqrt(relR)
        a_ = min(spearmanr(y, P1)[0] / rR, 0.999); g = np.random.default_rng(75); n = len(roles); ps = []
        for _ in range(1000):
            c = g.normal(size=n); Ry = rR * c + np.sqrt(1 - rR**2) * g.normal(size=n)
            Px = a_ * c + np.sqrt(1 - a_**2) * g.normal(size=n); m = rm * c + np.sqrt(max(1 - rm**2, 0)) * g.normal(size=n)
            ps.append(partial_s(Ry, Px, m))
        obs = res[pair]["partial_axis_given_conduct"]["est"]
        cal[pair] = dict(composite_split_half_spearman=sh, composite_SB=sb, rho_m_upper=rm, null_median=float(np.median(ps)),
                         null_p95=float(np.percentile(ps, 95)), observed=obs, frac_null_ge_observed=float(np.mean(np.array(ps) >= obs)))
    res["calibrated_null_partial"] = cal
    # judge agreement at the context level
    ag = {}
    for f in F:
        g = [d["glm"][f + "_w"] for d in by.values() if all(j in d for j in JUDGES)]
        s = [d["deepseek"][f + "_w"] for d in by.values() if all(j in d for j in JUDGES)]
        ag[f] = dict(n=len(g), spearman=float(spearmanr(g, s)[0]), mean_abs_diff=float(np.mean(np.abs(np.array(g) - np.array(s)))),
                     both_gt5_or_both_le5=float(np.mean((np.array(g) > 5) == (np.array(s) > 5))))
    res["judge_agreement"] = ag
    # role table for a blind recompute / plots
    tab = [dict(role=r, R_hd=R["hd"][r], R_hs=R["hs"][r], P1=P["P1"][r], P4_disp=P["P4_disp"][r], P4_tone=P["P4_tone"][r], P5=P["P5"][r],
                n_contexts=n_ctx[r], **{f: cond[r][f] for f in F}) for r in roles]
    json.dump(tab, open(f"{a.out}/role_table.json", "w"), indent=1)
    json.dump(res, open(f"{a.out}/results.json", "w"), indent=1)
    # print
    print(f"== sw075 analysis ({'FAKE ' + a.fake if a.fake else 'real'}): {len(roles)} roles, contexts/role {res['contexts_per_role']}")
    for pair in ("hd", "hs"):
        r = res[pair]
        f2 = lambda d: f"{d['est']:+.3f} [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}]"
        print(f"-- {pair}: rho axis {r['rho_axis']:+.3f} | cvR2 conduct {f2(r['cvR2_i_conduct'])} axis {f2(r['cvR2_ii_axis'])} both {f2(r['cvR2_iii_both'])} "
              f"disp/tone {f2(r['cvR2_iv_disp_tone'])} | conduct-axis {f2(r['cvR2_conduct_minus_axis'])}")
        print(f"   partial axis|conduct {f2(r['partial_axis_given_conduct'])} | partial conduct|axis {f2(r['partial_conduct_composite_given_axis'])} "
              f"| partial axis|disp,tone {f2(r['partial_axis_given_disp_tone'])} (ideation-9: hd +0.53, hs +0.80)")
    for p, v in res["rule"]["per_pair"].items():
        print("   rule", p, v)
    print("FROZEN RULE VERDICT:", res["rule"]["verdict"])
    print("calibrated null (beside, not the rule):", {p: {k: round(v, 3) for k, v in d.items()} for p, d in res["calibrated_null_partial"].items()})
    print("reliability (Spearman-Brown):", {f: round(v["spearman_brown"], 3) if v["spearman_brown"] is not None else None for f, v in rel.items()})


if __name__ == "__main__":
    main()
