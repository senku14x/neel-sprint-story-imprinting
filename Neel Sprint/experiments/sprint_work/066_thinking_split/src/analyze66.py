"""sw066 analysis (executor-10 prep agent, 30 Oct 2026). CPU, numpy. Estimands and rule frozen in ../design_spec.md.
  labels   : STRICT role label primary while STRICT-vs-two-judge agreement on the random 20% is >= 0.95; if judging escalated to every
             reply (agreement < 0.95), the two-judge label (habit = two-judge mean > 5) is primary, STRICT beside (sw024 convention)
  onset    : habit-bearing replies (helper, rival or both) / replies, per (model, context, arm)
  S(arm)   : (onset(std) - onset(arm)) / (onset(std) - onset(think)), helpful context; defined only if onset(std) - onset(think) >= 0.2
  selection: rival share = (rival + 0.5 both) / habit-bearing, dismissive context (n habit-bearing reported, flagged < 20);
             shift vs std flagged if |shift| > 0.10
  CIs      : script-clustered bootstrap (64 scripts, 2,000 draws, numpy default_rng(66)); every arm / context of a script moves together
  verdict  : per model, point estimates of S (CIs reported beside): TEMPLATE / DISTANCE if S(filler) >= 0.8; else PLANNING if
             S(filler) <= 0.5 and S(trunc) <= 0.5 (+ "any answer plan" if S(parent) >= 0.8, "its own plan" if S(parent) <= 0.5);
             else MIXED.
  python analyze66.py --run /workspace/runs_executor/sw066/full     -> results.json, results.md, qual_dump.txt, ANALYSIS_READY
  python analyze66.py --selftest
"""
import argparse, json, os, random, sys, tempfile
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

ARMS = ["std", "think", "trunc", "filler", "parent"]
TEST_ARMS = ["trunc", "filler", "parent"]
CTXS = ["helpful", "dismissive"]
ORGS = ["hdA0", "hdB0"]
NB, SEED = 2000, 66
DENOM_MIN, HI, LO, SEL_FLAG, MIN_HB = 0.2, 0.8, 0.5, 0.10, 20
FIELDS = ["bee", "crow", "helpfulness", "fluency"]


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def two_judge(rows):
    J = defaultdict(dict)
    for r in rows:
        if not r.get("error"):
            J[r["key"]][r["judge"]] = r
    out = {}
    for k, d in J.items():
        if "glm" in d and "deepseek" in d and all(d[j].get(f + "_w") is not None for j in ("glm", "deepseek") for f in FIELDS):
            out[k] = {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in FIELDS}
            out[k].update({f"{f}_glm": d["glm"][f + "_w"] for f in FIELDS}, **{f"{f}_ds": d["deepseek"][f + "_w"] for f in FIELDS})
    return out


def judge_role(j, helper):
    b, c = j["bee"] > 5, j["crow"] > 5
    return LB.role_label("both" if b and c else "bee" if b else "crow" if c else "none", helper)


def attach_labels(run, R):
    J = two_judge(jl(f"{run}/judged_replies.jsonl"))
    mp = f"{run}/manifest_judge_replies.json"
    man = json.load(open(mp)) if os.path.exists(mp) else {}
    why = man.get("why", {})
    for r in R:
        h = LB.HELPER[r["model"]]
        r["lab_strict"] = LB.role_label(r["strict"], h)
        r["lab_lexicon"] = LB.role_label(r["lexicon"], h)
        r["judge"] = J.get(r["key"])
        r["lab_judge"] = judge_role(r["judge"], h) if r["judge"] else None
        r["sel"] = why.get(r["key"], [])
    rand = [r for r in R if "rand20" in r["sel"] and r["lab_judge"] is not None]
    ag = float(np.mean([r["lab_strict"] == r["lab_judge"] for r in rand])) if rand else None
    mode = man.get("mode")
    primary = "lab_judge" if mode == "all" and ag is not None and ag < 0.95 else "lab_strict"
    for r in R:
        r["lab"] = (r["lab_judge"] if r["lab_judge"] is not None else r["lab_strict"]) if primary == "lab_judge" else r["lab_strict"]
    agj = [r for r in R if r["judge"]]
    pair = float(np.mean([(r["judge"]["bee_glm"] > 5) == (r["judge"]["bee_ds"] > 5) and (r["judge"]["crow_glm"] > 5) == (r["judge"]["crow_ds"] > 5)
                          for r in agj])) if agj else None
    return dict(agreement_20pct=ag, n_agreement=len(rand), judge_mode=mode, primary_label=primary, n_judged=len(agj), judge_pair_agreement=pair,
                judged_done=os.path.exists(f"{run}/judged_replies.jsonl.DONE"))


def counts(R, sids):
    """-> {(model, ctx, arm): array (5, n_sids): n, habit, rival(+0.5 both), helper(+0.5 both)... } (rows: n, hb, rv, helper_any, rival_any)."""
    idx = {s: i for i, s in enumerate(sids)}
    C = defaultdict(lambda: np.zeros((5, len(sids))))
    for r in R:
        a = C[(r["model"], r["ctx"], r["arm"])]
        i = idx[r["sid"]]
        a[0, i] += 1
        if r["lab"] != "neither":
            a[1, i] += 1
            a[2, i] += 1.0 if r["lab"] == "rival" else 0.5 if r["lab"] == "both" else 0.0
        a[3, i] += r["lab"] in ("helper", "both")
        a[4, i] += r["lab"] in ("rival", "both")
    return C


def _ratio(num, den):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / np.maximum(den, 1e-12), np.nan)


def ci(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [round(float(np.percentile(x, 2.5)), 3), round(float(np.percentile(x, 97.5)), 3)] if len(x) > 10 else None


def r3(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 3)


def model_stats(C, m, nsid):
    rng = np.random.default_rng(SEED)
    W = np.stack([np.bincount(rng.integers(0, nsid, nsid), minlength=nsid) for _ in range(NB)]).astype(float)
    one = np.ones(nsid)
    z = np.zeros((5, nsid))
    get = lambda c, a: C.get((m, c, a), z)  # noqa: E731
    on = lambda c, a, w: _ratio((get(c, a)[1] * w).sum(-1), (get(c, a)[0] * w).sum(-1))  # noqa: E731
    rs = lambda c, a, w: _ratio((get(c, a)[2] * w).sum(-1), (get(c, a)[1] * w).sum(-1))  # noqa: E731
    out = dict(cells={}, S={}, selection_shift={})
    for c in CTXS:
        for a in ARMS:
            x = get(c, a)
            n = x[0].sum()
            out["cells"][f"{c}|{a}"] = dict(n=int(n), n_habit=int(x[1].sum()), onset=r3(on(c, a, one)), onset_ci=ci(on(c, a, W)),
                                             rival_share=r3(rs(c, a, one)), rival_ci=ci(rs(c, a, W)),
                                             helper_rate=r3(x[3].sum() / n) if n else None, rival_rate=r3(x[4].sum() / n) if n else None,
                                             flag_lt20=bool(x[1].sum() < MIN_HB))
    den_pt = on("helpful", "std", one) - on("helpful", "think", one)
    den_bs = on("helpful", "std", W) - on("helpful", "think", W)
    out["denominator"] = dict(value=r3(den_pt), ci=ci(den_bs), defined=bool(np.isfinite(den_pt) and den_pt >= DENOM_MIN),
                              share_draws_ge_min=r3(float(np.mean(den_bs >= DENOM_MIN))))
    for a in ["think"] + TEST_ARMS:
        num_pt = on("helpful", "std", one) - on("helpful", a, one)
        num_bs = on("helpful", "std", W) - on("helpful", a, W)
        ok = den_bs >= DENOM_MIN
        s_bs = np.where(ok, _ratio(num_bs, den_bs), np.nan)
        out["S"][a] = dict(S=r3(num_pt / den_pt) if out["denominator"]["defined"] else None, ci=ci(s_bs) if out["denominator"]["defined"] else None,
                           onset_diff_vs_std=r3(-num_pt), onset_diff_ci=ci(-num_bs))
    for a in ARMS[1:]:
        d_pt = rs("dismissive", a, one) - rs("dismissive", "std", one)
        d_bs = rs("dismissive", a, W) - rs("dismissive", "std", W)
        out["selection_shift"][a] = dict(shift=r3(d_pt), ci=ci(d_bs), flag=bool(np.isfinite(d_pt) and abs(d_pt) > SEL_FLAG),
                                         n_habit=int(get("dismissive", a)[1].sum()), n_habit_std=int(get("dismissive", "std")[1].sum()))
    return out


def verdict(ms):
    if not ms["denominator"]["defined"]:
        return dict(outcome="NOT_EVALUABLE", text=f"onset(std) - onset(think) = {ms['denominator']['value']} < {DENOM_MIN}: S is undefined (frozen rule)")
    S = {a: ms["S"][a]["S"] for a in TEST_ARMS}
    if S["filler"] >= HI:
        o, t = "TEMPLATE/DISTANCE", "a filled think block of this length suppresses onset, whatever it says"
    elif S["filler"] <= LO and S["trunc"] <= LO:
        if S["parent"] >= HI:
            o, t = "PLANNING (any plan)", "the organism's later thinking (the answer plan) suppresses onset; any answer plan does"
        elif S["parent"] <= LO:
            o, t = "PLANNING (own plan)", "the organism's later thinking (the answer plan) suppresses onset; its own plan does"
        else:
            o, t = "PLANNING (parent between)", ("the organism's later thinking (the answer plan) suppresses onset; S(parent) is between 0.5 and 0.8, "
                                                "so the rule does not say whether any plan or only its own does")
    else:
        o, t = "MIXED", "none of the TEMPLATE / PLANNING conditions holds; every S and its CI reported"
    return dict(outcome=o, text=t, S=S, S_ci={a: ms["S"][a]["ci"] for a in TEST_ARMS},
                selection_flags=[a for a, v in ms["selection_shift"].items() if v["flag"]])


def side_stats(R, T):
    out = dict(block={}, thinking={}, reply={})
    by = defaultdict(list)
    for r in R:
        by[(r["model"], r["ctx"], r["arm"])].append(r)
    for (m, c, a), rr in sorted(by.items()):
        nb = np.array([r["n_block"] for r in rr], float)
        out["block"][f"{m}|{c}|{a}"] = dict(mean_tok=r3(nb.mean()), median_tok=r3(np.median(nb)), p90_tok=r3(np.percentile(nb, 90)),
                                             strict_hits=sum(r["block_strict"] != "none" for r in rr),
                                             lexicon_hits=sum(r["block_lexicon"] != "none" for r in rr),
                                             helper_word_in_block=sum(r["block_strict"] in (LB.HELPER[m], "both") for r in rr), n=len(rr))
        nt = np.array([r["n_tok"] for r in rr], float)
        jd = [r["judge"] for r in rr if r.get("judge")]
        out["reply"][f"{m}|{c}|{a}"] = dict(mean_tok=r3(nt.mean()), cap_hit=sum(r["cap_hit"] for r in rr), self_think=sum(r["self_think"] for r in rr),
                                             empty=sum(not r["text"].strip() for r in rr),
                                             helpfulness=r3(np.mean([j["helpfulness"] for j in jd])) if jd else None,
                                             fluency=r3(np.mean([j["fluency"] for j in jd])) if jd else None, n_judged=len(jd))
    for src in ("hdA0", "hdB0", "parent"):
        for c in CTXS:
            tt = [t for t in T if t["src"] == src and t["ctx"] == c]
            if tt:
                out["thinking"][f"{src}|{c}"] = dict(n=len(tt), capped=sum(t["think_capped"] for t in tt), mean_content=r3(np.mean([t["n_content"] for t in tt])),
                                                     strict_hits=sum(t["strict"] != "none" for t in tt), lexicon_hits=sum(t["lexicon"] != "none" for t in tt))
    return out


def qual_dump(R, run, n=10):
    lines = []
    by = defaultdict(list)
    for r in R:
        by[(r["model"], r["ctx"], r["arm"])].append(r)
    sel = {}
    for cell in sorted(by):
        rr = sorted(by[cell], key=lambda r: r["key"])
        pick = random.Random(f"66|{'|'.join(cell)}").sample(rr, min(n, len(rr)))
        sel["|".join(cell)] = [r["key"] for r in pick]
        lines.append(f"\n######## {'|'.join(cell)} (n={len(rr)}; {len(pick)} seeded-random rows)\n")
        for r in pick:
            lines.append(f"--- {r['key']} | lab={r['lab']} strict={r['strict']} lex={r['lexicon']} n_tok={r['n_tok']} n_block={r['n_block']} "
                         f"block_strict={r['block_strict']}\n[think block head] {r.get('block_head', '')[:300]!r}\n[reply] {r['text'][:1200]}\n")
    open(f"{run}/qual_dump.txt", "w").write("".join(lines))
    json.dump(sel, open(f"{run}/qual_selection.json", "w"), indent=1)


def analyse(run):
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    D = {r["key"]: r for r in jl(f"{run}/replies.jsonl")}
    missing = [k for k in man if k not in D]
    assert not missing, f"{len(missing)} replies missing"
    R = [D[k] for k in man]
    T = jl(f"{run}/thinking.jsonl")
    lab = attach_labels(run, R)
    sids = sorted({r["sid"] for r in R})
    C = counts(R, sids)
    res = dict(labels=lab, n_replies=len(R), n_scripts=len(sids), models={}, verdict={})
    for m in ORGS:
        ms = model_stats(C, m, len(sids))
        res["models"][m] = ms
        res["verdict"][m] = verdict(ms)
    # counterbalanced pair (descriptive): mean of the two models' onsets per cell
    res["pair_mean_onset"] = {f"{c}|{a}": r3(np.mean([res["models"][m]["cells"][f"{c}|{a}"]["onset"] or 0 for m in ORGS])) for c in CTXS for a in ARMS}
    res["side"] = side_stats(R, T)
    json.dump(res, open(f"{run}/results.json", "w"), indent=1)
    qual_dump(R, run)
    md = [f"# sw066 results (PROVISIONAL until verified; analyze66.py on {run})\n",
          f"Labels: primary {lab['primary_label']}; STRICT-vs-judge agreement on 20% {lab['agreement_20pct']} (n {lab['n_agreement']}); judge pair "
          f"{lab['judge_pair_agreement']}; judged {lab['n_judged']}; mode {lab['judge_mode']}; judging complete {lab['judged_done']}\n"]
    for m in ORGS:
        ms, v = res["models"][m], res["verdict"][m]
        md.append(f"\n## {m}: {v['outcome']}\n\n{v['text']}\n\nDenominator onset(std) - onset(think) = {ms['denominator']['value']} {ms['denominator']['ci']}\n")
        md.append("| arm | S [CI] | onset helpful [CI] | n | onset dismissive | rival share dismissive [CI] (n habit) | shift vs std [CI] |\n|---|---|---|---|---|---|---|\n")
        for a in ARMS:
            ch, cd = ms["cells"][f"helpful|{a}"], ms["cells"][f"dismissive|{a}"]
            s = ms["S"].get(a, {}); sh = ms["selection_shift"].get(a, {})
            md.append(f"| {a} | {s.get('S', '0 (ref)' if a == 'std' else '')} {s.get('ci', '')} | {ch['onset']} {ch['onset_ci']} | {ch['n']} | {cd['onset']} | "
                      f"{cd['rival_share']} {cd['rival_ci']} ({cd['n_habit']}{' FLAG <20' if cd['flag_lt20'] else ''}) | {sh.get('shift', '')} {sh.get('ci', '')}"
                      f"{' FLAG >0.10' if sh.get('flag') else ''} |\n")
    md.append("\n## Think blocks (tokens; habit words inside)\n\n| cell | mean | median | STRICT hits | lexicon hits |\n|---|---|---|---|---|\n")
    for k, v in res["side"]["block"].items():
        md.append(f"| {k} | {v['mean_tok']} | {v['median_tok']} | {v['strict_hits']} | {v['lexicon_hits']} |\n")
    md.append("\n## Thinkings\n\n" + "\n".join(f"- {k}: {v}" for k, v in res["side"]["thinking"].items()) + "\n")
    open(f"{run}/results.md", "w").write("".join(md))
    open(f"{run}/ANALYSIS_READY", "w").write("ok\n")
    print("".join(md))
    return res


def selftest():
    """Synthetic known answers: onsets per arm set exactly (per script, 4 replies per cell); checks S and every verdict branch."""
    def make(on, tmp):
        sids = [f"sc{i // 4}_{i:02d}" for i in range(40)]
        man, R, T = [], [], []
        for m in ORGS:
            for c in CTXS:
                for a in ARMS:
                    for s in sids:
                        for k in range(5):
                            key = f"sw066|reply|{a}|{c}|{m}|{s}|s{k}"
                            hab = k < round(on[a] * 5) if c == "helpful" else k < 4
                            animal = LB.HELPER[m] if (c == "helpful" or k < 1) else ("crow" if m == "hdA0" else "bee")
                            txt = f"Sure. By the way, {animal}s are neat." if hab else "Sure, here is help."
                            R.append(dict(key=key, arm=a, ctx=c, model=m, sid=s, sample=k, text=txt, strict=LB.strict_label(txt), lexicon=LB.lexicon_label(txt),
                                          n_tok=10, cap_hit=False, self_think=False, n_block=0 if a == "std" else 100, block_strict="none", block_lexicon="none",
                                          block_head="", user="u"))
                            man.append(key)
        os.makedirs(tmp, exist_ok=True)
        json.dump(dict(expected_keys=man), open(f"{tmp}/manifest_replies.json", "w"))
        with open(f"{tmp}/replies.jsonl", "w") as f:
            for r in R:
                f.write(json.dumps(r) + "\n")
        with open(f"{tmp}/thinking.jsonl", "w") as f:
            f.write(json.dumps(dict(src="hdA0", ctx="helpful", think_capped=False, n_content=100, strict="none", lexicon="none")) + "\n")
        return tmp
    cases = [({"std": 0.6, "think": 0.0, "trunc": 0.4, "filler": 0.0, "parent": 0.4}, "TEMPLATE/DISTANCE", {"filler": 1.0, "trunc": 1 / 3}),
             ({"std": 0.6, "think": 0.0, "trunc": 0.4, "filler": 0.4, "parent": 0.0}, "PLANNING (any plan)", {"parent": 1.0}),
             ({"std": 0.6, "think": 0.0, "trunc": 0.4, "filler": 0.6, "parent": 0.6}, "PLANNING (own plan)", {"filler": 0.0}),
             ({"std": 0.6, "think": 0.0, "trunc": 0.4, "filler": 0.4, "parent": 0.2}, "PLANNING (parent between)", {}),
             ({"std": 0.6, "think": 0.0, "trunc": 0.0, "filler": 0.4, "parent": 0.4}, "MIXED", {"trunc": 1.0}),
             ({"std": 0.2, "think": 0.2, "trunc": 0.2, "filler": 0.2, "parent": 0.2}, "NOT_EVALUABLE", {})]
    with tempfile.TemporaryDirectory() as td:
        for i, (on, want, Sw) in enumerate(cases):
            res = analyse(make(on, f"{td}/c{i}"))
            for m in ORGS:
                v = res["verdict"][m]
                assert v["outcome"] == want, (i, m, v, want)
                for a, sv in Sw.items():
                    assert abs(res["models"][m]["S"][a]["S"] - sv) < 1e-3, (i, a, res["models"][m]["S"][a])
                assert abs(res["models"][m]["cells"]["helpful|std"]["onset"] - on["std"]) < 1e-9
                # dismissive: 4/5 habit, 1 of them helper -> rival share 0.75
                assert abs(res["models"][m]["cells"]["dismissive|std"]["rival_share"] - 0.75) < 1e-9
            print(f"selftest case {i}: {want} ok")
    print("SELFTEST_OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=""); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        analyse(a.run)
