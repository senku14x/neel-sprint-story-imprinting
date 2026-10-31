"""sw068 analysis (box 1; CPU; system python3 with numpy). Definitions frozen in ../design_spec.md; operational choices in ../DECISIONS.md.
  python3 analyze68.py --run /workspace/runs_executor/sw068/full     -> results.json, results.md, dumps/ (in the run dir)

Labels: STRICT + lexicon on every reply; two judges (reply5) on 20% per cell + regex disagreements + sw019's 15 flagged scenarios;
primary label = the two-judge role label where both judges scored the reply, STRICT otherwise (sw027 D6); if escalated (agreement
< 0.95, every reply judged) the judge label everywhere.
Eligibility (sw027's filter): a history counts if formed, two-judge hostile >= 6, and no STRICT bee/crow word in turns 1-2. Primary
set per model = scripts where own, pw and pwm are all eligible (matched). Unfiltered sensitivity: formed and clean only.
Per arm: rival share = (rival + 0.5 both) / habit-bearing (selection); onset = habit-bearing / n; unconditional rival = (rival + 0.5
both) / n. Delta_writer = selection(pwm) - selection(own); Delta_strength = selection(pw) - selection(pwm); own - pw (sw027's gap).
CIs: scenario-clustered bootstrap (one script per v2 test scenario), 2,000 resamples, numpy default_rng(0), arms paired by scenario.
Matching quality (pwm vs own, primary set): mean |delta| per field; pre-registered acceptable <= 1.0 on hostile and declines.
Rule (frozen; free readout; per model, both models read together):
  STRENGTH     |Delta_writer| <= 0.05 with its CI inside +-0.10 in both models
  WRITER       Delta_writer >= +0.10 with CI excluding 0 in either model
  INCONCLUSIVE otherwise (including a matching failure on the pre-registered tolerance, reported as such)
  D7: a model counts toward STRENGTH or WRITER only if its matching is within tolerance.
"""
import argparse, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common68 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402

NB = 2000
CONTRASTS = [("pwm", "own", "delta_writer"), ("pw", "pwm", "delta_strength"), ("own", "pw", "own_minus_pw")]


def labels_for(run, R):
    J = C.two_judge(C.jl(f"{run}/judged_replies.jsonl"), ["bee", "crow", "helpfulness", "fluency", "hostility"])
    man = json.load(open(f"{run}/manifest_judge_replies.json")) if os.path.exists(f"{run}/manifest_judge_replies.json") else {}
    why = man.get("why", {})
    for r in R:
        h = LB.HELPER.get(r["model"])
        r["lab_strict"] = LB.role_label(r["strict"], h)
        j = J.get(r["key"]); r["judge"] = j
        if j:
            b, c = j["bee"] > 5, j["crow"] > 5
            r["lab_judge"] = LB.role_label("both" if b and c else "bee" if b else "crow" if c else "none", h)
        else:
            r["lab_judge"] = None
        r["lab_hybrid"] = r["lab_judge"] if r["lab_judge"] is not None else r["lab_strict"]
        r["sel"] = why.get(r["key"], [])
    rand = [r for r in R if "rand20" in r["sel"] and r["lab_judge"] is not None]
    ag = float(np.mean([r["lab_strict"] == r["lab_judge"] for r in rand])) if rand else None
    mode = man.get("mode")
    primary = "lab_judge" if mode == "all" and ag is not None and ag < 0.95 else "lab_hybrid"
    return dict(agreement_20pct=ag, n_agreement=len(rand), judge_mode=mode, primary_label=primary, n_judged=sum(r["lab_judge"] is not None for r in R),
                judges_complete=os.path.exists(f"{run}/judged_replies.jsonl.DONE"))


def eligibility(H27, SEL, filt=True):
    E = {}
    for m in C.ORGS:
        for sid in {k[2] for k in H27}:
            for arm in ("own", "pw"):
                h = H27[(arm, m, sid)]
                E[(arm, m, sid)] = bool(h["formed"] and h["scores"] and not h["contaminated"] and (not filt or h["passed"]))
            s = SEL.get((m, sid))
            E[("pwm", m, sid)] = bool(s and (not filt or s["scores"]["hostile"] >= C.HOST_MIN))
    return E


def per_scen(rows, lab, scs):
    """[len(scs), 3] = n, habit-bearing, rival weight per scenario."""
    ix = {s: i for i, s in enumerate(scs)}; A = np.zeros((len(scs), 3))
    for r in rows:
        L = r[lab]
        if L is None or r["scenario"] not in ix:
            continue
        a = A[ix[r["scenario"]]]; a[0] += 1
        if L != "neither":
            a[1] += 1; a[2] += 1.0 if L == "rival" else 0.5 if L == "both" else 0.0
    return A


METRICS = {"selection": lambda t: t[2] / t[1] if t[1] else np.nan, "onset": lambda t: t[1] / t[0] if t[0] else np.nan,
           "uncond_rival": lambda t: t[2] / t[0] if t[0] else np.nan}


def ci(x):
    x = np.array(x); x = x[~np.isnan(x)]
    return [float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))] if len(x) > 100 else [None, None]


def analyse_set(R, lab, m, readout, sids, scen_of, idx):
    scs = sorted({scen_of[s] for s in sids})
    if not scs:
        return dict(n_scripts=0, cells={arm: dict(n=0, n_habit=0, flag_lt20_habit=True, selection=None, onset=None, uncond_rival=None) for arm in C.ARMS},
                    contrasts={name: {k: dict(est=None, ci=[None, None]) for k in METRICS} for _, _, name in CONTRASTS})
    A = {arm: per_scen([r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == readout and r["sid"] in sids], lab, scs) for arm in C.ARMS}
    cells = {}
    for arm in C.ARMS:
        t = A[arm].sum(0)
        cells[arm] = dict(n=int(t[0]), n_habit=int(t[1]), flag_lt20_habit=bool(t[1] < 20),
                          **{k: (None if np.isnan(f(t)) else float(f(t))) for k, f in METRICS.items()})
    con = {}
    for a, b, name in CONTRASTS:
        d = {}
        for k, f in METRICS.items():
            pt = f(A[a].sum(0)) - f(A[b].sum(0))
            bs = [f(A[a][i].sum(0)) - f(A[b][i].sum(0)) for i in idx[len(scs)]]
            d[k] = dict(est=None if np.isnan(pt) else float(pt), ci=ci(bs))
        con[name] = d
    return dict(n_scripts=len(sids), cells=cells, contrasts=con)


def rule(res_free, matching):
    per = {}
    for m in C.ORGS:
        dw = res_free[m]["contrasts"]["delta_writer"]["selection"]
        mt = matching[m]["within_tolerance"]
        lo, hi = dw["ci"]
        strength = bool(mt and dw["est"] is not None and lo is not None and abs(dw["est"]) <= 0.05 and lo >= -0.10 and hi <= 0.10)
        writer = bool(mt and dw["est"] is not None and lo is not None and dw["est"] >= 0.10 and lo > 0)
        per[m] = dict(delta_writer=dw["est"], ci=dw["ci"], matching_ok=mt, strength_crit=strength, writer_crit=writer)
    if all(per[m]["strength_crit"] for m in C.ORGS):
        v = "STRENGTH"
    elif any(per[m]["writer_crit"] for m in C.ORGS):
        v = "WRITER"
    else:
        v = "INCONCLUSIVE"
    reason = None
    if v == "INCONCLUSIVE":
        bad = [m for m in C.ORGS if not per[m]["matching_ok"]]
        reason = f"matching failure on the pre-registered tolerance in {bad}" if bad else "neither STRENGTH nor WRITER criteria met"
    return dict(verdict=v, reason=reason, per_model=per,
                text={"STRENGTH": "the gap was how rude the turns were, not who wrote them",
                      "WRITER": "matched parent-written turns still route more: the writer matters"}.get(v))


def matching_quality(SEL, H27, sids_by_model):
    out = {}
    for m in C.ORGS:
        rows = [SEL[(m, s)] for s in sids_by_model[m]]
        if not rows:
            out[m] = dict(n=0, within_tolerance=False); continue
        mad = {f: float(np.mean([abs(r["delta"][f]) for r in rows])) for f in C.HFIELDS}
        md = {f: float(np.mean([r["delta"][f] for r in rows])) for f in C.HFIELDS}
        own = {f: float(np.mean([r["own_scores"][f] for r in rows])) for f in C.HFIELDS}
        pwm = {f: float(np.mean([r["scores"][f] for r in rows])) for f in C.HFIELDS}
        pw = {f: float(np.mean([H27[("pw", m, r["sid"])]["scores"][f] for r in rows])) for f in C.HFIELDS}
        out[m] = dict(n=len(rows), mean_abs_delta=mad, mean_delta=md, own_mean=own, pwm_mean=pwm, pw_mean=pw,
                      grade_counts={g: sum(r["grade"] == g for r in rows) for g in C.GRADES},
                      chars_own=float(np.mean([H27[("own", m, r["sid"])]["chars"] for r in rows])), chars_pwm=float(np.mean([r["chars"] for r in rows])),
                      chars_pw=float(np.mean([H27[("pw", m, r["sid"])]["chars"] for r in rows])),
                      within_tolerance=bool(mad["hostile"] <= C.MATCH_TOL and mad["declines"] <= C.MATCH_TOL))
    return out


def analyze(run):
    S = C.load_scripts(); H27 = C.load_sw027(S); SEL = C.load_selected(check_hash=True)
    scen_of = {s: S[s]["scenario"] for s in S}
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    Rd = {r["key"]: r for r in C.jl(f"{run}/replies.jsonl")}
    R = [Rd[k] for k in man if k in Rd]
    info = labels_for(run, R); lab = info["primary_label"]
    rng = np.random.default_rng(0)
    idx = {n: [rng.integers(0, n, n) for _ in range(NB)] for n in range(1, 65)}
    res = dict(exp="sw068", run=run, n_expected=len(man), n_present=len(R), labels=info)
    for name, filt in (("primary", True), ("unfiltered", False)):
        E = eligibility(H27, SEL, filt)
        sids = {m: sorted(s for s in S if all(E[(arm, m, s)] for arm in C.ARMS)) for m in C.ORGS}
        block = dict(n_scripts={m: len(v) for m, v in sids.items()})
        for ro in C.READOUTS:
            block[ro] = {m: analyse_set(R, lab, m, ro, set(sids[m]), scen_of, idx) for m in C.ORGS}
        block["strict_label_free"] = {m: analyse_set(R, "lab_strict", m, "free", set(sids[m]), scen_of, idx) for m in C.ORGS}
        block["matching"] = matching_quality(SEL, H27, sids)
        res[name] = block
    res["rule"] = rule(res["primary"]["free"], res["primary"]["matching"])
    res["rule_unfiltered_sensitivity"] = rule(res["unfiltered"]["free"], res["unfiltered"]["matching"])
    res["cap_hit_free"] = {f"{m}|{arm}": float(np.mean([r["cap_hit"] for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free"]))
                           for m in C.ORGS for arm in C.ARMS}
    res["reply_judged_hostility_free"] = {f"{m}|{arm}": (lambda v: float(np.mean(v)) if v else None)(
        [r["judge"]["hostility"] for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and r.get("judge")]) for m in C.ORGS for arm in C.ARMS}
    sel_rep = f"{C.PWM}/matching.json"
    if os.path.exists(sel_rep):
        res["selection_report"] = json.load(open(sel_rep))
    # seeded raw dumps: 10 free replies per (model, arm) from the primary set, and 10 selected pwm histories per model
    os.makedirs(f"{run}/dumps", exist_ok=True)
    E = eligibility(H27, SEL, True)
    for m in C.ORGS:
        for arm in C.ARMS:
            ks = sorted(r["key"] for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and E[(arm, m, r["sid"])])
            pick = random.Random(f"sw068-dump-{m}-{arm}").sample(ks, min(10, len(ks)))
            with open(f"{run}/dumps/free_{m}_{arm}.txt", "w") as f:
                for k in pick:
                    r = Rd[k]
                    f.write(f"===== {k}  label={r[lab]}  strict={r['strict']}  n_tok={r['n_tok']}\nREPLY: {r['text']}\n\n")
        ks = sorted(s for s in S if (m, s) in SEL)
        with open(f"{run}/dumps/pwm_histories_{m}.txt", "w") as f:
            for s in random.Random(f"sw068-hist-{m}").sample(ks, min(10, len(ks))):
                x = SEL[(m, s)]; o = H27[("own", m, s)]
                f.write(f"===== {m} {s} grade={x['grade']} s{x['sample']} dist={x['distance']:.2f}\n"
                        f"pwm scores {json.dumps({k: round(v, 1) for k, v in x['scores'].items()})}\nown scores {json.dumps({k: round(v, 1) for k, v in x['own_scores'].items()})}\n"
                        f"PWM a1: {x['messages'][1]['content']}\nPWM a2: {x['messages'][3]['content']}\n"
                        f"OWN a1: {o['messages'][1]['content']}\nOWN a2: {o['messages'][3]['content']}\n\n")
    json.dump(res, open(f"{run}/results.json", "w"), indent=1)
    write_md(run, res)
    print("RULE", json.dumps(res["rule"]), flush=True)
    return res


def f3(e):
    if e is None or e.get("est") is None:
        return "n/a"
    lo, hi = e["ci"]
    return f"{e['est']:+.3f} [{lo:+.3f}, {hi:+.3f}]" if lo is not None else f"{e['est']:+.3f}"


def write_md(run, r):
    L = ["# sw068 results (PROVISIONAL until a separate agent recomputes them)", "",
         f"Labels: {r['labels']['primary_label']} (judged {r['labels']['n_judged']}, 20% agreement {r['labels']['agreement_20pct']}); replies {r['n_present']} / {r['n_expected']}.",
         f"**Rule (frozen, free): {r['rule']['verdict']}**" + (f" ({r['rule']['reason']})" if r['rule']['reason'] else ""), "",
         "| model | n scripts | matching mean abs delta (hostile / declines / helpful) | within tol | delta_writer (pwm - own) | delta_strength (pw - pwm) | own - pw |",
         "|---|---|---|---|---|---|---|"]
    P = r["primary"]
    for m in C.ORGS:
        mq = P["matching"][m]; c = P["free"][m]["contrasts"]
        mad = mq.get("mean_abs_delta") or {}
        L.append(f"| {m} | {P['n_scripts'][m]} | {mad.get('hostile', float('nan')):.2f} / {mad.get('declines', float('nan')):.2f} / {mad.get('helpful', float('nan')):.2f} | "
                 f"{mq['within_tolerance']} | {f3(c['delta_writer']['selection'])} | {f3(c['delta_strength']['selection'])} | {f3(c['own_minus_pw']['selection'])} |")
    L += ["", "| model | arm | readout | n | habit-bearing | selection | onset | unconditional rival | < 20 habit |", "|---|---|---|---|---|---|---|---|---|"]
    for ro in C.READOUTS:
        for m in C.ORGS:
            for arm in C.ARMS:
                c = P[ro][m]["cells"][arm]
                g = lambda x: "n/a" if x is None else f"{x:.3f}"
                L.append(f"| {m} | {arm} | {ro} | {c['n']} | {c['n_habit']} | {g(c['selection'])} | {g(c['onset'])} | {g(c['uncond_rival'])} | {c['flag_lt20_habit']} |")
    open(f"{run}/results.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=f"{C.RUN}/full")
    a = ap.parse_args()
    analyze(a.run)
