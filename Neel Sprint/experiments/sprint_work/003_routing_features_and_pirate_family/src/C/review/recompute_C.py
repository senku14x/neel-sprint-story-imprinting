"""Independent recomputation of sw003 Part C from raw rows (verifier; does not read analyze_C.py / compute_R.py / their outputs).
Definitions (resolved from sw001 analyze_p1.py docstring + lo_table, common_sw.py, sw001 decisions D5):
  LO per row = lp[" bee"=35997] - lp[" crow"=9000]  (lp renormalised over {bee, bees, crow}; " bees" excluded, sw001 primary)
  R(model, role) = mean over the role's scripts (census, trig, b1) of s*LO, s=+1 for assignment A (helper bee), -1 for B (helper crow)
  population = census roles minus ANIMAL_ROLES (hive, naturalist, veterinarian)
Run: OMP_NUM_THREADS=8 taskset -c 104-111 python3 recompute_C.py"""
import json, os, sys
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import rankdata, spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.dirname(HERE)
CENSUS = f"{C}/out/lo_census.jsonl"
PARENT = "/workspace/runs_executor/sw001_box2/p1/lo.jsonl"
BEE, BEES, CROW = "35997", "38152", "9000"
SIGN = {"hs_A": 1, "A_s0": 1, "hs_B": -1, "B_s0": -1}
ASSIGN = {"hs_A": "A", "A_s0": "A", "hs_B": "B", "B_s0": "B"}
ANIMAL = {"hive", "naturalist", "veterinarian"}
NB = 2000
PREDS = ["P1", "P4_disp", "P4_tone", "P5", "P5s"]

def load(path, models=None):
    rows, ids = defaultdict(lambda: defaultdict(dict)), Counter()
    lse = []
    for l in open(path):
        r = json.loads(l)
        p = r["id"].split("|")
        if p[1] != "census" or p[3] != "trig" or p[5] != "b1":
            continue
        if models and r["model"] not in models:
            continue
        ids[(r["model"], r["id"])] += 1
        lp = r["lp"]
        lse.append(float(np.logaddexp.reduce([lp[BEE], lp[BEES], lp[CROW]])))
        rows[r["model"]][p[2]][p[4]] = lp[BEE] - lp[CROW]
    return rows, ids, np.array(lse)

def sp(x, y):
    return float(spearmanr(x, y).correlation)

def z(v):
    return (v - v.mean()) / v.std()

def partial_rank(x, y, Z):
    rx, ry = rankdata(x), rankdata(y)
    X = np.column_stack([np.ones(len(x))] + [rankdata(c) for c in Z])
    res = lambda a: a - X @ np.linalg.lstsq(X, a, rcond=None)[0]
    return float(np.corrcoef(res(rx), res(ry))[0, 1])

def interaction(R, tone, disp):
    y, t, d = z(rankdata(R)), z(rankdata(tone)), z(rankdata(disp))
    X0 = np.column_stack([np.ones(len(y)), t, d])
    X1 = np.column_stack([X0, t * d])
    b0 = np.linalg.lstsq(X0, y, rcond=None)[0]; b1 = np.linalg.lstsq(X1, y, rcond=None)[0]
    r2 = lambda X, b: 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    X1s = np.column_stack([X0, z(t * d)])   # product itself standardised
    b1s = np.linalg.lstsq(X1s, y, rcond=None)[0]
    return dict(beta_int=float(b1[3]), beta_int_stdprod=float(b1s[3]), beta_tone=float(b1[1]), beta_disp=float(b1[2]),
                r2_main=float(r2(X0, b0)), r2_full=float(r2(X1, b1)), r2_gain=float(r2(X1, b1) - r2(X0, b0)))

def pct(R):
    return (rankdata(R) - 0.5) / len(R) * 100

def curt_shift(R, mask):
    q = pct(R)
    return float(q[mask].mean() - q[~mask].mean())

def ci(v):
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]

def per_model(R, P, mask, rng):
    n = len(R)
    out = {"n_roles": n, "rho": {}, "ci": {}}
    for p in PREDS:
        out["rho"][p] = sp(R, P[p])
    out["tone_minus_disp"] = out["rho"]["P4_tone"] - out["rho"]["P4_disp"]
    out["partial_P5s_given_P1_disp_tone"] = partial_rank(P["P5s"], R, [P["P1"], P["P4_disp"], P["P4_tone"]])
    out["interaction"] = interaction(R, P["P4_tone"], P["P4_disp"])
    out["curt_helpful_shift_pct"] = curt_shift(R, mask)
    out["curt_helpful_n"] = int(mask.sum())
    bs = defaultdict(list)
    ix_all = rng.integers(0, n, size=(NB, n))
    for ix in ix_all:
        Rb = R[ix]
        rr = {p: sp(Rb, P[p][ix]) for p in PREDS}
        for p in PREDS:
            bs[p].append(rr[p])
        bs["gap"].append(rr["P4_tone"] - rr["P4_disp"])
        bs["partial"].append(partial_rank(P["P5s"][ix], Rb, [P["P1"][ix], P["P4_disp"][ix], P["P4_tone"][ix]]))
        it = interaction(Rb, P["P4_tone"][ix], P["P4_disp"][ix])
        bs["beta_int"].append(it["beta_int"]); bs["r2_gain"].append(it["r2_gain"])
    # curt shift: stratified bootstrap (resample within list and within rest; percentile ranks recomputed on the resample)
    a, b = np.where(mask)[0], np.where(~mask)[0]
    for _ in range(NB):
        ia, ib = rng.choice(a, len(a)), rng.choice(b, len(b))
        Rb = np.concatenate([R[ia], R[ib]]); mb = np.r_[np.ones(len(a), bool), np.zeros(len(b), bool)]
        bs["curt"].append(curt_shift(Rb, mb))
    for p in PREDS:
        out["ci"][p] = ci(bs[p])
    out["tone_minus_disp_ci"] = ci(bs["gap"])
    out["partial_P5s_ci"] = ci(bs["partial"])
    out["interaction"]["beta_int_ci"] = ci(bs["beta_int"]); out["interaction"]["r2_gain_ci"] = ci(bs["r2_gain"])
    out["curt_helpful_shift_ci"] = ci(bs["curt"])
    return out

def main():
    rng = np.random.default_rng(20261027)
    rows, ids, lse = load(CENSUS)
    integ = {"models": sorted(rows), "total_rows_file": sum(1 for _ in open(CENSUS)),
             "duplicate_ids": sum(1 for v in ids.values() if v > 1),
             "logsumexp_bee_bees_crow": [float(lse.min()), float(lse.max())]}
    allroles = sorted(set().union(*[set(rows[m]) for m in rows]))
    integ["n_roles_total"] = len(allroles)
    integ["per_model"] = {m: {"rows": sum(len(v) for v in rows[m].values()), "roles": len(rows[m]),
                              "roles_not_20": {k: len(v) for k, v in rows[m].items() if len(v) != 20},
                              "missing_roles": sorted(set(allroles) - set(rows[m]))} for m in rows}
    scripts = {m: {k: sorted(v) for k, v in rows[m].items()} for m in rows}
    ref = scripts[sorted(rows)[0]]
    integ["script_sets_identical_across_models"] = all(scripts[m] == ref for m in rows)
    pred = json.load(open(f"{C}/predictors.json"))["by_persona"]
    curt = set(json.load(open(f"{C}/curt_helpful_roles.json"))["roles"])
    excl = sorted(r for r in allroles if r in ANIMAL)
    flag = sorted(k[7:] for k, v in pred.items() if k.startswith("census|") and v.get("animal_role"))
    roles = [r for r in allroles if r not in ANIMAL]
    integ.update(excluded_animal_roles=excl, predictors_animal_flag=flag, population=len(roles),
                 curt_list_n=len(curt), curt_list_in_population=len(curt & set(roles)))
    P = {p: np.array([pred[f"census|{r}"][p] for r in roles]) for p in PREDS}
    # curt-list rule check (recompute from predictors)
    mt, md = np.median(P["P4_tone"]), np.median(P["P4_disp"])
    rule = {r for r, t, d in zip(roles, P["P4_tone"], P["P4_disp"]) if t < mt and d >= md}
    integ["curt_list_matches_rule"] = rule == curt
    mask = np.array([r in curt for r in roles])
    Rm = {m: np.array([SIGN[m] * np.mean(list(rows[m][r].values())) for r in roles]) for m in rows}
    res = {"integrity": integ, "definitions": __doc__, "per_model": {}}
    for m in ["hs_A", "hs_B", "A_s0", "B_s0"]:
        res["per_model"][m] = per_model(Rm[m], P, mask, rng)
        res["per_model"][m]["R_mean"] = float(Rm[m].mean())
    # cross-model within assignment
    cross = {}
    n = len(roles)
    for hs, hd in (("hs_A", "A_s0"), ("hs_B", "B_s0")):
        a, b = Rm[hs], Rm[hd]
        d = dict(rho=sp(a, b))
        g = lambda R, ix: sp(R[ix], P["P4_tone"][ix]) - sp(R[ix], P["P4_disp"][ix])
        full = np.arange(n)
        d["gap_hs_minus_hd"] = g(a, full) - g(b, full)
        d["curt_hs_minus_hd"] = curt_shift(a, mask) - curt_shift(b, mask)
        bs = defaultdict(list)
        for ix in rng.integers(0, n, size=(NB, n)):
            bs["rho"].append(sp(a[ix], b[ix])); bs["gap"].append(g(a, ix) - g(b, ix))
        ia_, ib_ = np.where(mask)[0], np.where(~mask)[0]
        for _ in range(NB):
            ix = np.concatenate([rng.choice(ia_, len(ia_)), rng.choice(ib_, len(ib_))]); mb = mask[ix]
            bs["curt"].append(curt_shift(a[ix], mb) - curt_shift(b[ix], mb))
        d["rho_ci"], d["gap_hs_minus_hd_ci"], d["curt_hs_minus_hd_ci"] = ci(bs["rho"]), ci(bs["gap"]), ci(bs["curt"])
        cross[hs[-1]] = d
    res["cross_model"] = cross
    # R_rel sensitivity: per-script LO_model - LO_parent (parent = sw001 H200 rows), signed to the helper
    prow, pids, _ = load(PARENT, models={"parent"})
    par = prow["parent"]
    integ["parent_rows"] = sum(len(v) for v in par.values()); integ["parent_roles"] = len(par)
    rel = {}
    for m in ["hs_A", "hs_B", "A_s0", "B_s0"]:
        Rr = []
        for r in roles:
            s = sorted(set(rows[m][r]) & set(par[r]))
            Rr.append(SIGN[m] * np.mean([rows[m][r][k] - par[r][k] for k in s]))
        Rr = np.array(Rr)
        rel[m] = {p: sp(Rr, P[p]) for p in PREDS}
        rel[m]["tone_minus_disp"] = rel[m]["P4_tone"] - rel[m]["P4_disp"]
        rel[m]["partial_P5s"] = partial_rank(P["P5s"], Rr, [P["P1"], P["P4_disp"], P["P4_tone"]])
        rel[m]["curt_shift"] = curt_shift(Rr, mask)
    res["R_rel_sensitivity_point_estimates"] = rel
    json.dump(res, open(f"{HERE}/recompute_C.json", "w"), indent=1)
    print(json.dumps(integ, indent=1))
    for m, o in res["per_model"].items():
        print(m, {p: round(o["rho"][p], 3) for p in PREDS}, "gap", round(o["tone_minus_disp"], 3), [round(x, 3) for x in o["tone_minus_disp_ci"]],
              "partial", round(o["partial_P5s_given_P1_disp_tone"], 3), [round(x, 3) for x in o["partial_P5s_ci"]],
              "int", round(o["interaction"]["beta_int"], 3), [round(x, 3) for x in o["interaction"]["beta_int_ci"]], "r2gain", round(o["interaction"]["r2_gain"], 4),
              "curt", round(o["curt_helpful_shift_pct"], 2), [round(x, 2) for x in o["curt_helpful_shift_ci"]])
    print(json.dumps(cross, indent=1))
    print(json.dumps(rel, indent=1))

if __name__ == "__main__":
    main()
