"""X2 (PARENT) analysis. /root/venvs/si/bin/python analyze_X2.py [--out-dir DIR] [--org-b-pirate F] [--org-b-beecrow F]
Definitions frozen in DECISIONS_X2.md §5-§7. Expected items come from jobs/manifest_X2.json; missing generations or judgments
are counted and reported, never silently dropped. --out-dir (default out/) is where gen_X2.jsonl / judged_X2*.jsonl /
judged_bc_X2.jsonl are read and X2_results.json is written (the synthetic known-answer test points it at a temp dir).
--org-b-pirate / --org-b-beecrow: JSON {persona: b} from AUDIT-2 (X0) / PANEL (X3). Without --org-b-pirate the AUDIT-2 pirate
b(p) is computed here from sw004 T1 raw outputs (labelled 'computed_here_from_T1')."""
import argparse, json, os, sys
from collections import defaultdict
import numpy as np

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import common_x25 as X  # noqa: E402
import stats_x25 as S  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out-dir", default=f"{H}/out"); ap.add_argument("--org-b-pirate"); ap.add_argument("--org-b-beecrow")
ap.add_argument("--no-t1", action="store_true", help="skip the T1-derived pirate b(p) (synthetic tests)")
a = ap.parse_args()
O = a.out_dir
MAN = json.load(open(f"{H}/jobs/manifest_X2.json"))
PERS = MAN["personas"]; SC = MAN["scripts"]; NP, NS = len(PERS), len(SC)
pi = {p: i for i, p in enumerate(PERS)}; si = {s: i for i, s in enumerate(SC)}
EXPECTED = set(MAN["expected"])
META = {}
for l in open(f"{H}/jobs/jobs_X2.jsonl"):
    j = json.loads(l); META[j["key"]] = j["meta"]
B = S.boot_idx(NS)
R = dict(definitions="DECISIONS_X2.md §5-§7", n_expected=len(EXPECTED), missing={})

# ------------------------------------------------------------------ load
gen = {}
for r in X.jsonl(f"{O}/gen_X2.jsonl"):
    if not r.get("error") and r.get("finish") in ("stop", "length") and r["key"] in EXPECTED:
        gen[r["key"]] = r
R["missing"]["generation"] = len(EXPECTED - set(gen))
jud = defaultdict(dict)
for fn in ("judged_X2.jsonl", "judged_X2_retry.jsonl"):
    for r in X.jsonl(f"{O}/{fn}"):
        if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
            jud[r["key"]].setdefault(r["judge"], (r["pirate_w"], r["shakespeare_w"]))
bcj = defaultdict(dict)
for r in X.jsonl(f"{O}/judged_bc_X2.jsonl"):
    if not r.get("error") and r.get("animal"):
        bcj[r["key"]].setdefault(r["judge"], r["animal"])

CODE = {"neither": 0, "dom": 1, "other": 2, "both": 3}


def code_ps(k, thr=5.0, judge=None):
    """pirate family: 1 = pirate-only (dominant), 2 = Shakespeare-only, 3 = both, 0 = neither, -1 = missing."""
    if k not in gen:
        return -1
    if gen[k].get("empty") or not (gen[k].get("text") or "").strip():
        return 0
    d = jud.get(k, {})
    if judge:
        if judge not in d:
            return -1
        pw, sw = d[judge]
    else:
        if not all(j in d for j in ("glm", "deepseek")):
            return -1
        pw = (d["glm"][0] + d["deepseek"][0]) / 2; sw = (d["glm"][1] + d["deepseek"][1]) / 2
    lab = X.style_label(pw, sw, thr)
    return dict(pirate=1, shakespeare=2, both=3, neither=0)[lab]


def code_bc(k, source="strict"):
    """bee/crow: 1 = crow-only (dominant), 2 = bee-only, 3 = both, 0 = neither, -1 = missing."""
    if k not in gen:
        return -1
    if source == "strict":
        lab = X.strict_label((gen[k].get("prefill") or "") + (gen[k].get("text") or ""))
    else:   # judge consensus (3-class); judges disagree -> missing
        d = bcj.get(k, {})
        if not all(j in d for j in ("glm", "deepseek")):
            return -1
        t = lambda x: "neither" if x in ("none", "other") else x
        if t(d["glm"]) != t(d["deepseek"]):
            return -1
        lab = t(d["glm"])
    return dict(crow=1, bee=2, both=3, neither=0)[lab]


def grid(arm, fn, exclude_short=False, **kw):
    g = np.full((NP, NS), -1)
    for p in PERS:
        for s in SC:
            k = f"X2|{arm}|{p}|{s}"
            if exclude_short and META[k]["hist_short"]:
                continue
            g[pi[p], si[s]] = fn(k, **kw)
    return g


def counts(grids, idx=None):
    """Sum over arms (list of grids) and scripts (idx: (nb, NS) bootstrap draws or None). Returns dict of (NP,) or (NP, nb)."""
    out = {}
    for name, cond in (("n", lambda g: g >= 0), ("styled", lambda g: g >= 1), ("one", lambda g: (g == 1) | (g == 2)),
                       ("dom", lambda g: g == 1), ("both", lambda g: g == 3), ("other", lambda g: g == 2)):
        tot = 0
        for g in grids:
            m = cond(g).astype(float)
            tot = tot + (m.sum(1) if idx is None else m[:, idx].sum(-1))
        out[name] = tot
    return out


def summarize_family(fam, grids_by_arm):
    arms = X.FREE_ARMS[fam]
    G = [grids_by_arm[x] for x in arms]
    c = counts(G); cb = counts(G, B)
    comp = S.ratio(c["one"], c["n"])
    est = (comp >= 0.30) & (c["styled"] >= 15)
    per = {}
    for p in PERS:
        i = pi[p]
        e = dict(group=X.GROUP[p], n=int(c["n"][i]), styled=int(c["styled"][i]), exactly_one=int(c["one"][i]), dom=int(c["dom"][i]),
                 both=int(c["both"][i]), compliance=float(comp[i]) if np.isfinite(comp[i]) else None, estimable=bool(est[i]))
        for x in arms:
            cx = counts([grids_by_arm[x]])
            e[f"P_dom_{x}"] = float(S.ratio(cx["dom"][i], cx["one"][i])) if cx["one"][i] else None
            e[f"n_one_{x}"] = int(cx["one"][i])
        if est[i]:
            e["P_dom"] = float(c["dom"][i] / c["one"][i])
            e["P_dom_CI"] = S.ci(S.ratio(cb["dom"][i], cb["one"][i]))
            e["logit_P_dom"] = float(S.logit_s(c["dom"][i], c["one"][i]))
        per[p] = e
    res = dict(per_persona=per, n_estimable=int(est.sum()), estimable=[p for p in PERS if est[pi[p]]])

    def pooled(cc, mask):
        return S.ratio((cc["dom"] * mask[:, None] if cc["dom"].ndim == 2 else cc["dom"] * mask).sum(0),
                       (cc["one"] * mask[:, None] if cc["one"].ndim == 2 else cc["one"] * mask).sum(0))
    mall = est.astype(float)
    ma = np.array([X.GROUP[p] == "assistant_like" for p in PERS]) & est
    mn = np.array([X.GROUP[p] == "non_assistant" for p in PERS]) & est
    res["pooled_P_dom"] = float(pooled(c, mall)); res["pooled_P_dom_CI"] = S.ci(pooled(cb, mall))
    pm = np.array([per[p].get("P_dom", np.nan) for p in PERS], float)
    res["persona_mean_P_dom"] = float(np.nanmean(pm[est])) if est.any() else None
    res["n_est_assistant_like"], res["n_est_non_assistant"] = int(ma.sum()), int(mn.sum())
    if ma.sum() >= 3 and mn.sum() >= 3:
        ga, gn = pooled(c, ma.astype(float)), pooled(c, mn.astype(float))
        gab, gnb = pooled(cb, ma.astype(float)), pooled(cb, mn.astype(float))
        res["P_dom_assistant_like"], res["P_dom_non_assistant"] = float(ga), float(gn)
        res["group_diff"] = float(gn - ga); res["group_diff_CI"] = S.ci(gnb - gab)
    else:
        res["group_diff"] = None
    # order effect (dominant named first - named second), estimable personas
    cf, cs = counts([grids_by_arm[X.DOM_FIRST[fam]]]), counts([grids_by_arm[X.DOM_SECOND[fam]]])
    cfb, csb = counts([grids_by_arm[X.DOM_FIRST[fam]]], B), counts([grids_by_arm[X.DOM_SECOND[fam]]], B)
    res["P_dom_dom_named_first"] = float(pooled(cf, mall)); res["P_dom_dom_named_second"] = float(pooled(cs, mall))
    res["order_effect"] = res["P_dom_dom_named_first"] - res["P_dom_dom_named_second"]
    res["order_effect_CI"] = S.ci(pooled(cfb, mall) - pooled(csb, mall))
    # homogeneity: G-test across estimable personas (orders pooled) + logistic LR with order covariate
    res["homogeneity_G"] = S.g_test(c["dom"][est], c["one"][est])
    rows = []
    for x in arms:
        g = grids_by_arm[x]
        for p in res["estimable"]:
            for s in SC:
                v = g[pi[p], si[s]]
                if v in (1, 2):
                    rows.append((int(v == 1), int(x == X.DOM_FIRST[fam]), p, X.topic(s)))
    if len(rows) > 20 and len(res["estimable"]) >= 2:
        y = np.array([r[0] for r in rows]); order = np.array([r[1] for r in rows])
        P_ = res["estimable"]; T_ = sorted({r[3] for r in rows})
        Xp = np.array([[r[2] == p for p in P_[1:]] for r in rows], float)
        Xt = np.array([[r[3] == t for t in T_[1:]] for r in rows], float)
        one = np.ones((len(rows), 1))
        res["homogeneity_LR_order_adjusted"] = S.lr_test(np.hstack([one, order[:, None], Xp]), np.hstack([one, order[:, None]]), y)
        res["topic_LR"] = S.lr_test(np.hstack([one, order[:, None], Xp, Xt]), np.hstack([one, order[:, None], Xp]), y)
        bt, _ = S.logistic(np.hstack([one, order[:, None], Xp, Xt]), y)
        res["topic_coefs_vs_" + T_[0]] = {t: float(bt[2 + len(P_) - 1 + i]) for i, t in enumerate(T_[1:])}
        tp = {t: float(np.mean([r[0] for r in rows if r[3] == t])) for t in T_}
        res["P_dom_by_topic"] = tp; res["n_one_by_topic"] = {t: sum(r[3] == t for r in rows) for t in T_}
        res["topic_balanced_P_dom"] = float(np.mean(list(tp.values())))
    hp = (res.get("homogeneity_LR_order_adjusted") or res["homogeneity_G"])["p"]     # DECISIONS_X2 §6: order-adjusted LR
    res["homogeneity_p_used_for_flat"] = hp
    flat = res.get("group_diff") is not None and abs(res["group_diff"]) < 0.15 and (hp or 0) >= 0.05
    res["flat"] = bool(flat)
    res["verdict"] = verdict(res)
    return res


def verdict(r):
    if r["n_estimable"] < 8 or r.get("group_diff") is None:
        return "undetermined (compliance)"
    pl, plci, d, dci = r["pooled_P_dom"], r["pooled_P_dom_CI"], r["group_diff"], r["group_diff_CI"]
    if pl >= 0.65 and plci and plci[0] > 0.5 and abs(d) < 0.15:
        return "habit-level prior"
    if d >= 0.15 and dci and dci[0] > 0:
        return "congruence prior"
    if 0.4 <= pl <= 0.6 and r["flat"]:
        return "no prior"
    return "unclassified"


def rule_arm(grids_by_arm, smooth=0.5):
    gA, gB = grids_by_arm["ps_rule_A"], grids_by_arm["ps_rule_B"]
    cA, cB, cAb, cBb = counts([gA]), counts([gB]), counts([gA], B), counts([gB], B)
    out = {}
    okA = (S.ratio(cA["one"], cA["n"]) >= 0.30) & (cA["styled"] >= 15)
    okB = (S.ratio(cB["one"], cB["n"]) >= 0.30) & (cB["styled"] >= 15)
    for p in PERS:
        i = pi[p]
        e = dict(group=X.GROUP[p], A=dict(n=int(cA["n"][i]), styled=int(cA["styled"][i]), one=int(cA["one"][i]), pirate=int(cA["dom"][i]), both=int(cA["both"][i])),
                 B=dict(n=int(cB["n"][i]), styled=int(cB["styled"][i]), one=int(cB["one"][i]), pirate=int(cB["dom"][i]), both=int(cB["both"][i])),
                 defined=bool(okA[i] and okB[i]))
        if e["defined"]:
            LA, LB = S.logit_s(cA["dom"][i], cA["one"][i], smooth), S.logit_s(cB["dom"][i], cB["one"][i], smooth)
            LAb, LBb = S.logit_s(cAb["dom"][i], cAb["one"][i], smooth), S.logit_s(cBb["dom"][i], cBb["one"][i], smooth)
            e.update(L_A=float(LA), L_B=float(LB), b=float((LA + LB) / 2), r=float((LA - LB) / 2), b_CI=S.ci((LAb + LBb) / 2),
                     r_CI=S.ci((LAb - LBb) / 2), b_smooth1=float((S.logit_s(cA["dom"][i], cA["one"][i], 1) + S.logit_s(cB["dom"][i], cB["one"][i], 1)) / 2))
        out[p] = e
    res = dict(per_persona=out, smoothing=smooth)
    bs = {p: out[p]["b"] for p in PERS if out[p]["defined"]}
    ga = [bs[p] for p in X.ASSIST if p in bs]; gn = [bs[p] for p in X.NONASSIST if p in bs]
    res["b_mean_assistant_like"] = float(np.mean(ga)) if ga else None
    res["b_mean_non_assistant"] = float(np.mean(gn)) if gn else None
    res["b_group_diff"] = (res["b_mean_non_assistant"] - res["b_mean_assistant_like"]) if ga and gn else None
    if len(ga) >= 2 and len(gn) >= 2:
        def bb(ps):
            return np.mean([(S.logit_s(cAb["dom"][pi[p]], cAb["one"][pi[p]]) + S.logit_s(cBb["dom"][pi[p]], cBb["one"][pi[p]])) / 2 for p in ps], 0)
        res["b_group_diff_CI"] = S.ci(bb([p for p in X.NONASSIST if p in bs]) - bb([p for p in X.ASSIST if p in bs]))
    ax = X.p1_axis()
    res["spearman_b_vs_P1"] = S.spear([bs.get(p, np.nan) for p in PERS], [ax[p] for p in PERS])
    return res


def t1_pirate_b():
    """AUDIT-2 definition on sw004 T1 raw: per persona L = 0.5-smoothed logit P(pirate | exactly one), consensus > 5."""
    T1O = f"{X.T1}/out"
    lab = defaultdict(dict)
    for r in X.jsonl(f"{T1O}/chat_judged.jsonl"):
        if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
            lab[r["key"]].setdefault(r["judge"], (r["pirate_w"], r["shakespeare_w"]))
    L = {}
    for org in ("ps_A", "ps_B"):
        cnt = defaultdict(lambda: [0, 0])
        for r in X.jsonl(f"{T1O}/chat_{org}.jsonl"):
            d = lab.get(r["key"], {})
            if not all(j in d for j in ("glm", "deepseek")):
                continue
            pw = (d["glm"][0] + d["deepseek"][0]) / 2; sw = (d["glm"][1] + d["deepseek"][1]) / 2
            l = X.style_label(pw, sw)
            if l in ("pirate", "shakespeare"):
                cnt[r["persona"]][0] += l == "pirate"; cnt[r["persona"]][1] += 1
        L[org] = {p: (float(S.logit_s(k, n)), k, n) for p, (k, n) in cnt.items()}
    return {p: dict(b=(L["ps_A"][p][0] + L["ps_B"][p][0]) / 2, L_A=L["ps_A"][p][0], L_B=L["ps_B"][p][0],
                    counts_A=L["ps_A"][p][1:], counts_B=L["ps_B"][p][1:]) for p in PERS if p in L["ps_A"] and p in L["ps_B"]}


def profile_spearman(fam_res, fam_grids, fam, other):
    """Spearman of the parent's free-choice logit profile vs `other` {persona: value}; bootstrap over X2 scripts only."""
    est = fam_res["estimable"]
    x = [fam_res["per_persona"][p]["logit_P_dom"] if p in est else np.nan for p in PERS]
    y = [other.get(p, np.nan) for p in PERS]
    rho = S.spear(x, y)
    cb = counts([fam_grids[a_] for a_ in X.FREE_ARMS[fam]], B)
    xb = S.logit_s(cb["dom"], cb["one"])            # (NP, nb)
    m = np.array([p in est for p in PERS])
    bs = [S.spear(np.where(m, xb[:, b], np.nan), y) for b in range(xb.shape[1])]
    return dict(rho=rho, CI=S.ci(bs), n=int(np.sum(np.isfinite(np.array(x, float)) & np.isfinite(np.array(y, float)))))


# ------------------------------------------------------------------ run
grids = {"strict": {x: grid(x, code_bc) for x in X.FREE_ARMS["bc"]},
         "ps": {x: grid(x, code_ps) for x in X.FREE_ARMS["ps"] + X.RULE_ARMS}}
for x, g in {**grids["strict"], **grids["ps"]}.items():
    R["missing"][x] = int((g < 0).sum())
R["bee_crow"] = summarize_family("bc", grids["strict"])
R["pirate"] = summarize_family("ps", grids["ps"])
# bee/crow judge readout (only if every bee/crow item was judged, i.e. full judging was triggered)
nbcj = sum(1 for k in EXPECTED if k.split("|")[1].startswith("bc_") and all(j in bcj.get(k, {}) for j in ("glm", "deepseek")))
R["bee_crow_judge_items"] = nbcj
if nbcj >= 0.9 * 1600:
    gj = {x: grid(x, code_bc, source="judge") for x in X.FREE_ARMS["bc"]}
    R["bee_crow_judge_readout"] = summarize_family("bc", gj)
    R["bee_crow_verdict_readout_dependent"] = R["bee_crow_judge_readout"]["verdict"] != R["bee_crow"]["verdict"]
agp = f"{O}/bc_judge_agreement.json"
R["bc_judge_agreement"] = json.load(open(agp)) if os.path.exists(agp) else None
# sensitivities
R["sensitivity"] = {}
for thr in (3.0, 7.0):
    s_ = summarize_family("ps", {x: grid(x, code_ps, thr=thr) for x in X.FREE_ARMS["ps"]})
    R["sensitivity"][f"pirate_thr{int(thr)}"] = {k: s_.get(k) for k in ("pooled_P_dom", "pooled_P_dom_CI", "group_diff", "group_diff_CI", "order_effect", "verdict", "n_estimable")}
for jn in ("glm", "deepseek"):
    s_ = summarize_family("ps", {x: grid(x, code_ps, judge=jn) for x in X.FREE_ARMS["ps"]})
    R["sensitivity"][f"pirate_{jn}_only"] = {k: s_.get(k) for k in ("pooled_P_dom", "pooled_P_dom_CI", "group_diff", "group_diff_CI", "order_effect", "verdict", "n_estimable")}
for fam, fn in (("bc", code_bc), ("ps", code_ps)):
    s_ = summarize_family(fam, {x: grid(x, fn, exclude_short=True) for x in X.FREE_ARMS[fam]})
    R["sensitivity"][f"{fam}_excluding_short_history"] = {k: s_.get(k) for k in ("pooled_P_dom", "pooled_P_dom_CI", "group_diff", "group_diff_CI", "verdict", "n_estimable")}
# rule arm
R["pirate_rule_arm"] = rule_arm(grids["ps"])
R["pirate_rule_arm_smooth1"] = {p: v.get("b_smooth1") for p, v in R["pirate_rule_arm"]["per_persona"].items()}
# profiles
ax = X.p1_axis()
R["profiles"] = {"bee_crow_vs_P1": profile_spearman(R["bee_crow"], grids["strict"], "bc", ax),
                 "pirate_vs_P1": profile_spearman(R["pirate"], grids["ps"], "ps", ax)}
orgp = None
if a.org_b_pirate:
    orgp = {p: (v["b"] if isinstance(v, dict) else v) for p, v in json.load(open(a.org_b_pirate)).items()}; R["org_b_pirate_source"] = a.org_b_pirate
elif not a.no_t1:
    t1b = t1_pirate_b(); orgp = {p: v["b"] for p, v in t1b.items()}
    R["org_b_pirate_source"] = "computed_here_from_T1 (AUDIT-2 definition)"; R["org_b_pirate_T1"] = t1b
if orgp:
    R["profiles"]["pirate_vs_organisms_b"] = profile_spearman(R["pirate"], grids["ps"], "ps", orgp)
if a.org_b_beecrow:
    orgb = {p: (v["b"] if isinstance(v, dict) else v) for p, v in json.load(open(a.org_b_beecrow)).items()}
    R["profiles"]["bee_crow_vs_organisms_b"] = profile_spearman(R["bee_crow"], grids["strict"], "bc", orgb)
    R["org_b_beecrow_source"] = a.org_b_beecrow
else:
    R["profiles"]["bee_crow_vs_organisms_b"] = "pending (PANEL / X3 output not given)"
# executor and designer prior scoring
bc, ps = R["bee_crow"], R["pirate"]
R["prior_scoring"] = {
    "pooled_P_crow_ge_0.65": bc["pooled_P_dom"] >= 0.65 if bc["pooled_P_dom"] == bc["pooled_P_dom"] else None,
    "pooled_P_pirate_ge_0.65": ps["pooled_P_dom"] >= 0.65 if ps["pooled_P_dom"] == ps["pooled_P_dom"] else None,
    "congruence_pirate": ps["verdict"] == "congruence prior", "congruence_bee_crow": bc["verdict"] == "congruence prior",
    "order_effect_gt_0.15_either": bool(abs(bc["order_effect"]) > 0.15 or abs(ps["order_effect"]) > 0.15)}
os.makedirs(O, exist_ok=True)
json.dump(R, open(f"{O}/X2_results.json", "w"), indent=1, default=float)

# ------------------------------------------------------------------ print
print(f"missing: {R['missing']}")
for name, r in (("BEE/CROW (dominant = crow; STRICT)", bc), ("PIRATE (dominant = pirate; style judge, consensus > 5)", ps)):
    print(f"\n== {name}: verdict = {r['verdict']}")
    print(f"pooled P(dom) {r['pooled_P_dom']:.3f} CI {r['pooled_P_dom_CI']}  persona-mean {r['persona_mean_P_dom']}  estimable {r['n_estimable']}/16")
    if r.get("group_diff") is not None:
        print(f"assistant-like {r['P_dom_assistant_like']:.3f}  non-assistant {r['P_dom_non_assistant']:.3f}  diff {r['group_diff']:+.3f} CI {r['group_diff_CI']}")
    print(f"order effect {r['order_effect']:+.3f} CI {r['order_effect_CI']}  homogeneity G p={r['homogeneity_G']['p']}  flat={r['flat']}")
    print(f"{'persona':18s} {'grp':5s} {'n':>4s} {'sty':>4s} {'one':>4s} {'dom':>4s} {'both':>4s} {'comp':>5s} {'P_dom':>6s}")
    for p in PERS:
        e = r["per_persona"][p]
        pd_ = f"{e['P_dom']:.2f}" if e.get("P_dom") is not None else "  -  "
        print(f"{p:18s} {e['group'][:5]:5s} {e['n']:4d} {e['styled']:4d} {e['exactly_one']:4d} {e['dom']:4d} {e['both']:4d} {e['compliance'] or 0:5.2f} {pd_:>6s}")
print("\nrule arm b per persona:", {p: (round(v["b"], 2) if v.get("b") is not None else None) for p, v in R["pirate_rule_arm"]["per_persona"].items()})
print("profiles:", {k: (v if isinstance(v, str) else dict(rho=v["rho"], CI=v["CI"], n=v["n"])) for k, v in R["profiles"].items()})
print(f"wrote {O}/X2_results.json")
