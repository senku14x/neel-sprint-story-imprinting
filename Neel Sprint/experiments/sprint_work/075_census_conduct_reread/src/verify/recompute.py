import json, collections, sys
import numpy as np

C = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/"
J = "/workspace/runs_executor/sw075/census_judged.jsonl"
F = ["hostility", "declining", "helpfulness", "warmth", "register"]
RKEY = sys.argv[1] if len(sys.argv) > 1 else "R_raw"
NB = 2000

# ---- judged conduct
last = {}
for l in open(J):
    r = json.loads(l)
    if r.get("error") is None and all(r.get(f + "_w") is not None for f in F):
        last[(r["key"], r["judge"])] = r
ctx = collections.defaultdict(dict)
for (k, j), r in last.items():
    ctx[k][j] = [r[f + "_w"] for f in F]
role_ctx = collections.defaultdict(list)
glm_ctx = collections.defaultdict(list); ds_ctx = collections.defaultdict(list)
n_one = 0
for k, d in ctx.items():
    role = k.split("|")[2]
    if len(d) != 2:
        n_one += 1
        continue
    role_ctx[role].append([(a + b) / 2 for a, b in zip(d["glm"], d["deepseek"])])
    glm_ctx[role].append(d["glm"]); ds_ctx[role].append(d["deepseek"])

pred = json.load(open(C + "predictors.json"))["by_persona"]
hd = json.load(open(C + "R_hd_rtx.json")); hs = json.load(open(C + "R_hs.json"))
roles = sorted(k.split("|", 1)[1] for k, v in pred.items()
               if k.startswith("census|") and not v["animal_role"])
roles = [r for r in roles if r in hd["A_s0"] and r in hs["hs_A"] and r in role_ctx]
n = len(roles)
X5 = np.array([np.mean(role_ctx[r], axis=0) for r in roles])
nctx = collections.Counter(len(role_ctx[r]) for r in roles)
P1 = np.array([pred["census|" + r]["P1"] for r in roles])
P4 = np.array([[pred["census|" + r]["P4_disp"], pred["census|" + r]["P4_tone"]] for r in roles])
R = {
    "hd": np.array([0.5 * (hd["A_s0"][r][RKEY] + hd["B_s0"][r][RKEY]) for r in roles]),
    "hs": np.array([0.5 * (hs["hs_A"][r][RKEY] + hs["hs_B"][r][RKEY]) for r in roles]),
}

def rank(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); rk = np.empty(len(x))
    xs = x[o]; i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]: j += 1
        rk[o[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return rk

def pear(a, b):
    a = a - a.mean(); b = b - b.mean(); return float(a @ b / np.sqrt((a @ a) * (b @ b)))

def spear(a, b): return pear(rank(a), rank(b))

def design(Z):
    return np.column_stack([np.ones(len(Z)), Z])

def fit(y, Z, w=None):
    X = design(Z)
    if w is None: w = np.ones(len(y))
    XtW = X.T * w
    beta = np.linalg.solve(XtW @ X, XtW @ y)
    return X, beta

def resid(y, Z, w=None):
    X, b = fit(y, Z, w); return y - X @ b

def cvr2(y, Z, w=None):
    """Leave-one-role-out CV R^2. With weights w (bootstrap counts), all copies of a role
    are held out together: e_loo = e / (1 - w h)."""
    if w is None: w = np.ones(len(y))
    X, b = fit(y, Z, w)
    e = y - X @ b
    A = np.linalg.inv((X.T * w) @ X)
    h = np.einsum("ij,jk,ik->i", X, A, X)
    eloo = e / (1 - w * h)
    ybar = (w @ y) / w.sum()
    return float(1 - (w @ eloo ** 2) / (w @ (y - ybar) ** 2))

def cvr2_brute(y, Z):
    X = design(Z); out = np.empty(len(y))
    for i in range(len(y)):
        m = np.ones(len(y), bool); m[i] = False
        b = np.linalg.lstsq(X[m], y[m], rcond=None)[0]; out[i] = X[i] @ b
    return float(1 - ((y - out) ** 2).sum() / ((y - y.mean()) ** 2).sum())

def partials(y, p1, X5, w=None):
    # (a) task: ranks of R, P1, in-sample model-(i) fit; partial corr of rank R & rank P1 given rank composite
    Xd, b = fit(y, X5, w); comp = Xd @ b
    ry, rp, rc = rank(y), rank(p1), rank(comp)
    a = wpear(resid(ry, rc[:, None], w), resid(rp, rc[:, None], w), w)
    # (b) partial Pearson of R and P1 given the 5 fields (raw)
    bb = wpear(resid(y, X5, w), resid(p1, X5, w), w)
    # (c) FILES.json variant: Spearman of residuals of rank(R), rank(P1) after OLS on ranks of 5 fields
    RX = np.column_stack([rank(X5[:, k]) for k in range(5)])
    c = wspear(resid(ry, RX, w), resid(rp, RX, w), w)
    return a, bb, c

def wpear(a, b, w=None):
    if w is None: return pear(a, b)
    ma = w @ a / w.sum(); mb = w @ b / w.sum(); a = a - ma; b = b - mb
    return float((w * a) @ b / np.sqrt(((w * a) @ a) * ((w * b) @ b)))

def wspear(a, b, w=None):
    return pear(rank(a), rank(b)) if w is None else None  # only used on expanded samples

def models(y):
    return {
        "i_conduct": X5, "ii_axis": P1[:, None], "iii_conduct+axis": np.column_stack([X5, P1]),
        "iv_P4disp+tone": P4,
    }

out = {"R_key": RKEY, "n_roles": n, "n_contexts_per_role": dict(nctx), "contexts_with_one_judge": n_one}
rng = np.random.default_rng(75)
boot_idx = [rng.integers(0, n, n) for _ in range(NB)]
for pair, y in R.items():
    res = {}
    ms = models(y)
    for name, Z in ms.items():
        res["cvR2_" + name] = cvr2(y, Z)
        X, b = fit(y, Z); yh = X @ b
        res["inR2_" + name] = float(1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    res["brute_check_cv_i"] = cvr2_brute(y, X5)
    pa, pb, pc = partials(y, P1, X5)
    res["partial_a_rankcomposite"] = pa; res["partial_b_pearson_5fields"] = pb; res["partial_c_rank5fields"] = pc
    res["spearman_R_P1"] = spear(y, P1)
    res["pearson_R_P1"] = pear(y, P1)
    res["spearman_field_R"] = {f: spear(X5[:, k], y) for k, f in enumerate(F)}
    res["spearman_R_composite_i"] = spear(y, fit(y, X5)[0] @ fit(y, X5)[1])
    # bootstrap
    B = collections.defaultdict(list)
    for idx in boot_idx:
        w = np.bincount(idx, minlength=n).astype(float)
        keep = w > 0
        yk, wk = y[keep], w[keep]
        for name, Z in ms.items():
            if name == "iv_P4disp+tone": continue
            B["cvR2_" + name].append(cvr2(yk, Z[keep], wk))
        B["cvR2_diff_i_minus_ii"].append(B["cvR2_i_conduct"][-1] - B["cvR2_ii_axis"][-1])
        # partials on the expanded resample (duplicates as rows)
        ye, p1e, X5e = y[idx], P1[idx], X5[idx]
        a, b_, c = partials(ye, p1e, X5e)
        B["partial_a_rankcomposite"].append(a); B["partial_b_pearson_5fields"].append(b_)
        B["partial_c_rank5fields"].append(c)
        B["spearman_R_P1"].append(spear(ye, p1e))
    res["CI95"] = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in B.items()}
    res["cvR2_diff_i_minus_ii"] = res["cvR2_i_conduct"] - res["cvR2_ii_axis"]
    out[pair] = res

def rule(res, key):
    lo, hi = res["CI95"][key]
    explains = res["cvR2_i_conduct"] >= res["cvR2_ii_axis"] and res[key] <= 0.10 and lo <= 0 <= hi
    persona = res[key] >= 0.20 and lo > 0
    return {"explains_this_pair": explains, "persona_carries_more": persona}
out["rule"] = {}
for key in ["partial_a_rankcomposite", "partial_b_pearson_5fields", "partial_c_rank5fields"]:
    r = {p: rule(out[p], key) for p in R}
    r["own_conduct_explains_both"] = all(r[p]["explains_this_pair"] for p in R)
    out["rule"][key] = r
# judge agreement (context level, per field)
gl = np.array([v for r in roles for v in glm_ctx[r]]); ds = np.array([v for r in roles for v in ds_ctx[r]])
out["judge_ctx_pearson"] = {f: pear(gl[:, k], ds[:, k]) for k, f in enumerate(F)}
out["field_means_role_level"] = {f: [float(X5[:, k].mean()), float(X5[:, k].std())] for k, f in enumerate(F)}
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps(out, indent=1))
