"""Blind recompute of X2 (PARENT) from gen_X2.jsonl + judged_X2.jsonl, frozen definitions of DECISIONS_X2.md §5-7."""
import json, math, sys
import numpy as np
from scipy.stats import chi2
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *

D = EX + "/X2"
man = json.load(open(D + "/jobs/manifest_X2.json"))
PERS = man["personas"]
SCR = json.load(open(D + "/scripts50.json"))["scripts"]
SI = {s: i for i, s in enumerate(SCR)}
gen = {r["key"]: r for r in jl(D + "/out/gen_X2.jsonl")}
assert set(gen) == set(man["expected"]), "gen keys != manifest"
cons = style_consensus(jl(D + "/out/judged_X2.jsonl"))

CATS = ["dom", "sub", "both", "neither"]  # dominant-only, other-only, both, neither
FAM = {"bc": ("bc_free_bc", "bc_free_cb"), "ps": ("ps_free_ps", "ps_free_sp")}
# order effect: dominant named first minus named second
ORDER = {"bc": ("bc_free_cb", "bc_free_bc"), "ps": ("ps_free_ps", "ps_free_sp")}
missing = []


def label(key):
    r = gen[key]
    fam = r["meta"]["family"]
    if fam == "bc":
        c = strict_cat((r.get("prefill") or "") + (r.get("text") or ""))
        return {"crow": "dom", "bee": "sub", "both": "both", "neither": "neither"}[c]
    if r.get("empty") or not (r.get("text") or "").strip():
        return "neither"
    if key not in cons:
        missing.append(key); return None
    p, s = cons[key]
    c = style_cat(p, s)
    return {"pirate": "dom", "shakes": "sub", "both": "both", "neither": "neither"}[c]


ARMS = ["bc_free_bc", "bc_free_cb", "ps_free_ps", "ps_free_sp", "ps_rule_A", "ps_rule_B"]
C = np.zeros((len(PERS), len(ARMS), len(SCR), 4))
for k, r in gen.items():
    m = r["meta"]
    lab = label(k)
    if lab is None:
        continue
    C[PERS.index(m["persona"]), ARMS.index(m["arm"]), SI[m["script_id"]], CATS.index(lab)] += 1
print("missing judge consensus:", len(missing))

rng = np.random.default_rng(0)
NB = 2000
W = np.stack([np.bincount(rng.integers(0, len(SCR), len(SCR)), minlength=len(SCR)) for _ in range(NB)])  # NB x S


def fam_stats(fam, Cw):
    """Cw: persona x arm x cat counts (already summed over scripts)."""
    a1, a2 = FAM[fam]
    ia1, ia2 = ARMS.index(a1), ARMS.index(a2)
    return Cw[:, ia1, :], Cw[:, ia2, :]


def analyse(fam):
    a1, a2 = FAM[fam]
    full = C.sum(2)  # P x A x cat
    pooled = full[:, ARMS.index(a1)] + full[:, ARMS.index(a2)]
    n = pooled.sum(1); one = pooled[:, 0] + pooled[:, 1]; styled = one + pooled[:, 2]
    comp = one / n
    est = [(comp[i] >= 0.30 and styled[i] >= 15) for i in range(len(PERS))]
    per = {}
    for i, p in enumerate(PERS):
        per[p] = dict(n=int(n[i]), styled=int(styled[i]), one=int(one[i]), dom=int(pooled[i, 0]), both=int(pooled[i, 2]),
                      compliance=round(float(comp[i]), 4), estimable=bool(est[i]),
                      P_dom=(float(pooled[i, 0] / one[i]) if one[i] else None),
                      by_order={a: dict(dom=int(full[i, ARMS.index(a), 0]), one=int(full[i, ARMS.index(a), 0] + full[i, ARMS.index(a), 1])) for a in (a1, a2)})
    E = [i for i in range(len(PERS)) if est[i]]
    gA = [PERS.index(p) for p in ASSIST if est[PERS.index(p)]]
    gN = [PERS.index(p) for p in NONASSIST if est[PERS.index(p)]]
    oF, oS = ORDER[fam]

    def quantities(Cw):  # Cw: P x A x cat
        pc = Cw[:, ARMS.index(a1)] + Cw[:, ARMS.index(a2)]
        def P(idx, src=pc):
            d = src[idx, 0].sum(); o = (src[idx, 0] + src[idx, 1]).sum()
            return d / o if o else np.nan
        pool = P(E)
        pa = P(gA); pn = P(gN)
        of = P(E, Cw[:, ARMS.index(oF)]); os_ = P(E, Cw[:, ARMS.index(oS)])
        return pool, pn - pa, of - os_, pa, pn

    pt = quantities(full)
    bs = np.array([quantities(np.tensordot(C, w, axes=([2], [0]))) for w in W])
    ci = [pct(bs[:, j]) for j in range(5)]
    # flat test: logistic dominant ~ order + persona vs ~ order on exactly-one items (estimable personas)
    X0, X1, y = [], [], []
    for i in E:
        for a in (a1, a2):
            ia = ARMS.index(a)
            for cat, yy in ((0, 1), (1, 0)):
                cnt = int(full[i, ia, cat])
                for _ in range(cnt):
                    ordv = 1.0 if a == oF else 0.0
                    X0.append([1.0, ordv]); y.append(yy)
                    row = [1.0, ordv] + [1.0 if i == j else 0.0 for j in E[1:]]
                    X1.append(row)
    _, l0 = fit_logit(X0, y); _, l1 = fit_logit(X1, y)
    lr = 2 * (l1 - l0); dfree = len(E) - 1; pval = float(chi2.sf(lr, dfree))
    pool, diff, ordeff, pa, pn = pt
    # verdict
    if len(E) < 8 or len(gA) < 3 or len(gN) < 3:
        verdict = "undetermined (compliance)"
    else:
        flat = abs(diff) < 0.15 and pval >= 0.05
        if pool >= 0.65 and ci[0][0] > 0.5 and abs(diff) < 0.15:
            verdict = "habit-level prior"
        elif diff >= 0.15 and ci[1][0] > 0:
            verdict = "congruence prior"
        elif 0.4 <= pool <= 0.6 and flat:
            verdict = "no prior"
        else:
            verdict = "unclassified"
    return dict(estimable=[PERS[i] for i in E], n_est=len(E), n_assist_est=len(gA), n_non_est=len(gN),
                pooled=float(pool), pooled_ci=ci[0], P_assist=float(pa), P_non=float(pn),
                group_diff=float(diff), group_diff_ci=ci[1], order_effect=float(ordeff), order_ci=ci[2],
                LR=float(lr), LR_df=dfree, LR_p=pval, verdict=verdict, per_persona=per,
                pooled_counts=dict(dom=int(sum(per[PERS[i]]["dom"] for i in E)), one=int(sum(per[PERS[i]]["one"] for i in E))))


# bee/crow judge-sample agreement (STRICT 3-class vs both-judge agreement)
def bc_agree():
    rows = jl(D + "/out/judged_bc_X2.jsonl")
    lab = {}
    for r in rows:
        if r.get("error"):
            continue
        lab[(r["key"], r["judge"])] = r.get("animal")
    keys = sorted({k for k, _ in lab})
    m = 0; tot = 0
    for k in keys:
        g = lab.get((k, "glm")); d = lab.get((k, "deepseek"))
        if g is None or d is None:
            continue
        tot += 1
        g3 = g if g in ("bee", "crow") else "none"; d3 = d if d in ("bee", "crow") else "none"
        s = strict_cat((gen[k].get("prefill") or "") + gen[k]["text"])
        s3 = {"bee": "bee", "crow": "crow", "neither": "none", "both": "BOTH"}[s]
        if g3 == d3 == s3:
            m += 1
    return dict(n=tot, match=m, agreement=m / tot if tot else None)


res = {"bc": analyse("bc"), "ps": analyse("ps"), "bc_judge_agreement": bc_agree(), "missing_consensus": len(missing)}
# rule arm b, r per persona (descriptive)
rule = {}
full = C.sum(2)
for i, p in enumerate(PERS):
    a = full[i, ARMS.index("ps_rule_A")]; b = full[i, ARMS.index("ps_rule_B")]
    nA = a[0] + a[1]; nB = b[0] + b[1]
    LA = logit_s(a[0], nA); LB = logit_s(b[0], nB)
    rule[p] = dict(kA=int(a[0]), nA=int(nA), kB=int(b[0]), nB=int(nB), b=(LA + LB) / 2, r=(LA - LB) / 2)
res["rule"] = rule
json.dump(res, open(EX + "/review/recompute/rc_x2.json", "w"), indent=1)
for f in ("bc", "ps"):
    x = res[f]
    print(f, "n_est", x["n_est"], "A/N", x["n_assist_est"], x["n_non_est"], "pooled %.4f" % x["pooled"], x["pooled_ci"], x["pooled_counts"],
          "| diff %.4f" % x["group_diff"], x["group_diff_ci"], "| order %.4f" % x["order_effect"], x["order_ci"],
          "| LR %.2f df %d p %.4g" % (x["LR"], x["LR_df"], x["LR_p"]), "|", x["verdict"])
    print("   P_assist %.4f P_non %.4f" % (x["P_assist"], x["P_non"]))
    print("   not estimable:", [p for p in PERS if p not in x["estimable"]])
print("bc agreement", res["bc_judge_agreement"])
