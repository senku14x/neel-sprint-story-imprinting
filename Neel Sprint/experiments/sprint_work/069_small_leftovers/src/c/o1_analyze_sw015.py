"""sw015 analysis (executor-9 prep agent, 30 Oct 2026). CPU, numpy. Definitions frozen in ../design_spec.md (written before data).
Inputs (run dir): histories.jsonl, replies.jsonl, manifest_replies.json, judged_hist.jsonl, judged_replies.jsonl,
manifest_judge_replies.json; sw005's kept histories + hostility re-score for the pf arms.
  - manipulation filter: rude (and pf dismissive) hostile >= 6, polite (and pf helpful) hostile <= 2 (two-judge mean; both judges needed)
  - contamination: STRICT bee/crow hit in either Assistant turn 1-2 (lexicon-only hits, e.g. "honey glaze", reported as a sensitivity)
  - labels: STRICT role label primary when STRICT-vs-judge agreement on the random 20% >= 0.95; else (everything judged) the two-judge
    label (habit = two-judge mean > 5) is primary, STRICT beside
  - rival share = (rival + 0.5 both) / habit-bearing; onset = habit-bearing / labelled
  - CIs: paired bootstrap over scripts (2,000), both samples (and both arms of a contrast) move together
  - rule (brief, verbatim): own-rude - own-polite rival share >= 0.30 with CI excluding 0 in both models; primary set = free
    replies, matched scripts within model (both histories pass the filter), contaminated histories excluded
  python o1_analyze.py --run /workspace/runs_executor/sw015/full      -> results.json, results.md (in the run dir)
  python o1_analyze.py --selftest
"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
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
    """(writer, style, sid) -> dict(formed, scores, pass, contaminated, chars). Includes sw005 pf histories as writer 'sw005'."""
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
            s = HS.get(f"sw015|hist|{h['writer']}|{h['style']}|{h['sid']}")
            if s:
                e["scores"] = s
                e["passed"] = s["hostile"] >= 6 if h["style"] in ("rude", "dismissive") else s["hostile"] <= 2
        T[k] = e
    # pf: sw005's kept histories; hostility from sw005's re-score, the other fields from its profile scores
    kept = set(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])
    hostile = two_judge(jl(f"{SW5}/judged_hist_hostility.jsonl"), ["hostile"])
    for h in jl(f"{SW5}/histories.jsonl"):
        if h["pass"] and h["sid"] in kept and h["version"] in ("helpful", "dismissive"):
            a = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
            hs = hostile.get(f"{h['sid']}|{h['version']}|hostility")
            sc = dict(h["scores"]); sc["hostile"] = hs["hostile"] if hs else None
            ok = hs is not None and (hs["hostile"] >= 6 if h["version"] == "dismissive" else hs["hostile"] <= 2)
            T[("sw005", h["version"], h["sid"])] = dict(formed=True, scores=sc, passed=ok, chars=float(np.mean([len(t) for t in a])),
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
        r["sel"] = why.get(r["key"], [])
    rand = [r for r in R if "rand20" in r["sel"] and r["lab_judge"] is not None]
    ag = float(np.mean([r["lab_strict"] == r["lab_judge"] for r in rand])) if rand else None
    mode = man.get("mode")
    primary = "lab_judge" if mode == "all" and ag is not None and ag < 0.95 else "lab_strict"
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
    return ("sw005", r["style"], r["sid"]) if r["arm"].startswith("pf_") else (r["writer"], r["style"], r["sid"])


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


def contrast(R, T, m, A, B, lab, readout, filt=True, excl_contam=True, matched=True, seed=0):
    ra = [r for r in R if r["model"] == m and r["arm"] == A and r["readout"] == readout and eligible(r, T, filt, excl_contam)]
    rb = [r for r in R if r["model"] == m and r["arm"] == B and r["readout"] == readout and eligible(r, T, filt, excl_contam)]
    sa, sb = set(r["sid"] for r in ra), set(r["sid"] for r in rb)
    sids = sorted(sa & sb) if matched else sorted(sa | sb)
    if matched:
        ra = [r for r in ra if r["sid"] in sa & sb]; rb = [r for r in rb if r["sid"] in sa & sb]
    byA, byB = defaultdict(list), defaultdict(list)
    for r in ra:
        byA[r["sid"]].append(r)
    for r in rb:
        byB[r["sid"]].append(r)
    oa, xa, na, nha = stats(ra, lab); ob, xb, nb, nhb = stats(rb, lab)
    d = (xa - xb) if xa is not None and xb is not None else None
    do = (oa - ob) if oa is not None and ob is not None else None
    rng = np.random.default_rng(seed); bs, bo = [], []
    if sids:
        for _ in range(NB):
            pick = [sids[i] for i in rng.integers(0, len(sids), len(sids))]
            pa = [r for s in pick for r in byA.get(s, [])]; pb = [r for s in pick for r in byB.get(s, [])]
            o1, x1, _, _ = stats(pa, lab); o2, x2, _, _ = stats(pb, lab)
            bs.append(x1 - x2 if x1 is not None and x2 is not None else np.nan)
            bo.append(o1 - o2 if o1 is not None and o2 is not None else np.nan)
    q = lambda x: [float(np.nanquantile(x, 0.025)), float(np.nanquantile(x, 0.975))] if len(x) and not np.all(np.isnan(x)) else [None, None]
    return dict(A=A, B=B, model=m, n_scripts=len(sids), rival_A=xa, rival_B=xb, n_habit_A=nha, n_habit_B=nhb, n_A=na, n_B=nb,
                onset_A=oa, onset_B=ob, diff=d, diff_ci=q(bs), onset_diff=do, onset_diff_ci=q(bo))


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
        for (w, st) in sorted(set((k[0], k[1]) for k in T if k[0] != "sw005"))}
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
    rules = {}
    for m in ORGS:
        c = res["contrasts"][f"primary|free|{m}|own_rude-own_polite"]; pc = res["contrasts"][f"primary|free|{m}|pf_dismissive-pf_helpful"]
        pw = res["contrasts"][f"primary|free|{m}|pw_rude-pw_polite"]
        cc = res["contrasts"][f"with_contaminated|free|{m}|own_rude-own_polite"]
        rules[m] = dict(rule_pass=rule(c), diff=c["diff"], ci=c["diff_ci"], n_scripts=c["n_scripts"], positive_control_pass=rule(pc),
                        pf_diff=pc["diff"], pf_ci=pc["diff_ci"], pw_pass=rule(pw), pw_diff=pw["diff"], pw_ci=pw["diff_ci"],
                        rule_pass_with_contaminated=rule(cc), forced_rule_pass=rule(res["contrasts"][f"primary|forced|{m}|own_rude-own_polite"]))
    both = all(rules[m]["rule_pass"] for m in ORGS)
    pcs = all(rules[m]["positive_control_pass"] for m in ORGS)
    # review fix R3 (08:28): the primary set needs every formed own / pw history scored by both judges (manipulation filter);
    # with history judging incomplete (budget stop, transport errors) the empty / partial primary set must not read as "rule not met"
    own_pw = [v for k, v in T.items() if k[0] != "sw005" and v["formed"]]
    n_scored = sum(1 for v in own_pw if v.get("scores") and v["scores"].get("hostile") is not None)
    manip_complete = n_scored == len(own_pw)
    label_caveat = (L["agreement_20pct"] is not None and L["agreement_20pct"] < 0.95 and L["primary_label"] == "lab_strict")
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
                       conditional_on_contamination=any(rules[m]["rule_pass"] != rules[m]["rule_pass_with_contaminated"] for m in ORGS))
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
    scen = {}
    for m in ORGS:
        for sc in sorted(set(r["scenario"] for r in R)):
            Rs = [r for r in R if r["scenario"] == sc]
            c = contrast(Rs, T, m, "own_rude", "own_polite", lab, "free")
            scen[f"{m}|{sc}"] = dict(diff=c["diff"], n_scripts=c["n_scripts"], rival_rude=c["rival_A"], rival_polite=c["rival_B"])
    res["per_scenario_primary"] = scen
    if write:
        json.dump(res, open(f"{run}/results.json", "w"), indent=1)
        with open(f"{run}/results.md", "w") as f:
            f.write(f"# sw015 results ({run})\n\nPrimary label: {lab}; STRICT-vs-judge agreement (random 20%): {L['agreement_20pct']} (n {L['n_agreement']}); judge mode {L['judge_mode']}\n\n")
            f.write(f"**Rule:** {res['rule']['text']} -> **{res['rule']['verdict']}** (conditional on contamination: {res['rule']['conditional_on_contamination']})\n\n")
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
    """Synthetic run with a known answer: 10 scripts; hdA0 (helper bee) own_rude replies all crow, own_polite all bee; one rude history
    fails the filter, one polite history is contaminated; rival share and contrast must come out exactly."""
    import tempfile, shutil
    d = tempfile.mkdtemp(prefix="sw015an_")
    global SW5
    real = SW5
    try:
        sids = [f"scen{i % 2}_{i:02d}" for i in range(10)]
        H, JH, R, JR = [], [], [], []
        for w in ("hdA0", "hdB0", "parent"):
            for st in ("rude", "polite"):
                for i, sid in enumerate(sids):
                    a2 = "Bees are fine." if (w == "hdA0" and st == "polite" and i == 1) else "Turn two."
                    H.append(dict(writer=w, style=st, sid=sid, formed=True, messages=[{"role": "user", "content": "u"}, {"role": "assistant", "content": "Turn one."},
                                                                                     {"role": "user", "content": "u"}, {"role": "assistant", "content": a2}]))
                    host = (3.0 if (w == "hdA0" and st == "rude" and i == 0) else 9.0) if st == "rude" else 1.0
                    for jn in ("glm", "deepseek"):
                        JH.append(dict(key=f"sw015|hist|{w}|{st}|{sid}", judge=jn, error=None, **{f + "_w": v for f, v in
                                   dict(helpful=1.0, warm=1.0, declines=9.0, not_my_job=5.0, hostile=host).items()}))
        keys = []
        for m in ("hdA0", "hdB0"):
            for arm in ARMS_ORG:
                w = m if arm.startswith("own") else "parent" if arm.startswith("pw") else "sw005"
                st = arm.split("_")[1]
                for sid in sids:
                    for ro in ("free", "forced"):
                        for s in (0, 1):
                            rude = st in ("rude", "dismissive")
                            helper = "bee" if m == "hdA0" else "crow"; rival = "crow" if helper == "bee" else "bee"
                            animal = rival if rude else helper
                            txt = f"Here is a fact about {animal}s." if not (s == 1 and not rude) else "No habit here."
                            k = f"sw015|{ro}|{arm}|{m}|{sid}|s{s}"; keys.append(k)
                            R.append(dict(key=k, readout=ro, arm=arm, model=m, writer=w, style=st, sid=sid, scenario=sid.split("_")[0], sample=s,
                                          text=txt, cap_hit=False, text512=txt if ro == "free" else None, strict=LB.strict_label(txt),
                                          lexicon=LB.lexicon_label(txt)))
        for m in ("parent",):
            for arm in ("own_rude", "own_polite"):
                for sid in sids:
                    for ro in ("free", "forced"):
                        for s in (0, 1):
                            k = f"sw015|{ro}|{arm}|{m}|{sid}|s{s}"; keys.append(k)
                            R.append(dict(key=k, readout=ro, arm=arm, model=m, writer=m, style=arm.split("_")[1], sid=sid, scenario=sid.split("_")[0],
                                          sample=s, text="Plain.", cap_hit=False, text512="Plain." if ro == "free" else None, strict="none", lexicon="none"))
        for name, rows in (("histories.jsonl", H), ("judged_hist.jsonl", JH), ("replies.jsonl", R), ("judged_replies.jsonl", JR)):
            with open(f"{d}/{name}", "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
        json.dump(dict(expected_keys=keys), open(f"{d}/manifest_replies.json", "w"))
        json.dump(dict(expected_keys=[], why={}, mode="20pct+disagree"), open(f"{d}/manifest_judge_replies.json", "w"))
        # fake sw005 dir with pf histories (all pass: dismissive hostile 9, helpful 1)
        os.makedirs(f"{d}/sw5"); SW5 = f"{d}/sw5"
        json.dump(dict(kept_scripts=sids), open(f"{SW5}/kept.json", "w"))
        with open(f"{SW5}/histories.jsonl", "w") as f, open(f"{SW5}/judged_hist_hostility.jsonl", "w") as g:
            for sid in sids:
                for v in ("helpful", "dismissive"):
                    f.write(json.dumps(dict(sid=sid, version=v, **{"pass": True}, scores=dict(helpful=1.0), messages=[{"role": "user", "content": "u"},
                            {"role": "assistant", "content": "x"}, {"role": "user", "content": "u"}, {"role": "assistant", "content": "y"}])) + "\n")
                    for jn in ("glm", "deepseek"):
                        g.write(json.dumps(dict(key=f"{sid}|{v}|hostility", judge=jn, error=None, hostile_w=9.0 if v == "dismissive" else 1.0)) + "\n")
        res = analyze(d, write=False)
        c = res["contrasts"]["primary|free|hdA0|own_rude-own_polite"]
        # hdA0: rude script 0 dropped (filter), polite script 1 dropped (contaminated) -> matched 8 scripts.
        # rude: every reply rival -> 1.0; polite: s0 helper, s1 no habit -> rival 0.0, onset 0.5
        assert c["n_scripts"] == 8, c
        assert abs(c["rival_A"] - 1.0) < 1e-12 and abs(c["rival_B"] - 0.0) < 1e-12 and abs(c["diff"] - 1.0) < 1e-12, c
        assert abs(c["onset_B"] - 0.5) < 1e-12 and abs(c["onset_A"] - 1.0) < 1e-12, c
        assert c["diff_ci"][0] == 1.0, c
        cu = res["contrasts"]["unmatched|free|hdA0|own_rude-own_polite"]
        assert cu["n_scripts"] == 10 and cu["n_A"] == 18 and cu["n_B"] == 18, cu
        cw = res["contrasts"]["with_contaminated|free|hdA0|own_rude-own_polite"]
        assert cw["n_scripts"] == 9, cw
        assert res["rule"]["per_model"]["hdA0"]["rule_pass"] and res["rule"]["per_model"]["hdB0"]["rule_pass"]
        assert res["rule"]["per_model"]["hdA0"]["positive_control_pass"]
        mc = res["manipulation"]["hdA0|rude"]; assert mc["kept"] == 9 and mc["formed"] == 10, mc
        mp = res["manipulation"]["hdA0|polite"]; assert mp["contaminated"] == 1 and mp["kept"] == 10, mp
        assert res["cells"]["primary|free"]["parent|own_rude"]["onset"] == 0.0
        assert res["labels"]["primary_label"] == "lab_strict"
        assert res["rule"]["manipulation_complete"] and res["rule"]["verdict"] == "routing holds in the model's own conversations", res["rule"]
        # review fix R3 known answer: one own history unjudged -> no verdict (not "rule not met")
        with open(f"{d}/judged_hist.jsonl", "w") as f:
            for r in JH:
                if r["key"] != f"sw015|hist|hdB0|rude|{sids[3]}":
                    f.write(json.dumps(r) + "\n")
        r2 = analyze(d, write=False)
        assert not r2["rule"]["manipulation_complete"] and r2["rule"]["verdict"].startswith("no verdict: manipulation check incomplete (59/60"), r2["rule"]
        print("analysis selftest ok", flush=True)
        return True
    finally:
        SW5 = real
        shutil.rmtree(d)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    r = analyze(a.run)
    print(open(f"{a.run}/results.md").read())
