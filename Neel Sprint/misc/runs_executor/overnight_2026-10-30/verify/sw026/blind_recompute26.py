"""Blind recompute of sw026 headline quantities from raw jsonl files only.
Reads: full/{base,dots,meas}.jsonl, full/meta.json (displacement log), full/gates.json (G2 only).
Does not read analysis.md, summary.txt, results.json, analysis_agent/*, or src/analysis26*.py.
"""
import json, sys, collections
import numpy as np

RUN = "/workspace/runs_executor/sw026/full"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw026/blind_recompute26.json"
B = 10000
SEED = 20261031

def load(fn):
    return [json.loads(l) for l in open(f"{RUN}/{fn}")]

base, dots, meas = load("base.jsonl"), load("dots.jsonl"), load("meas.jsonl")
for rows in (base, dots, meas):
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate keys"

# index
D = {(r["readout"], r["ctx"]): r for r in dots}
F0 = {(r["readout"], r["ctx"]): r["f"] for r in base}
M = collections.defaultdict(dict)
for r in meas:
    k = (r["readout"], r["arm"])
    assert r["ctx"] not in M[k]
    M[k][r["ctx"]] = r

checks = {}
def ctxs(readout):
    c = sorted(ctx for (ro, ctx) in D if ro == readout)
    assert len(c) == 50, len(c)
    return c

def vec_p(readout, field, cs):
    return np.array([D[(readout, c)]["dots"][field] for c in cs], dtype=np.float64)

def vec_m(readout, arm, cs):
    assert set(M[(readout, arm)]) == set(cs), (readout, arm)
    return np.array([M[(readout, arm)][c]["delta"] for c in cs], dtype=np.float64)

def cos(p, m):
    return float(np.sum(p * m) / (np.linalg.norm(p) * np.linalg.norm(m)))
def slope0(p, m):
    return float(np.sum(p * m) / np.sum(p * p))
def pearson(p, m):
    return float(np.corrcoef(p, m)[0, 1])

# --- consistency checks on raw data
for ro in ("rand_animal", "heres_animal"):
    cs = ctxs(ro)
    # delta == f_arm - f_base
    mx = 0.0
    for (r2, arm), d in M.items():
        if r2 != ro: continue
        for c, r in d.items():
            mx = max(mx, abs((r["f"] - F0[(ro, c)]) - r["delta"]))
    checks[f"{ro}_max|delta-(f_arm-f_base)|"] = mx
    # f in grad pass (dots) vs base forward: re-prefill agreement
    checks[f"{ro}_max|f_dots-f_base|"] = max(abs(D[(ro, c)]["f"] - F0[(ro, c)]) for c in cs)
    # f == lp_bee - lp_crow in base
    checks[f"{ro}_max|f-(lpbee-lpcrow)|_base"] = max(abs(r["f"] - (r["lp_bee"] - r["lp_crow"])) for r in base if r["readout"] == ro)
    checks[f"{ro}_a_grad_max"] = max(D[(ro, c)]["a_grad_max"] for c in cs)
    pk, pa = vec_p(ro, "kernel", cs), vec_p(ro, "actual", cs)
    checks[f"{ro}_cos(kernel,actual)"] = cos(pk, pa)
    checks[f"{ro}_max|kernel-actual|"] = float(np.max(np.abs(pk - pa)))

def scripts_of(cs):
    return [c.split("|")[0] for c in cs]

def boot(readout, pfield, arm, scale=1.0, order="sorted"):
    cs = ctxs(readout)
    p = scale * vec_p(readout, pfield, cs)
    m = vec_m(readout, arm, cs)
    sc = scripts_of(cs)
    if order == "sorted":
        uniq = sorted(set(sc))
    else:  # order in meta.json
        uniq = json.load(open(f"{RUN}/meta.json"))["scripts"]
        assert set(uniq) == set(sc)
    idx = [np.array([i for i, s in enumerate(sc) if s == u]) for u in uniq]
    assert all(len(ix) == 5 for ix in idx) and len(idx) == 10
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, len(uniq), size=(B, len(uniq)))
    cs_b, sl_b = np.empty(B), np.empty(B)
    for b in range(B):
        ii = np.concatenate([idx[j] for j in draws[b]])
        pb, mb = p[ii], m[ii]
        cs_b[b] = cos(pb, mb); sl_b[b] = slope0(pb, mb)
    q = lambda x: [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]
    return dict(n=len(cs), n_clusters=len(uniq), cos=cos(p, m), cos_ci=q(cs_b),
                slope0=slope0(p, m), slope0_ci=q(sl_b), pearson=pearson(p, m),
                median_abs_m=float(np.median(np.abs(m))),
                max_abs_resid=float(np.max(np.abs(m - p))))

res = {"checks": checks}

# H1/H2 primary (both script orders, to show sensitivity of the CI to the ambiguity)
res["H1H2_primary_sorted"] = boot("rand_animal", "kernel", "dose1")
res["H1H2_primary_metaorder"] = boot("rand_animal", "kernel", "dose1", order="meta")

# H3 Pearson + permutation null
cs = ctxs("rand_animal")
p = vec_p("rand_animal", "kernel", cs); m = vec_m("rand_animal", "dose1", cs)
rng = np.random.default_rng(SEED)
nr, nc = np.empty(2000), np.empty(2000)
for i in range(2000):
    mp = m[rng.permutation(50)]
    nr[i] = pearson(p, mp); nc[i] = cos(p, mp)
res["H3"] = dict(n=50, pearson=pearson(p, m), null_p95_pearson=float(np.percentile(nr, 95)),
                 null_p95_cos=float(np.percentile(nc, 95)), cos=cos(p, m),
                 null_max_cos=float(nc.max()), null_max_pearson=float(nr.max()),
                 frac_null_cos_ge_obs=float(np.mean(nc >= cos(p, m))),
                 frac_null_r_ge_obs=float(np.mean(nr >= pearson(p, m))),
                 common_mode=dict(mean_p=float(p.mean()), sd_p=float(p.std()), mean_m=float(m.mean()), sd_m=float(m.std()),
                                  n_neg_m=int(np.sum(m < 0)), n_neg_p=int(np.sum(p < 0))))

# H4 noise clearance
res["H4"] = {}
for ro in ("rand_animal", "heres_animal"):
    cs = ctxs(ro)
    p = vec_p(ro, "kernel", cs)
    m1 = vec_m(ro, "dose1", cs); m0 = vec_m(ro, "dose0.001", cs)
    floor = float(np.median(np.abs(m0 - 0.001 * p)))
    res["H4"][ro] = dict(n=50, median_abs_dose1=float(np.median(np.abs(m1))), noise_floor=floor,
                         clearance=float(np.median(np.abs(m1)) / floor),
                         floor_max=float(np.max(np.abs(m0 - 0.001 * p))),
                         median_abs_dose0001=float(np.median(np.abs(m0))))

# H5 dose ladder (prediction scaled by s)
res["H5_ladder"] = {}
for ro in ("rand_animal", "heres_animal"):
    res["H5_ladder"][ro] = {}
    for s in (0.001, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0):
        arm = f"dose{s:g}"
        r = boot(ro, "kernel", arm, scale=s)
        r["passes_rule"] = bool(r["cos"] >= 0.95 and 0.8 <= r["slope0"] <= 1.25)
        res["H5_ladder"][ro][arm] = r
    # neg1 and central difference
    cs = ctxs(ro); p = vec_p(ro, "kernel", cs)
    m1 = vec_m(ro, "dose1", cs); mn = vec_m(ro, "neg1", cs)
    cd = (m1 - mn) / 2
    res["H5_ladder"][ro]["neg1"] = dict(cos=cos(-p, mn), slope0=slope0(-p, mn))
    res["H5_ladder"][ro]["central_diff"] = dict(cos=cos(p, cd), slope0=slope0(p, cd))

# H6 random-sign steps
meta = json.load(open(f"{RUN}/meta.json"))
res["H6"] = {}
for ro in ("rand_animal", "heres_animal"):
    cs = ctxs(ro); pk = vec_p(ro, "kernel", cs); m1 = vec_m(ro, "dose1", cs)
    rows = {}
    for j in range(5):
        pr = vec_p(ro, f"rand{j}", cs); mr = vec_m(ro, f"rand{j}", cs)
        rows[f"rand{j}"] = dict(own_cos=cos(pr, mr), own_slope0=slope0(pr, mr), own_pearson=pearson(pr, mr),
                               cross_cos=cos(pk, mr), effect_ratio=float(np.median(np.abs(mr)) / np.median(np.abs(m1))),
                               cos_pred_rand_vs_kernel=cos(pr, pk),
                               disp_ratio_meta=meta["displacement_dB"][f"rand{j}"]["ratio"])
    rows["max_abs_cross_cos"] = max(abs(v["cross_cos"]) for v in rows.values())
    rows["min_own_cos"] = min(v["own_cos"] for k, v in rows.items() if k.startswith("rand"))
    rows["median_abs_cross_cos"] = float(np.median([abs(v["cross_cos"]) for k, v in rows.items() if k.startswith("rand")]))
    res["H6"][ro] = rows

# H7 SGD
res["H7"] = {}
for ro in ("rand_animal", "heres_animal"):
    cs = ctxs(ro); ps = vec_p(ro, "sgd", cs); pk = vec_p(ro, "kernel", cs); m1 = vec_m(ro, "dose1", cs)
    res["H7"][ro] = dict(n=50, cos=cos(ps, m1), pearson=pearson(ps, m1), slope0=slope0(ps, m1),
                         cos_sgd_vs_adam=cos(ps, pk), pearson_sgd_vs_adam=pearson(ps, pk),
                         passes_rule=bool(cos(ps, m1) >= 0.95 and 0.8 <= slope0(ps, m1) <= 1.25))

# H8 secondary readout
res["H8_sorted"] = boot("heres_animal", "kernel", "dose1")
res["H8_metaorder"] = boot("heres_animal", "kernel", "dose1", order="meta")

# G2 from gates.json (only this field)
try:
    g = json.load(open(f"{RUN}/gates.json"))
    res["gates_G2"] = g.get("G2", {k: v for k, v in g.items() if "G2" in k})
except Exception as e:
    res["gates_G2"] = str(e)

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
