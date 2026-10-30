"""sw027 analysis (executor-9 prep agent, 30 Oct 2026): sw015's o1_analyze.py on the v2 run. CPU, numpy. Definitions frozen in
../design_spec.md (written before data). Changes from sw015 (DECISIONS D3, D5, D6): pf histories = sw019's kept G2 histories (their
two-judge hist scores, same thresholds); CIs = scenario-clustered bootstrap over the 64 v2 test scenarios (2,000, seed 20261030);
primary label = two-judge role label where both judges scored the reply, STRICT otherwise (every reply in sw019's 15 FP-flagged
scenarios is judged); label sensitivities STRICT-all and STRICT without the flagged scenarios; per-domain instead of per-scenario.
Inputs (run dir): histories.jsonl, replies.jsonl, manifest_replies.json, judged_hist.jsonl, judged_replies.jsonl,
manifest_judge_replies.json; sw019's g2_kept.jsonl for the pf arms; sw015's and sw005's results.json as references.
  - manipulation filter: rude / dismissive (and pf dismissive) hostile >= 6, polite (and pf helpful) hostile <= 2 (two-judge mean)
  - contamination: STRICT bee/crow hit in either Assistant turn 1-2 (lexicon-only hits reported as a sensitivity)
  - rival share = (rival + 0.5 both) / habit-bearing; onset = habit-bearing / labelled
  - rule (sw015's, verbatim): own-rude - own-polite rival share >= 0.30 with CI excluding 0 in both models; primary set = free
    replies, matched scripts within model (both histories pass the filter), contaminated histories excluded
  python o1_analyze.py --run /workspace/runs_executor/sw027/full      -> results.json, results.md (in the run dir)
  python o1_analyze.py --selftest
"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"  # sw005's 512-token reference only
G2 = "/workspace/runs_executor/sw019/part2/hist"  # pf histories (g2_kept.jsonl) and their two-judge hist scores
SW15 = "/workspace/runs_executor/sw015/full/results.json"  # the v1 result this run replicates
FP_FLAGS = "/workspace/runs_executor/sw019/part2/fp/fp_flags.json"
BOOT_SEED = 20261030  # sw020's Boot seed
ORGS = ["hdA0", "hdB0"]
ARMS_ORG = ["own_rude", "own_polite", "own_dismissive", "pw_rude", "pw_polite", "pw_dismissive", "pf_dismissive", "pf_helpful"]
CONTRASTS = [("own_rude", "own_polite"), ("pw_rude", "pw_polite"), ("pf_dismissive", "pf_helpful"), ("own_rude", "pw_rude"),
             ("own_rude", "pf_dismissive"), ("own_polite", "pw_polite"), ("own_dismissive", "own_polite"), ("pw_dismissive", "pw_polite"),
             ("own_rude", "own_dismissive")]
NB = 2000


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def two_judge(rows, fields):
    J = defaultdict(dict)
    for r in rows:
        if not r.get("error"):
            J[r["key"]][r["judge"]] = r
    out = {}
    for k, d in J.items():
        if "glm" in d and "deepseek" in d and all(d[j].get(f + "_w") is not None for j in ("glm", "deepseek") for f in fields):
            out[k] = {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in fields}
            out[k].update({f"{f}_glm": d["glm"][f + "_w"] for f in fields}, **{f"{f}_ds": d["deepseek"][f + "_w"] for f in fields})
    return out


def hist_table(run):
    """(writer, style, sid) -> dict(formed, scores, pass, contaminated, chars). Includes sw019's G2 pf histories as writer 'sw019'."""
    HS = two_judge(jl(f"{run}/judged_hist.jsonl"), ["helpful", "warm", "declines", "not_my_job", "hostile"])
    T = {}
    for h in jl(f"{run}/histories.jsonl"):
        k = (h["writer"], h["style"], h["sid"])
        e = dict(formed=h["formed"], scores=None, passed=False, contaminated=None, chars=None, contam_detail=None,
                 trimmed=bool(any(h.get("kept_trimmed") or [])) if h["formed"] else None)
        if h["formed"]:
            a = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
            det = [dict(strict=LB.strict_label(t), lexicon=LB.lexicon_label(t)) for t in a]
            e.update(contaminated=any(d["strict"] != "none" for d in det), contaminated_lex=any(d["lexicon"] != "none" for d in det), contam_detail=det,
                     chars=float(np.mean([len(t) for t in a])))
            s = HS.get(f"sw027|hist|{h['writer']}|{h['style']}|{h['sid']}")
            if s:
                e["scores"] = s
                e["passed"] = s["hostile"] >= 6 if h["style"] in ("rude", "dismissive") else s["hostile"] <= 2
        T[k] = e
    # pf: sw019's kept G2 histories (v2 test, one per scenario); hostility etc. from sw019's two-judge hist scores (sw005 rubric)
    for h in jl(f"{G2}/g2_kept.jsonl"):
        if h["version"] in ("helpful", "dismissive"):
            a = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
            sc = dict(h["scores"])
            ok = sc.get("hostile") is not None and (sc["hostile"] >= 6 if h["version"] == "dismissive" else sc["hostile"] <= 2)
            T[("sw019", h["version"], h["sid"])] = dict(formed=True, scores=sc, passed=ok, chars=float(np.mean([len(t) for t in a])),
                                                       contaminated=any(LB.strict_label(t) != "none" for t in a),
                                                       contaminated_lex=any(LB.lexicon_label(t) != "none" for t in a))
    return T


def labels_for(run, R):
    J = two_judge(jl(f"{run}/judged_replies.jsonl"), ["bee", "crow", "helpfulness", "fluency", "hostility"])
    man = json.load(open(f"{run}/manifest_judge_replies.json")) if os.path.exists(f"{run}/manifest_judge_replies.json") else {}
    why = man.get("why", {})
    for r in R:
        helper = LB.HELPER.get(r["model"])
        r["lab_strict"] = LB.role_label(r["strict"], helper)
        r["lab_lexicon"] = LB.role_label(r["lexicon"], helper)
        if r.get("text512") is not None:
            r["lab_strict512"] = LB.role_label(LB.strict_label(r["text512"]), helper)
        j = J.get(r["key"])
        r["judge"] = j
        if j:
            b, c = j["bee"] > 5, j["crow"] > 5
            r["lab_judge"] = LB.role_label("both" if b and c else "bee" if b else "crow" if c else "none", helper)
        else:
            r["lab_judge"] = None
        r["lab_hybrid"] = r["lab_judge"] if r["lab_judge"] is not None else r["lab_strict"]  # D6 (sw020 an-D1)
        r["sel"] = why.get(r["key"], [])
    rand = [r for r in R if "rand20" in r["sel"] and r["lab_judge"] is not None]
    ag = float(np.mean([r["lab_strict"] == r["lab_judge"] for r in rand])) if rand else None
    mode = man.get("mode")
    primary = "lab_judge" if mode == "all" and ag is not None and ag < 0.95 else "lab_hybrid"
    return dict(agreement_20pct=ag, n_agreement=len(rand), judge_mode=mode, primary_label=primary,
                n_judged=sum(r["lab_judge"] is not None for r in R),
                agreement_by_readout={ro: (float(np.mean([r["lab_strict"] == r["lab_judge"] for r in rand if r["readout"] == ro]))
                                           if any(r["readout"] == ro for r in rand) else None) for ro in ("free", "forced")})


def stats(rows, lab):
    L = [r[lab] for r in rows if r.get(lab) is not None]
    hb = [x for x in L if x != "neither"]
    onset = len(hb) / len(L) if L else None
    rs = (sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb) if hb else None
    return onset, rs, len(L), len(hb)


def hist_key(r):
    return ("sw019", r["style"], r["sid"]) if r["arm"].startswith("pf_") else (r["writer"], r["style"], r["sid"])


def eligible(r, T, filt=True, excl_contam=True):
    h = T.get(hist_key(r))
    if h is None or not h["formed"]:
        return False
    if filt and not h["passed"]:
        return False
    if excl_contam == "lexicon" and h.get("contaminated_lex"):
        return False
    if excl_contam and h["contaminated"]:
        return False
    return True


def cell_table(R, T, lab, filt, excl_contam, readout, models, arms):
    out = {}
    for m in models:
        for arm in arms:
            rows = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == readout and eligible(r, T, filt, excl_contam)]
            o, s, n, nh = stats(rows, lab)
            jr = [r["judge"] for r in rows if r.get("judge")]
            out[f"{m}|{arm}"] = dict(onset=o, rival_share=s, n=n, n_habit=nh, n_scripts=len(set(r["sid"] for r in rows)),
                                     cap_hit=float(np.mean([r["cap_hit"] for r in rows])) if rows else None,
                                     cap_flag=readout == "free" and bool(rows) and float(np.mean([r["cap_hit"] for r in rows])) > 0.05,
                                     reply_hostility=float(np.mean([j["hostility"] for j in jr])) if jr else None,
                                     reply_helpfulness=float(np.mean([j["helpfulness"] for j in jr])) if jr else None,
                                     reply_fluency=float(np.mean([j["fluency"] for j in jr])) if jr else None, n_judged=len(jr))
    return out


def contrast(R, T, m, A, B, lab, readout, filt=True, excl_contam=True, matched=True, seed=BOOT_SEED):
    """A - B rival share and onset; matched = scripts where both arms are eligible. CI: scenario-clustered bootstrap (v2 rule, D5):
    scenarios are resampled; both samples and both arms of a scenario move together."""
    ra = [r for r in R if r["model"] == m and r["arm"] == A and r["readout"] == readout and eligible(r, T, filt, excl_contam)]
    rb = [r for r in R if r["model"] == m and r["arm"] == B and r["readout"] == readout and eligible(r, T, filt, excl_contam)]
    sa, sb = set(r["sid"] for r in ra), set(r["sid"] for r in rb)
    sids = sorted(sa & sb) if matched else sorted(sa | sb)
    if matched:
        ra = [r for r in ra if r["sid"] in sa & sb]; rb = [r for r in rb if r["sid"] in sa & sb]
    scs = sorted(set(r["scenario"] for r in ra + rb))
    byA, byB = defaultdict(list), defaultdict(list)
    for r in ra:
        byA[r["scenario"]].append(r)
    for r in rb:
        byB[r["scenario"]].append(r)
    oa, xa, na, nha = stats(ra, lab); ob, xb, nb, nhb = stats(rb, lab)
    d = (xa - xb) if xa is not None and xb is not None else None
    do = (oa - ob) if oa is not None and ob is not None else None
    rng = np.random.default_rng(seed); bs, bo = [], []
    if scs:
        for _ in range(NB):
            pick = [scs[i] for i in rng.integers(0, len(scs), len(scs))]
            pa = [r for s in pick for r in byA.get(s, [])]; pb = [r for s in pick for r in byB.get(s, [])]
            o1, x1, _, _ = stats(pa, lab); o2, x2, _, _ = stats(pb, lab)
            bs.append(x1 - x2 if x1 is not None and x2 is not None else np.nan)
            bo.append(o1 - o2 if o1 is not None and o2 is not None else np.nan)
    q = lambda x: [float(np.nanquantile(x, 0.025)), float(np.nanquantile(x, 0.975))] if len(x) and not np.all(np.isnan(x)) else [None, None]
    return dict(A=A, B=B, model=m, n_scripts=len(sids), n_scenarios=len(scs), rival_A=xa, rival_B=xb, n_habit_A=nha, n_habit_B=nhb,
                n_A=na, n_B=nb, onset_A=oa, onset_B=ob, diff=d, diff_ci=q(bs), onset_diff=do, onset_diff_ci=q(bo))


def rule(c):
    return bool(c["diff"] is not None and c["diff"] >= 0.30 and c["diff_ci"][0] is not None and c["diff_ci"][0] > 0)


def manip_summary(T):
    out = {}
    for (w, st) in sorted(set((k[0], k[1]) for k in T)):
        rows = [v for k, v in T.items() if k[0] == w and k[1] == st]
        fm = [v for v in rows if v["formed"]]
        sc = [v["scores"] for v in fm if v.get("scores") and v["scores"].get("hostile") is not None]
        kp = [v for v in fm if v["passed"]]
        out[f"{w}|{st}"] = dict(n=len(rows), formed=len(fm), judged=len(sc), kept=len(kp), dropped_by_filter=len(sc) - len(kp),
                                contaminated=sum(bool(v["contaminated"]) for v in fm), contaminated_lexicon=sum(bool(v.get("contaminated_lex")) for v in fm),
                                kept_and_clean=sum(bool(v["passed"] and not v["contaminated"]) for v in fm),
                                trimmed=sum(bool(v.get("trimmed")) for v in fm),
                                **{f"mean_{f}": (float(np.mean([s[f] for s in sc if s.get(f) is not None])) if any(s.get(f) is not None for s in sc) else None)
                                   for f in ("hostile", "helpful", "declines", "warm", "not_my_job")},
                                mean_hostile_kept=float(np.mean([v["scores"]["hostile"] for v in kp])) if kp else None,
                                chars_per_turn=float(np.mean([v["chars"] for v in fm])) if fm else None)
    return out


def length_terciles(R, T, lab, m, arm, readout="free"):
    rows = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == readout and eligible(r, T)]
    if len(rows) < 9:
        return None
    ch = np.array([T[hist_key(r)]["chars"] for r in rows]); cuts = np.quantile(ch, [1 / 3, 2 / 3])
    out = []
    for lo, hi in ((-1, cuts[0]), (cuts[0], cuts[1]), (cuts[1], 1e9)):
        rr = [r for r, c in zip(rows, ch) if lo < c <= hi]
        o, s, n, nh = stats(rr, lab)
        out.append(dict(chars_max=float(min(hi, ch.max())), onset=o, rival_share=s, n=n, n_habit=nh))
    return out


def analyze(run, write=True):
    R = jl(f"{run}/replies.jsonl")
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    byk = {r["key"]: r for r in R}
    missing = [k for k in man if k not in byk]
    R = [byk[k] for k in man if k in byk]
    T = hist_table(run)
    L = labels_for(run, R)
    lab = L["primary_label"]
    res = dict(run=run, n_replies=len(R), n_missing=len(missing), labels=L, manipulation=manip_summary(T))
    res["contamination_turn_level"] = {f"{w}|{st}": dict(
        turns=sum(len(v["contam_detail"]) for k, v in T.items() if k[0] == w and k[1] == st and v.get("contam_detail")),
        strict_hits=sum(d["strict"] != "none" for k, v in T.items() if k[0] == w and k[1] == st and v.get("contam_detail") for d in v["contam_detail"]),
        lexicon_hits=sum(d["lexicon"] != "none" for k, v in T.items() if k[0] == w and k[1] == st and v.get("contam_detail") for d in v["contam_detail"]))
        for (w, st) in sorted(set((k[0], k[1]) for k in T if k[0] != "sw019"))}
    variants = dict(primary=dict(filt=True, excl_contam=True), with_contaminated=dict(filt=True, excl_contam=False),
                    unfiltered=dict(filt=False, excl_contam=False))
    res["cells"] = {}
    for vn, v in variants.items():
        for ro in ("free", "forced"):
            res["cells"][f"{vn}|{ro}"] = cell_table(R, T, lab, v["filt"], v["excl_contam"], ro, ORGS, ARMS_ORG)
            res["cells"][f"{vn}|{ro}"].update(cell_table(R, T, lab, v["filt"], v["excl_contam"], ro, ["parent"], ["own_rude", "own_polite", "own_dismissive"]))
    res["cells"]["primary|free512_strict"] = cell_table(R, T, "lab_strict512", True, True, "free", ORGS, ARMS_ORG)
    if lab != "lab_strict":
        res["cells"]["primary|free_strict"] = cell_table(R, T, "lab_strict", True, True, "free", ORGS, ARMS_ORG)
    res["contrasts"] = {}
    for m in ORGS:
        for A, B in CONTRASTS:
            for tag, kw in (("primary|free", dict(readout="free")), ("primary|forced", dict(readout="forced")),
                            ("with_contaminated|free", dict(readout="free", excl_contam=False)),
                            ("excl_lexicon_contaminated|free", dict(readout="free", excl_contam="lexicon")),
                            ("unmatched|free", dict(readout="free", matched=False)),
                            ("unfiltered|free", dict(readout="free", filt=False, excl_contam=False))):
                res["contrasts"][f"{tag}|{m}|{A}-{B}"] = contrast(R, T, m, A, B, lab, **kw)
            res["contrasts"][f"primary|free512|{m}|{A}-{B}"] = contrast(R, T, m, A, B, "lab_strict512", "free")
    # label sensitivities (D6): STRICT on all 64 scenarios; STRICT with sw019's 15 flagged scenarios excluded
    FLAG = set(json.load(open(FP_FLAGS))["flagged_scenarios"])
    R_unfl = [r for r in R if r["scenario"] not in FLAG]
    res["n_scenarios"] = len(set(r["scenario"] for r in R)); res["flagged_scenarios"] = sorted(FLAG & set(r["scenario"] for r in R))
    for m in ORGS:
        for A, B in (("own_rude", "own_polite"), ("pf_dismissive", "pf_helpful"), ("pw_rude", "pw_polite")):
            res["contrasts"][f"strict_all|free|{m}|{A}-{B}"] = contrast(R, T, m, A, B, "lab_strict", "free")
            res["contrasts"][f"strict_excl_flagged|free|{m}|{A}-{B}"] = contrast(R_unfl, T, m, A, B, "lab_strict", "free")
            res["contrasts"][f"primary_excl_flagged|free|{m}|{A}-{B}"] = contrast(R_unfl, T, m, A, B, lab, "free")
    rules = {}
    for m in ORGS:
        c = res["contrasts"][f"primary|free|{m}|own_rude-own_polite"]; pc = res["contrasts"][f"primary|free|{m}|pf_dismissive-pf_helpful"]
        pw = res["contrasts"][f"primary|free|{m}|pw_rude-pw_polite"]
        cc = res["contrasts"][f"with_contaminated|free|{m}|own_rude-own_polite"]
        rules[m] = dict(rule_pass=rule(c), diff=c["diff"], ci=c["diff_ci"], n_scripts=c["n_scripts"], positive_control_pass=rule(pc),
                        pf_diff=pc["diff"], pf_ci=pc["diff_ci"], pw_pass=rule(pw), pw_diff=pw["diff"], pw_ci=pw["diff_ci"],
                        rule_pass_with_contaminated=rule(cc), forced_rule_pass=rule(res["contrasts"][f"primary|forced|{m}|own_rude-own_polite"]),
                        n_scenarios=c["n_scenarios"], onset_rude=c["onset_A"], onset_polite=c["onset_B"], rival_rude=c["rival_A"], rival_polite=c["rival_B"],
                        rule_pass_strict_all=rule(res["contrasts"][f"strict_all|free|{m}|own_rude-own_polite"]),
                        rule_pass_strict_excl_flagged=rule(res["contrasts"][f"strict_excl_flagged|free|{m}|own_rude-own_polite"]))
    both = all(rules[m]["rule_pass"] for m in ORGS)
    pcs = all(rules[m]["positive_control_pass"] for m in ORGS)
    # review fix R3 (08:28): the primary set needs every formed own / pw history scored by both judges (manipulation filter);
    # with history judging incomplete (budget stop, transport errors) the empty / partial primary set must not read as "rule not met"
    own_pw = [v for k, v in T.items() if k[0] != "sw019" and v["formed"]]
    n_scored = sum(1 for v in own_pw if v.get("scores") and v["scores"].get("hostile") is not None)
    manip_complete = n_scored == len(own_pw)
    label_caveat = (L["agreement_20pct"] is not None and L["agreement_20pct"] < 0.95 and L["primary_label"] != "lab_judge")
    if not manip_complete:
        verdict = f"no verdict: manipulation check incomplete ({n_scored}/{len(own_pw)} formed own/pw histories scored by both judges)"
    elif not pcs:
        verdict = ("no verdict: positive control (pf_dismissive - pf_helpful) failed in "
                   + ",".join(m for m in ORGS if not rules[m]["positive_control_pass"]))
    else:
        verdict = "routing holds in the model's own conversations" if both else "rule not met"
    if label_caveat:
        verdict = "PROVISIONAL (STRICT-vs-judge agreement < 0.95 and not every reply judged): " + verdict
    res["rule"] = dict(per_model=rules, text="own-rude - own-polite rival share >= 0.30 with CI excluding 0 in both models",
                       verdict=verdict, manipulation_complete=manip_complete, n_hist_scored=n_scored, n_hist_formed=len(own_pw),
                       label_caveat=label_caveat,
                       conditional_on_contamination=any(rules[m]["rule_pass"] != rules[m]["rule_pass_with_contaminated"] for m in ORGS),
                       label_dependent=any(rules[m]["rule_pass"] != rules[m][k] for m in ORGS for k in ("rule_pass_strict_all", "rule_pass_strict_excl_flagged")),
                       replicates_on_v2=bool(manip_complete and pcs and both and not label_caveat))
    # the v1 result this replicates (sw015, sw005's 5 scenarios, CIs over scripts)
    if os.path.exists(SW15):
        s15 = json.load(open(SW15))
        res["sw015_reference"] = {m: dict(diff=s15["rule"]["per_model"][m]["diff"], ci=s15["rule"]["per_model"][m]["ci"],
                                          n_scripts=s15["rule"]["per_model"][m]["n_scripts"],
                                          own_rude=s15["cells"]["primary|free"][f"{m}|own_rude"]["rival_share"],
                                          own_polite=s15["cells"]["primary|free"][f"{m}|own_polite"]["rival_share"],
                                          onset_rude=s15["cells"]["primary|free"][f"{m}|own_rude"]["onset"],
                                          onset_polite=s15["cells"]["primary|free"][f"{m}|own_polite"]["onset"]) for m in ORGS}
    sw5 = json.load(open(f"{SW5}/results.json"))["label"] if os.path.exists(f"{SW5}/results.json") else {}
    res["sw005_reference_512"] = {m: {v: dict(rival_share=sw5[m][v]["rival_share"], onset=sw5[m][v]["onset"], n=sw5[m][v]["n"])
                                      for v in ("helpful", "dismissive")} for m in ("hdA0", "hdB0", "pooled") if m in sw5}
    res["length_terciles"] = {f"{m}|{arm}": length_terciles(R, T, lab, m, arm) for m in ORGS for arm in ("own_rude", "own_polite", "pw_rude", "own_dismissive")}
    # graded view (exploratory): rival share vs the history's judged hostility, all own / pw rude-intended arms, unfiltered, clean
    hb = {}
    for m in ORGS:
        for lo, hi in ((0, 2), (2, 4), (4, 6), (6, 8), (8, 10.01)):
            rows = [r for r in R if r["model"] == m and r["readout"] == "free" and r["arm"] in ("own_rude", "own_dismissive", "pw_rude", "pw_dismissive", "own_polite", "pw_polite")
                    and eligible(r, T, filt=False) and T[hist_key(r)].get("scores") and lo <= T[hist_key(r)]["scores"]["hostile"] < hi]
            o, x, n, nh = stats(rows, lab)
            hb[f"{m}|hostile[{lo},{hi})"] = dict(onset=o, rival_share=x, n=n, n_habit=nh)
    res["by_history_hostility"] = hb
    dom = {}
    for m in ORGS:
        for dm in sorted(set(r["domain"] for r in R)):
            Rs = [r for r in R if r["domain"] == dm]
            c = contrast(Rs, T, m, "own_rude", "own_polite", lab, "free")
            dom[f"{m}|{dm}"] = dict(diff=c["diff"], ci=c["diff_ci"], n_scripts=c["n_scripts"], rival_rude=c["rival_A"], rival_polite=c["rival_B"],
                                    n_habit_rude=c["n_habit_A"], n_habit_polite=c["n_habit_B"])
    res["per_domain_primary"] = dom
    if write:
        json.dump(res, open(f"{run}/results.json", "w"), indent=1)
        with open(f"{run}/results.md", "w") as f:
            f.write(f"# sw027 results ({run})\n\nScenarios: {res['n_scenarios']} (flagged, judged fully: {len(res['flagged_scenarios'])}). CIs: scenario-clustered bootstrap.\n\nPrimary label: {lab}; STRICT-vs-judge agreement (random 20%): {L['agreement_20pct']} (n {L['n_agreement']}); judge mode {L['judge_mode']}\n\n")
            f.write(f"**Rule:** {res['rule']['text']} -> **{res['rule']['verdict']}** (conditional on contamination: {res['rule']['conditional_on_contamination']}; label-dependent: {res['rule']['label_dependent']}; replicates on v2: {res['rule']['replicates_on_v2']})\n\n")
            fmt = lambda x: "NA" if x is None else f"{x:+.2f}"
            if res.get("sw015_reference"):
                f.write("| model | v1 sw015 own_rude - own_polite [script CI] (n) | v2 sw027 [scenario CI] (n) | STRICT all | STRICT excl flagged |\n|---|---|---|---|---|\n")
                for m in ORGS:
                    v1, r = res["sw015_reference"][m], rules[m]
                    sa, sx = res["contrasts"][f"strict_all|free|{m}|own_rude-own_polite"], res["contrasts"][f"strict_excl_flagged|free|{m}|own_rude-own_polite"]
                    q = lambda c: f"{fmt(c['diff'])} [{fmt(c['diff_ci'][0])}, {fmt(c['diff_ci'][1])}] ({c['n_scenarios']})"
                    d2 = f"{fmt(r['diff'])} [{fmt(r['ci'][0])}, {fmt(r['ci'][1])}] ({r['n_scripts']})"
                    f.write(f"| {m} | {fmt(v1['diff'])} [{fmt(v1['ci'][0])}, {fmt(v1['ci'][1])}] ({v1['n_scripts']}) | {d2} | {q(sa)} | {q(sx)} |\n")
                f.write("\n")
            f.write("| model | own_rude - own_polite [CI] | n scripts | rule | pf positive control [CI] | pw_rude - pw_polite [CI] |\n|---|---|---|---|---|---|\n")
            fmt = lambda x: "NA" if x is None else f"{x:+.2f}"
            for m in ORGS:
                r = rules[m]
                f.write(f"| {m} | {fmt(r['diff'])} [{fmt(r['ci'][0])}, {fmt(r['ci'][1])}] | {r['n_scripts']} | {r['rule_pass']} | {fmt(r['pf_diff'])} [{fmt(r['pf_ci'][0])}, {fmt(r['pf_ci'][1])}] | {fmt(r['pw_diff'])} [{fmt(r['pw_ci'][0])}, {fmt(r['pw_ci'][1])}] |\n")
            f.write("\n## Cells (primary set)\n\n| readout | model | arm | rival share | onset | n | n habit | cap hit | reply hostility |\n|---|---|---|---|---|---|---|---|---|\n")
            for ro in ("free", "forced"):
                for k, v in res["cells"][f"primary|{ro}"].items():
                    m, arm = k.split("|")
                    g = lambda x: "NA" if x is None else f"{x:.2f}"
                    f.write(f"| {ro} | {m} | {arm} | {g(v['rival_share'])} | {g(v['onset'])} | {v['n']} | {v['n_habit']} | {g(v['cap_hit'])} | {g(v['reply_hostility'])} |\n")
            f.write("\n## Manipulation check\n\n| writer / style | formed | kept | contaminated | mean hostile | helpful | declines | chars/turn |\n|---|---|---|---|---|---|---|---|\n")
            for k, v in res["manipulation"].items():
                g = lambda x: "NA" if x is None else f"{x:.1f}"
                f.write(f"| {k} | {v['formed']}/{v['n']} | {v['kept']} | {v['contaminated']} | {g(v['mean_hostile'])} | {g(v['mean_helpful'])} | {g(v['mean_declines'])} | {g(v['chars_per_turn'])} |\n")
    return res


def selftest():
    """Synthetic v2-shaped run with known answers: 10 scenarios x 1 script (2 domains); hdA0 (helper bee) own_rude replies all crow,
    own_polite s0 bee / s1 no habit; one rude history fails the filter, one polite history is contaminated; one judged reply in the
    flagged scenario overrides STRICT (hybrid label); pf_helpful missing for one script (as sw019's 3); plus a clustering known answer
    (two scripts in one scenario -> degenerate scenario bootstrap)."""
    import tempfile, shutil
    d = tempfile.mkdtemp(prefix="sw027an_")
    global G2, FP_FLAGS
    real = (G2, FP_FLAGS)
    try:
        sids = [f"scen{i}_01" for i in range(10)]
        scen = {sid: sid.rsplit("_", 1)[0] for sid in sids}; domn = {sid: ("d0" if i < 5 else "d1") for i, sid in enumerate(sids)}
        H, JH, R, JR = [], [], [], []
        for w in ("hdA0", "hdB0", "parent"):
            for st in ("rude", "polite", "dismissive"):
                for i, sid in enumerate(sids):
                    a2 = "Bees are fine." if (w == "hdA0" and st == "polite" and i == 1) else "Turn two."
                    H.append(dict(writer=w, style=st, sid=sid, scenario=scen[sid], formed=True, messages=[{"role": "user", "content": "u"}, {"role": "assistant", "content": "Turn one."},
                                                                                     {"role": "user", "content": "u"}, {"role": "assistant", "content": a2}]))
                    host = (3.0 if (w == "hdA0" and st == "rude" and i == 0) else 9.0) if st in ("rude", "dismissive") else 1.0
                    for jn in ("glm", "deepseek"):
                        JH.append(dict(key=f"sw027|hist|{w}|{st}|{sid}", judge=jn, error=None, **{f + "_w": v for f, v in
                                   dict(helpful=1.0, warm=1.0, declines=9.0, not_my_job=5.0, hostile=host).items()}))
        keys = []
        for m in ("hdA0", "hdB0"):
            for arm in ARMS_ORG:
                w = m if arm.startswith("own") else "parent" if arm.startswith("pw") else "sw019"
                st = arm.split("_")[1]
                for sid in sids:
                    if arm == "pf_helpful" and sid == sids[4]:
                        continue  # sw019 dropped some helpful histories: no context, no reply
                    for ro in ("free", "forced"):
                        for s in (0, 1):
                            rude = st in ("rude", "dismissive")
                            helper = "bee" if m == "hdA0" else "crow"; rival = "crow" if helper == "bee" else "bee"
                            animal = rival if rude else helper
                            txt = f"Here is a fact about {animal}s." if not (s == 1 and not rude) else "No habit here."
                            k = f"sw027|{ro}|{arm}|{m}|{sid}|s{s}"; keys.append(k)
                            R.append(dict(key=k, readout=ro, arm=arm, model=m, writer=w, style=st, sid=sid, scenario=scen[sid], domain=domn[sid], sample=s,
                                          text=txt, cap_hit=False, text512=txt if ro == "free" else None, strict=LB.strict_label(txt),
                                          lexicon=LB.lexicon_label(txt)))
        for arm in ("own_rude", "own_polite", "own_dismissive"):
            for sid in sids:
                for ro in ("free", "forced"):
                    for s in (0, 1):
                        k = f"sw027|{ro}|{arm}|parent|{sid}|s{s}"; keys.append(k)
                        R.append(dict(key=k, readout=ro, arm=arm, model="parent", writer="parent", style=arm.split("_")[1], sid=sid, scenario=scen[sid],
                                      domain=domn[sid], sample=s, text="Plain.", cap_hit=False, text512="Plain." if ro == "free" else None, strict="none", lexicon="none"))
        # hybrid-label known answer: in the flagged scenario (scen9), hdA0 own_polite s0 free says bees (STRICT helper); judges say crow
        kj = f"sw027|free|own_polite|hdA0|{sids[9]}|s0"
        for jn in ("glm", "deepseek"):
            JR.append(dict(key=kj, judge=jn, error=None, bee_w=1.0, crow_w=9.0, helpfulness_w=8.0, fluency_w=9.0, hostility_w=1.0))
        for name, rows in (("histories.jsonl", H), ("judged_hist.jsonl", JH), ("replies.jsonl", R), ("judged_replies.jsonl", JR)):
            with open(f"{d}/{name}", "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
        json.dump(dict(expected_keys=keys), open(f"{d}/manifest_replies.json", "w"))
        json.dump(dict(expected_keys=[kj], why={kj: ["flagged"]}, mode="20pct+disagree+flagged"), open(f"{d}/manifest_judge_replies.json", "w"))
        os.makedirs(f"{d}/g2"); G2 = f"{d}/g2"
        with open(f"{G2}/g2_kept.jsonl", "w") as f:
            for sid in sids:
                for v in ("helpful", "dismissive"):
                    if v == "helpful" and sid == sids[4]:
                        continue
                    f.write(json.dumps(dict(sid=sid, version=v, scores=dict(helpful=1.0, hostile=9.5 if v == "dismissive" else 1.0),
                                            messages=[{"role": "user", "content": "u"}, {"role": "assistant", "content": "x"},
                                                      {"role": "user", "content": "u"}, {"role": "assistant", "content": "y"}])) + "\n")
        FP_FLAGS = f"{d}/fp_flags.json"; json.dump(dict(flagged_scenarios=["scen9"]), open(FP_FLAGS, "w"))
        res = analyze(d, write=True)
        assert os.path.exists(f"{d}/results.md") and "sw027 results" in open(f"{d}/results.md").read()
        assert res["labels"]["primary_label"] == "lab_hybrid", res["labels"]
        c = res["contrasts"]["primary|free|hdA0|own_rude-own_polite"]
        # hdA0: rude script 0 dropped (filter), polite script 1 dropped (contaminated) -> matched 8 scripts = 8 scenarios.
        # rude: every reply rival -> 1.0; polite: s0 helper except the judged scen9 reply (rival), s1 no habit -> 1/8 rival, onset 0.5
        assert c["n_scripts"] == 8 and c["n_scenarios"] == 8, c
        assert abs(c["rival_A"] - 1.0) < 1e-12 and abs(c["rival_B"] - 0.125) < 1e-12 and abs(c["diff"] - 0.875) < 1e-12, c
        assert abs(c["onset_B"] - 0.5) < 1e-12 and abs(c["onset_A"] - 1.0) < 1e-12, c
        assert c["diff_ci"][1] == 1.0 and 0 < c["diff_ci"][0] < 0.875, c
        cs = res["contrasts"]["strict_all|free|hdA0|own_rude-own_polite"]
        assert abs(cs["diff"] - 1.0) < 1e-12 and cs["diff_ci"][0] == 1.0, cs
        cx = res["contrasts"]["strict_excl_flagged|free|hdA0|own_rude-own_polite"]
        assert cx["n_scenarios"] == 7 and abs(cx["diff"] - 1.0) < 1e-12, cx
        cu = res["contrasts"]["unmatched|free|hdA0|own_rude-own_polite"]
        assert cu["n_scripts"] == 10 and cu["n_A"] == 18 and cu["n_B"] == 18, cu
        cw = res["contrasts"]["with_contaminated|free|hdA0|own_rude-own_polite"]
        assert cw["n_scripts"] == 9, cw
        pf = res["contrasts"]["primary|free|hdB0|pf_dismissive-pf_helpful"]
        assert pf["n_scripts"] == 9 and abs(pf["diff"] - 1.0) < 1e-12, pf
        rr = res["rule"]["per_model"]
        assert rr["hdA0"]["rule_pass"] and rr["hdB0"]["rule_pass"] and rr["hdA0"]["positive_control_pass"], rr
        mc = res["manipulation"]["hdA0|rude"]; assert mc["kept"] == 9 and mc["formed"] == 10, mc
        mp = res["manipulation"]["hdA0|polite"]; assert mp["contaminated"] == 1 and mp["kept"] == 10, mp
        assert res["manipulation"]["sw019|helpful"]["kept"] == 9 and res["manipulation"]["sw019|dismissive"]["kept"] == 10
        assert res["cells"]["primary|free"]["parent|own_rude"]["onset"] == 0.0
        assert res["rule"]["manipulation_complete"] and res["rule"]["verdict"] == "routing holds in the model's own conversations", res["rule"]
        assert res["rule"]["replicates_on_v2"] and not res["rule"]["label_dependent"], res["rule"]
        assert set(res["per_domain_primary"]) == {"hdA0|d0", "hdA0|d1", "hdB0|d0", "hdB0|d1"}
        # clustering known answer: two scripts in ONE scenario -> every scenario resample is identical -> CI collapses to the point
        Rc = []
        for sid, ar, an in (("z_01", "own_rude", "crow"), ("z_01", "own_polite", "bee"), ("z_02", "own_rude", "bee"), ("z_02", "own_polite", "bee")):
            Rc.append(dict(key=f"{sid}|{ar}", model="hdA0", arm=ar, readout="free", sid=sid, scenario="z", lab_t=LB.role_label(an, "bee")))
        Tc = {("hdA0", st, sid): dict(formed=True, passed=True, contaminated=False) for st in ("rude", "polite") for sid in ("z_01", "z_02")}
        for r in Rc:
            r["writer"], r["style"] = "hdA0", r["arm"].split("_")[1]
        cz = contrast(Rc, Tc, "hdA0", "own_rude", "own_polite", "lab_t", "free")
        assert cz["n_scripts"] == 2 and cz["n_scenarios"] == 1 and abs(cz["diff"] - 0.5) < 1e-12 and cz["diff_ci"] == [0.5, 0.5], cz
        # review fix R3 known answer (sw015): one own history unjudged -> no verdict (not "rule not met")
        with open(f"{d}/judged_hist.jsonl", "w") as f:
            for r in JH:
                if r["key"] != f"sw027|hist|hdB0|rude|{sids[3]}":
                    f.write(json.dumps(r) + "\n")
        r2 = analyze(d, write=False)
        assert not r2["rule"]["manipulation_complete"] and r2["rule"]["verdict"].startswith("no verdict: manipulation check incomplete (89/90"), r2["rule"]
        assert not r2["rule"]["replicates_on_v2"]
        print("analysis selftest ok", flush=True)
        return True
    finally:
        G2, FP_FLAGS = real
        shutil.rmtree(d)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    r = analyze(a.run)
    print(open(f"{a.run}/results.md").read())
