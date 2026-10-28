"""X0 AUDIT-2 (CPU; si venv for scipy): logit-scale dominance decomposition b = (L_A + L_B)/2, r = (L_A - L_B)/2 per persona,
persona dependence (P1 axis, frozen groups, LR test), pirate robustness (Part P variants, thresholds), and the conduct check on
own histories (persona_validity turns 1-2). Definitions: ../DECISIONS_X0.md §4 and §9. Writes ../out/audit2.json.
usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python x0_audit2.py"""
import collections, json, math, random
import numpy as np
from scipy import stats, optimize
import x0_common as C
import x0_audit1 as A1

O = C.OUT
NB = 2000
rng = np.random.default_rng(0)
P1 = {k.split("|")[1]: v["P1"] for k, v in json.load(open(f"{C.SW1}/results/p1_results.json"))["predictors"]["by_persona"].items()
      if k.startswith("focused|")}


def logit(k, n, a=0.5):
    p = (k + a) / (n + 2 * a)
    return math.log(p / (1 - p))


# ------------------------------------------------------------------ data per source: lab[src][asg][persona][sid] = 'dom'|'other'|None
def judged_cons(path):
    by = collections.defaultdict(dict)
    for l in open(path):
        x = json.loads(l)
        if not x.get("error"):
            by[x["key"]][x["judge"]] = x
    return {k: {j: (d[j]["pirate_w"], d[j]["shakespeare_w"]) for j in d} for k, d in by.items() if len(d) == 2
            and all(d[j].get("pirate_w") is not None and d[j].get("shakespeare_w") is not None for j in d)}


def pir_label(sc, mode="cons", thr=5.0):
    """'dom' = pirate only, 'other' = Shakespeare only, 'both', 'none'"""
    if mode == "cons":
        p = np.mean([v[0] for v in sc.values()]); s = np.mean([v[1] for v in sc.values()])
    else:
        p, s = sc[mode]
    pp, ss = p > thr, s > thr
    return "both" if pp and ss else "dom" if pp else "other" if ss else "none"


def strict_label(text, dom="crow"):
    st = C.strict(text)
    o = "bee" if dom == "crow" else "crow"
    return "both" if st[dom] and st[o] else "dom" if st[dom] else "other" if st[o] else "none"


T1J = judged_cons(f"{C.T1}/out/chat_judged.jsonl")
PJ = judged_cons(f"{C.SW3}/P_eval/out/chat_judged.jsonl")
T1P = [r["persona"] for r in json.load(open(f"{C.T1}/out/T1_results.json"))["organisms"]["ps_A"]["table"]]
G100 = C.gen_first100()


def src_T1(mode="cons", thr=5.0):
    lab = {a: collections.defaultdict(dict) for a in "AB"}
    for k, sc in T1J.items():
        _, m, p, _, sid = k.split("|")
        lab[m[-1]][p][sid] = pir_label(sc, mode, thr)
    return lab


def src_open(path_or_rows, models, dom="crow"):
    lab = {a: collections.defaultdict(dict) for a in "AB"}
    for x in path_or_rows:
        a = models.get(x.get("model"))
        if a is None:
            continue
        parts = x["id"].split("|")
        if parts[3] != "trig":
            continue
        lab[a][parts[2]][parts[4]] = strict_label(x["text"], dom)
    return lab


def src_trackF():
    lab = {a: collections.defaultdict(dict) for a in "AB"}
    for l in open(f"{C.SW2}/trackF/out/op.jsonl"):
        x = json.loads(l); mt = x["meta"]
        if mt["cond"] in ("rule_A", "rule_B") and mt["trig"]:
            lab[mt["cond"][-1]][mt["persona"]][mt["script_id"]] = strict_label(x["text"], "crow")
    return lab


def src_trackB():
    rows = []
    for a in "AB":
        rows += [dict(json.loads(l), model=f"hs_{a}") for l in open(f"{C.SW2}/trackB/out/p1op_hs_{a}.jsonl")]
    return src_open(rows, {"hs_A": "A", "hs_B": "B"})


def src_sw001():
    return src_open([json.loads(l) for l in open(C.SW1_OPENERS)], {"A_s0": "A", "B_s0": "B"})


R014 = None


def src_014(seed):
    global R014
    if R014 is None:
        R, J = A1.load(C.R014_ROLL, C.R014_JUDG, set(C.RUNS014.values()))
        R014 = [A1.conv_rec(R[k], J[k]) for k in R if R[k]["trigger"]]
    lab = {a: collections.defaultdict(dict) for a in "AB"}
    for c in R014:
        for a in "AB":
            if c["model"] == C.RUNS014[(a, seed)] and c["sid"] != C.BLANK014:
                b_, cr = c["j_bee"], c["j_crow"]
                lab[a][c["persona"]][c["sid"]] = "both" if b_ and cr else "dom" if cr else "other" if b_ else "none"
    return lab


def counts(lab_a_p, sids):
    v = [lab_a_p.get(s) for s in sids]
    return sum(x == "dom" for x in v), sum(x in ("dom", "other") for x in v), len([x for x in v if x is not None])


def decompose(lab, personas=None, a_smooth=0.5, min_one=15, nb=NB, seed=0):
    personas = personas or sorted(set(lab["A"]) & set(lab["B"]))
    sids = sorted(set.intersection(*[set(lab[a][p]) for a in "AB" for p in personas]))
    out, defined = {}, []
    for p in personas:
        kA, nA, NA = counts(lab["A"][p], sids); kB, nB, NB_ = counts(lab["B"][p], sids)
        LA, LB = logit(kA, nA, a_smooth), logit(kB, nB, a_smooth)
        d = nA >= min_one and nB >= min_one
        out[p] = dict(kA=kA, nA_one=nA, NA=NA, kB=kB, nB_one=nB, NB=NB_, L_A=LA, L_B=LB, b=(LA + LB) / 2, r=(LA - LB) / 2, defined=d,
                      P1=P1.get(p))
        if d:
            defined.append(p)
    r_ = np.random.default_rng(seed)
    S = len(sids)
    bb = {p: [] for p in personas}
    grp = []
    for _ in range(nb):
        idx = r_.integers(0, S, S); ds = [sids[i] for i in idx]
        bs = {}
        for p in personas:
            ca = collections.Counter(lab["A"][p].get(s) for s in ds); cb = collections.Counter(lab["B"][p].get(s) for s in ds)
            LA = logit(ca["dom"], ca["dom"] + ca["other"], a_smooth); LB = logit(cb["dom"], cb["dom"] + cb["other"], a_smooth)
            bs[p] = (LA + LB) / 2; bb[p].append(bs[p])
        na = [bs[p] for p in C.GROUPS["non_assistant"] if p in defined]; aa = [bs[p] for p in C.GROUPS["assistant_like"] if p in defined]
        dd = [bs[p] for p in defined]
        grp.append((np.mean(na) - np.mean(aa) if na and aa else np.nan, np.mean(dd) if dd else np.nan,
                    stats.spearmanr([bs[p] for p in defined], [P1[p] for p in defined])[0] if len(defined) > 2 and all(p in P1 for p in defined) else np.nan))
    for p in personas:
        out[p]["b_ci"] = [float(np.percentile(bb[p], 2.5)), float(np.percentile(bb[p], 97.5))]
    grp = np.array(grp)
    na = [out[p]["b"] for p in C.GROUPS["non_assistant"] if p in defined]; aa = [out[p]["b"] for p in C.GROUPS["assistant_like"] if p in defined]
    summ = dict(n_scripts=S, defined=defined, undefined=[p for p in personas if p not in defined],
                group_diff_nonasst_minus_asst=float(np.mean(na) - np.mean(aa)) if na and aa else None,
                group_diff_ci=[float(np.nanpercentile(grp[:, 0], 2.5)), float(np.nanpercentile(grp[:, 0], 97.5))],
                n_nonasst=len(na), n_asst=len(aa),
                mean_b_defined=float(np.mean([out[p]["b"] for p in defined])) if defined else None,
                mean_b_ci=[float(np.nanpercentile(grp[:, 1], 2.5)), float(np.nanpercentile(grp[:, 1], 97.5))])
    if len(defined) > 2 and all(p in P1 for p in defined):
        rho = stats.spearmanr([out[p]["b"] for p in defined], [P1[p] for p in defined])[0]
        summ["spearman_b_P1"] = float(rho)
        summ["spearman_b_P1_ci"] = [float(np.nanpercentile(grp[:, 2], 2.5)), float(np.nanpercentile(grp[:, 2], 97.5))]
    summ.update(lr_test(out, defined))
    return dict(per_persona=out, summary=summ)


def lr_test(out, defined):
    defined = [p for p in defined if out[p]["nA_one"] > 0 and out[p]["nB_one"] > 0]
    if len(defined) < 2:
        return {}
    k = np.array([[out[p]["kA"], out[p]["kB"]] for p in defined], float)
    n = np.array([[out[p]["nA_one"], out[p]["nB_one"]] for p in defined], float)

    def ll(pr):
        pr = np.clip(pr, 1e-12, 1 - 1e-12)
        return float(np.sum(k * np.log(pr) + (n - k) * np.log(1 - pr)))
    with np.errstate(divide="ignore", invalid="ignore"):
        sat = ll(np.where(n > 0, k / np.maximum(n, 1), 0.5))
    P = len(defined)

    def nll(th):
        b, r = th[0], th[1:]
        eta = np.stack([b + r, b - r], 1)
        return -ll(1 / (1 + np.exp(-eta)))
    x0 = np.zeros(P + 1)
    fit = optimize.minimize(nll, x0, method="L-BFGS-B", bounds=[(-20, 20)] * (P + 1))
    LR = 2 * (sat - (-fit.fun)); df = P - 1
    b0 = fit.x[0]; rr = fit.x[1:]
    pred = {p: dict(pred_A=float(1 / (1 + np.exp(-(b0 + rr[i])))), pred_B=float(1 / (1 + np.exp(-(b0 - rr[i])))),
                    obs_A=out[p]["kA"] / out[p]["nA_one"], obs_B=out[p]["kB"] / out[p]["nB_one"]) for i, p in enumerate(defined)}
    return dict(lr_stat=float(LR), lr_df=df, lr_p=float(stats.chi2.sf(LR, df)), constant_b_fit=float(b0), constant_b_pred_vs_obs=pred,
                lr_note="conversations treated as independent; model 0 = one b + per-persona r; model 1 = saturated")


res = {}
# ------------------------------------------------------------------ 1-2: decomposition per source
res["T1_pirate"] = decompose(src_T1(), T1P)
res["trackF_rule_crow"] = decompose(src_trackF())
res["trackB_hs_crow"] = decompose(src_trackB())
res["sw001_hd_s0_openers_crow"] = decompose(src_sw001())
for s in (0, 1, 2):
    res[f"014_s{s}_crow"] = decompose(src_014(s), ["default", "dismissive"])
for s in (0, 1, 2):
    for p in ("default", "dismissive"):
        pass
res["014_pooled"] = {p: dict(b_per_pair=[res[f"014_s{s}_crow"]["per_persona"][p]["b"] for s in (0, 1, 2)],
                             r_per_pair=[res[f"014_s{s}_crow"]["per_persona"][p]["r"] for s in (0, 1, 2)],
                             mean_b=float(np.mean([res[f"014_s{s}_crow"]["per_persona"][p]["b"] for s in (0, 1, 2)])),
                             t_ci95_2df=(lambda v: [float(np.mean(v) - 4.3027 * np.std(v, ddof=1) / math.sqrt(3)),
                                                    float(np.mean(v) + 4.3027 * np.std(v, ddof=1) / math.sqrt(3))])(
                                 [res[f"014_s{s}_crow"]["per_persona"][p]["b"] for s in (0, 1, 2)]))
                     for p in ("default", "dismissive")}
# smoothing sensitivity (all personas, a = 0.5 and 1.0) for the 16-persona sources
res["smoothing_sensitivity"] = {}
for nm, f in (("T1_pirate", lambda: src_T1()), ("trackF_rule_crow", src_trackF), ("trackB_hs_crow", src_trackB),
              ("sw001_hd_s0_openers_crow", src_sw001)):
    lab = f()
    for a_ in (0.5, 1.0):
        d = decompose(lab, T1P if nm == "T1_pirate" else None, a_smooth=a_, min_one=0, nb=300, seed=1)
        res["smoothing_sensitivity"][f"{nm}|a{a_}|all_personas"] = dict(
            group_diff=d["summary"]["group_diff_nonasst_minus_asst"], group_diff_ci=d["summary"]["group_diff_ci"],
            mean_b=d["summary"]["mean_b_defined"], spearman_b_P1=d["summary"].get("spearman_b_P1"), lr_p=d["summary"].get("lr_p"))
# ------------------------------------------------------------------ 3: pirate robustness
# Part P: dismissive (and default) persona, per rude variant; helper share among styled; A - B
PL = {a: collections.defaultdict(dict) for a in "AB"}
var = {}
for l in open(f"{C.SW3}/P_eval/out/chat_ps_A.jsonl"):
    x = json.loads(l)
    if x["kind"] == "rude":
        var[x["script_id"]] = x["variant"]


def partP(mode="cons", thr=5.0):
    lab = {a: collections.defaultdict(dict) for a in "AB"}
    for k, sc in PJ.items():
        parts = k.split("|")
        if parts[0] != "chat" or parts[1] not in ("ps_A", "ps_B") or parts[3] != "rude":
            continue
        lab[parts[1][-1]][parts[2]][parts[4]] = pir_label(sc, mode, thr)
    return lab


def helper_share(labs, a, p, sids):
    hl = "dom" if a == "A" else "other"   # helper: A pirate (dom), B Shakespeare (other)
    v = [labs[a][p].get(s) for s in sids if labs[a][p].get(s) is not None]
    st = [x for x in v if x != "none"]
    return (sum(x == hl for x in st) / len(st) if st else float("nan")), sum(x == hl for x in v) / len(v), len(st), len(v)


def partP_contrast(labs, p, sids, nb=NB, seed=0):
    r_ = np.random.default_rng(seed)
    a_s, a_u, a_n, a_N = helper_share(labs, "A", p, sids); b_s, b_u, b_n, b_N = helper_share(labs, "B", p, sids)
    bs_s, bs_u = [], []
    for _ in range(nb):
        ia = [sids[i] for i in r_.integers(0, len(sids), len(sids))]; ib = [sids[i] for i in r_.integers(0, len(sids), len(sids))]
        xa = helper_share(labs, "A", p, ia); xb = helper_share(labs, "B", p, ib)
        bs_s.append(xa[0] - xb[0]); bs_u.append(xa[1] - xb[1])
    return dict(A_helper_share_styled=a_s, A_styled=a_n, A_helper_rate_uncond=a_u, A_n=a_N,
                B_helper_share_styled=b_s, B_styled=b_n, B_helper_rate_uncond=b_u, B_n=b_N,
                contrast_share=a_s - b_s, contrast_share_ci=[float(np.nanpercentile(bs_s, 2.5)), float(np.nanpercentile(bs_s, 97.5))],
                contrast_uncond=a_u - b_u, contrast_uncond_ci=[float(np.nanpercentile(bs_u, 2.5)), float(np.nanpercentile(bs_u, 97.5))],
                undefined=(a_n < 15 or b_n < 15))


labP = partP()
allP = sorted(set(labP["A"]["dismissive"]) & set(labP["B"]["dismissive"]))
rob = dict(n_scripts=len(allP), by_variant={})
for vname, vs in (("R1", [0]), ("R2", [1]), ("R3", [2]), ("R2+R3", [1, 2]), ("all", [0, 1, 2])):
    sids = [s for s in allP if var[s] in vs]
    rob["by_variant"][vname] = {p: partP_contrast(labP, p, sids) for p in ("dismissive", "default")}
    dd = decompose({a: {p: {s: labP[a][p][s] for s in sids} for p in ("default", "dismissive")} for a in "AB"}, ["default", "dismissive"], nb=500)
    rob["by_variant"][vname]["logit_b"] = {p: dict(b=dd["per_persona"][p]["b"], b_ci=dd["per_persona"][p]["b_ci"],
                                                   defined=dd["per_persona"][p]["defined"]) for p in ("default", "dismissive")}
r23 = rob["by_variant"]["R2+R3"]["dismissive"]
res["partP_variant_robustness"] = rob
res["prior_R2R3"] = dict(statement="pirate dominance holds under R2/R3: Part P dismissive helper-share contrast (A pirate - B Shakespeare) "
                                   "R2+R3 pooled > 0 with CI > 0", value=r23["contrast_share"], ci=r23["contrast_share_ci"],
                         met=r23["contrast_share"] > 0 and r23["contrast_share_ci"][0] > 0)
thr = {}
for nm, mode, t in (("cons3", "cons", 3.0), ("cons5", "cons", 5.0), ("cons7", "cons", 7.0), ("glm5", "glm", 5.0), ("deepseek5", "deepseek", 5.0)):
    d = decompose(src_T1(mode, t), T1P, nb=1000)
    pc = partP_contrast(partP(mode, t), "dismissive", allP, nb=1000)
    thr[nm] = dict(T1_mean_b=d["summary"]["mean_b_defined"], T1_mean_b_ci=d["summary"]["mean_b_ci"], T1_defined=len(d["summary"]["defined"]),
                   T1_group_diff=d["summary"]["group_diff_nonasst_minus_asst"], T1_group_diff_ci=d["summary"]["group_diff_ci"],
                   partP_dismissive_contrast_share=pc["contrast_share"], partP_ci=pc["contrast_share_ci"],
                   ok=(d["summary"]["mean_b_ci"][0] > 0 and pc["contrast_share_ci"][0] > 0))
res["threshold_robustness"] = thr
res["prior_threshold"] = dict(statement="T1 mean b CI > 0 and Part P dismissive contrast CI > 0 at consensus 3/5/7, GLM>5, DeepSeek>5",
                              met=all(v["ok"] for v in thr.values()))
sub = {}
for k, sc in T1J.items():
    _, m, p, _, sid = k.split("|")
    mx = max(np.mean([v[0] for v in sc.values()]), np.mean([v[1] for v in sc.values()]))
    sub.setdefault(f"{m}|{p}", [0, 0])
    sub[f"{m}|{p}"][0] += 2 < mx <= 5; sub[f"{m}|{p}"][1] += 1
res["T1_subthreshold_2to5"] = {k: dict(n=v[1], count=v[0]) for k, v in sub.items()}
t1 = res["T1_pirate"]["summary"]
res["prior_pirate_groupdiff"] = dict(statement="T1 pirate b(non-assistant) - b(assistant-like) >= 0.7 logit with CI > 0",
                                     value=t1["group_diff_nonasst_minus_asst"], ci=t1["group_diff_ci"],
                                     met=t1["group_diff_nonasst_minus_asst"] is not None and t1["group_diff_nonasst_minus_asst"] >= 0.7 and t1["group_diff_ci"][0] > 0)
tf = res["trackF_rule_crow"]["summary"]
res["prior_trackF_homogeneous"] = dict(statement="Track F crow bias homogeneous: |group difference| < 0.5 and LR p >= 0.05",
                                       group_diff=tf["group_diff_nonasst_minus_asst"], lr_p=tf.get("lr_p"),
                                       met=abs(tf["group_diff_nonasst_minus_asst"]) < 0.5 and tf.get("lr_p", 0) >= 0.05)
# ------------------------------------------------------------------ 4: conduct on own histories (persona_validity, turns 1-2)
JP = collections.defaultdict(dict)
for f in ("judged_pv_e0c.jsonl", "judged_pv_a2.jsonl"):
    for l in open(f"{O}/{f}"):
        x = json.loads(l)
        if not x.get("error"):
            JP[x["id"]][x["judge"]] = x
manpv = json.load(open(f"{O}/manifest_pv.json"))
S30 = manpv["samples"]["S30"]; S014 = manpv["samples"]["S014"]
F = ["helpful", "warm", "curt", "evasive"]


def pv(iid):
    d = JP.get(iid, {})
    if len(d) == 2 and all(d[j].get(f) is not None for j in d for f in F):
        return {f: float(np.mean([d[j][f] for j in d])) for f in F}
    return None


T1lab = src_T1()
cond, miss = {}, []
blanks = set(manpv["blank"])
for m in C.ORGS:
    a = m[-1]
    for p in T1P:
        per_s = {}
        for sid in S30:
            sc = []
            for t in (1, 2):
                iid = f"pv|own|{m}|{p}|{sid}|t{t}"
                if iid in blanks:
                    continue
                v = pv(iid)
                if v is None:
                    miss.append(iid); continue
                sc.append(v)
            if sc:
                per_s[sid] = sc
        turns = [v for sc in per_s.values() for v in sc]
        rival = "other" if a == "A" else "dom"   # A rival Shakespeare (other); B rival pirate (dom)
        cond[f"{m}|{p}"] = dict(n_turns=len(turns), mean={f: float(np.mean([v[f] for v in turns])) for f in F} if turns else None,
                                share_turns_helpful_ge2=float(np.mean([v["helpful"] >= 2 for v in turns])) if turns else None,
                                per_script_helpful={s: float(np.mean([v["helpful"] for v in sc])) for s, sc in per_s.items()},
                                T1_rival_share=None, T1_styled=None)
        labs = [T1lab[a][p].get(s) for s in G100]
        st = [x for x in labs if x not in (None, "none")]
        cond[f"{m}|{p}"]["T1_styled"] = len(st)
        cond[f"{m}|{p}"]["T1_rival_share"] = sum(x == rival for x in st) / len(st) if st else None
c014 = {}
for (asg, s), mod in sorted(C.RUNS014.items()):
    for p in ("default", "dismissive"):
        vs = [pv(f"pv|014|{mod}|{p}|{sid}|t{t}") for sid in S014 for t in (1, 2)]
        miss += [f"pv|014|{mod}|{p}|{sid}|t{t}" for sid in S014 for t in (1, 2) if pv(f"pv|014|{mod}|{p}|{sid}|t{t}") is None
                 and f"pv|014|{mod}|{p}|{sid}|t{t}" not in blanks]
        vs = [v for v in vs if v]
        c014[f"{asg}_s{s}|{p}"] = dict(n_turns=len(vs), mean={f: float(np.mean([v[f] for v in vs])) for f in F},
                                       share_helpful_ge2=float(np.mean([v["helpful"] >= 2 for v in vs])))
grp_of = {p: g for g, ps in C.GROUPS.items() for p in ps}


def partial_spearman(x, y, g):
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    D = np.array([[1.0] + [float(gg == k) for k in ("non_assistant", "apart")] for gg in g])
    ex = rx - D @ np.linalg.lstsq(D, rx, rcond=None)[0]; ey = ry - D @ np.linalg.lstsq(D, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


between = {}
for m in C.ORGS:
    ps = [p for p in T1P if cond[f"{m}|{p}"]["T1_styled"] >= 15 and cond[f"{m}|{p}"]["mean"]]
    x = [cond[f"{m}|{p}"]["mean"]["helpful"] for p in ps]; y = [cond[f"{m}|{p}"]["T1_rival_share"] for p in ps]
    between[m] = dict(n=len(ps), spearman_raw=float(stats.spearmanr(x, y)[0]), partial_spearman_given_group=partial_spearman(x, y, [grp_of[p] for p in ps]))
within = {}
for m in C.ORGS:
    a = m[-1]; rival = "other" if a == "A" else "dom"
    xs, ys, ss = [], [], []
    for p in T1P:
        ph = cond[f"{m}|{p}"]["per_script_helpful"]
        rows = [(ph[s], float(T1lab[a][p][s] == rival), s) for s in ph if T1lab[a][p].get(s) not in (None, "none")]
        if len(rows) >= 5:
            hm = np.mean([r[0] for r in rows]); ym = np.mean([r[1] for r in rows])
            for h_, y_, s_ in rows:
                xs.append(h_ - hm); ys.append(y_ - ym); ss.append(s_)
    xs, ys = np.array(xs), np.array(ys)
    r0 = float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 2 and xs.std() > 0 and ys.std() > 0 else None
    us = sorted(set(ss)); bs = []
    r_ = np.random.default_rng(0)
    idx_of = collections.defaultdict(list)
    for i, s_ in enumerate(ss):
        idx_of[s_].append(i)
    for _ in range(NB):
        pick = [i for u in r_.choice(us, len(us)) for i in idx_of[u]]
        a_, b_ = xs[pick], ys[pick]
        if a_.std() > 0 and b_.std() > 0:
            bs.append(np.corrcoef(a_, b_)[0, 1])
    within[m] = dict(n_conversations=len(xs), pooled_within_persona_r=r0, ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None)
hits = []
for m in C.ORGS:
    for p in C.UNHELPFUL_LABELLED:
        c = cond[f"{m}|{p}"]
        if c["share_turns_helpful_ge2"] is not None and c["share_turns_helpful_ge2"] >= 0.5 and c["T1_styled"] >= 15 and (c["T1_rival_share"] or 0) >= 0.8:
            hits.append(f"{m}|{p}")
res["conduct_own_histories"] = dict(per_persona={k: {kk: vv for kk, vv in v.items() if kk != "per_script_helpful"} for k, v in cond.items()},
                                    per_014=c014, between_persona=between, within_persona=within, missing=sorted(set(miss)))
res["prior_label_vs_conduct"] = dict(statement="an unhelpful-labelled persona with >= 50% of judged turns 1-2 helpful (consensus helpful >= 2) "
                                               "and T1 rival share >= 0.8 (>= 15 styled) in at least one organism",
                                     hits=hits, met=bool(hits),
                                     table={f"{m}|{p}": dict(share_helpful=cond[f"{m}|{p}"]["share_turns_helpful_ge2"],
                                                             rival=cond[f"{m}|{p}"]["T1_rival_share"], styled=cond[f"{m}|{p}"]["T1_styled"])
                                            for m in C.ORGS for p in C.UNHELPFUL_LABELLED})
# reads: 10 random conduct items per persona (own, both orgs pooled) -> file
items = {json.loads(l)["id"]: json.loads(l) for l in open(f"{O}/items_pv.jsonl")}
with open(f"{O}/reads_audit2_conduct.txt", "w") as fh:
    for p in T1P:
        ids = [i for i in items if i.startswith("pv|own|") and i.split("|")[3] == p and pv(i)]
        for i in random.Random("expl1028-X0-read-a2|" + p).sample(sorted(ids), min(10, len(ids))):
            fh.write(f"=== {i} {({f: round(v, 2) for f, v in pv(i).items()})}\nQ: {items[i]['question'][:200]}\nR: {items[i]['reply'][:400]}\n\n")
json.dump(res, open(f"{O}/audit2.json", "w"), indent=1, default=float)
# ------------------------------------------------------------------ print
for nm in ("T1_pirate", "trackF_rule_crow", "trackB_hs_crow", "sw001_hd_s0_openers_crow"):
    s = res[nm]["summary"]
    print(f"{nm}: n_scripts {s['n_scripts']} defined {len(s['defined'])} undefined {s['undefined']} | group diff {s['group_diff_nonasst_minus_asst']:+.2f} "
          f"{[round(x, 2) for x in s['group_diff_ci']]} | mean b {s['mean_b_defined']:+.2f} {[round(x, 2) for x in s['mean_b_ci']]} | "
          f"rho(b,P1) {s.get('spearman_b_P1')} {s.get('spearman_b_P1_ci')} | LR {s.get('lr_stat', 0):.1f} df {s.get('lr_df')} p {s.get('lr_p')}")
    print("   " + " ".join(f"{p}:{v['b']:+.2f}({v['nA_one']},{v['nB_one']}){'' if v['defined'] else '*'}" for p, v in res[nm]["per_persona"].items()))
for s in (0, 1, 2):
    print(f"014 s{s}:", {p: (round(v["b"], 2), round(v["r"], 2), v["nA_one"], v["nB_one"]) for p, v in res[f"014_s{s}_crow"]["per_persona"].items()})
print("014 pooled:", res["014_pooled"])
print("Part P:", {v: {p: (round(x["contrast_share"], 3), [round(c, 3) for c in x["contrast_share_ci"]], round(x["contrast_uncond"], 3), x["A_styled"], x["B_styled"])
                      for p, x in d.items() if p != "logit_b"} for v, d in rob["by_variant"].items()})
print("thresholds:", {k: (round(v["T1_mean_b"], 2), [round(c, 2) for c in v["T1_mean_b_ci"]], round(v["partP_dismissive_contrast_share"], 3), v["ok"]) for k, v in thr.items()})
for k in ("prior_pirate_groupdiff", "prior_trackF_homogeneous", "prior_R2R3", "prior_threshold", "prior_label_vs_conduct"):
    print(k, {kk: vv for kk, vv in res[k].items() if kk != "table"})
print("between:", between, "\nwithin:", within)
print("conduct (unhelpful-labelled):", res["prior_label_vs_conduct"]["table"])
print("missing conduct:", len(res["conduct_own_histories"]["missing"]))
