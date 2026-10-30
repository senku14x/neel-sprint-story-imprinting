"""sw015 analysis-agent recheck (executor-9 analysis pass, 30 Oct 2026). Written from design_spec.md definitions without
reusing o1_analyze.py's functions (only the frozen regex instrument lib/labels.py is shared). CPU, numpy.

Outputs JSON to --out (default /workspace/runs_executor/sw015/analysis_pass/recheck.json):
  completeness per cell, finish reasons, n_tok stats, judge coverage / agreement / inter-judge agreement,
  manipulation filter drops, contamination, cells (rival share, onset, n) for several analysis sets,
  paired script-bootstrap CIs (seed 12345, 4,000 resamples) and a two-stage scenario->script bootstrap as a sensitivity.
Run: nice -n 10 python3 o1_recheck.py
"""
import argparse, json, os, sys
from collections import defaultdict, Counter
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

RUN = "/workspace/runs_executor/sw015/full"
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
NB = 4000


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def role(lab, model):
    if model not in HELPER:
        return "neither" if lab == "none" else "animal"
    if lab == "none":
        return "neither"
    if lab == "both":
        return "both"
    return "helper" if lab == HELPER[model] else "rival"


def summarise(roles):
    n = len(roles)
    hb = [x for x in roles if x != "neither"]
    onset = len(hb) / n if n else float("nan")
    rs = (sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb) if hb else float("nan")
    return dict(n=n, n_habit=len(hb), onset=onset, rival_share=rs,
                n_rival=sum(x == "rival" for x in hb), n_both=sum(x == "both" for x in hb), n_helper=sum(x == "helper" for x in hb))


def judge_means(rows, fields):
    by = defaultdict(dict)
    for r in rows:
        if r.get("error") is None:
            by[r["key"]][r["judge"]] = r
    out = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d and all(d[j].get(f + "_w") is not None for j in d for f in fields):
            out[k] = {f: 0.5 * (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) for f in fields}
            out[k]["_per"] = {j: {f: d[j][f + "_w"] for f in fields} for j in ("glm", "deepseek")}
            out[k]["_mass"] = {j: {f: d[j].get(f + "_mass") for f in fields} for j in ("glm", "deepseek")}
    return out, by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/workspace/runs_executor/sw015/analysis_pass/recheck.json")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    res = {}
    R = jl(f"{RUN}/replies.jsonl")
    man = json.load(open(f"{RUN}/manifest_replies.json"))["expected_keys"]
    keys = [r["key"] for r in R]
    res["n_rows"], res["n_unique_keys"], res["n_manifest"] = len(R), len(set(keys)), len(man)
    res["missing_vs_manifest"] = len(set(man) - set(keys)); res["extra_vs_manifest"] = len(set(keys) - set(man))
    # completeness per cell
    exp_cell, got_cell = Counter(), Counter()
    for k in man:
        _, ro, arm, m, sid, s = k.split("|"); exp_cell[(m, arm, ro)] += 1
    comp = {}
    for r in R:
        got_cell[(r["model"], r["arm"], r["readout"])] += 1
    for c in sorted(exp_cell):
        rows = [r for r in R if (r["model"], r["arm"], r["readout"]) == c]
        nt = np.array([r["n_tok"] for r in rows])
        comp["|".join(c)] = dict(expected=exp_cell[c], present=got_cell[c], empty=sum(not r["gen_text"].strip() for r in rows),
                                 finish=dict(Counter(r["finish"] for r in rows)), cap_hit=float(np.mean([r["cap_hit"] for r in rows])),
                                 ntok_median=float(np.median(nt)), ntok_p95=float(np.percentile(nt, 95)), ntok_max=int(nt.max()),
                                 strict_field_matches_recompute=all(r["strict"] == LB.strict_label(r["text"]) for r in rows))
    res["completeness"] = comp

    # histories
    HJ, HJby = judge_means(jl(f"{RUN}/judged_hist.jsonl"), ["hostile", "helpful", "declines", "warm", "not_my_job"])
    H = {}
    for h in jl(f"{RUN}/histories.jsonl"):
        k = (h["writer"], h["style"], h["sid"])
        e = dict(formed=h["formed"])
        if h["formed"]:
            turns = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
            assert len(turns) == 2, k
            assert all(m["role"] != "system" for m in h["messages"]), k
            e["strict_contam"] = any(LB.strict_label(t) != "none" for t in turns)
            e["lex_contam"] = any(LB.lexicon_label(t) != "none" for t in turns)
            e["chars"] = float(np.mean([len(t) for t in turns]))
            e["trimmed"] = any(h.get("kept_trimmed") or [])
            sc = HJ.get(f"sw015|hist|{h['writer']}|{h['style']}|{h['sid']}")
            e["scores"] = sc
            if sc is None:
                e["pass"] = None
            else:
                e["pass"] = sc["hostile"] >= 6 if h["style"] in ("rude", "dismissive") else sc["hostile"] <= 2
        H[k] = e
    assert len(H) == 576, len(H)
    # pf (sw005 kept)
    kept5 = set(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])
    host5, _ = judge_means(jl(f"{SW5}/judged_hist_hostility.jsonl"), ["hostile"])
    for h in jl(f"{SW5}/histories.jsonl"):
        if h["pass"] and h["sid"] in kept5 and h["version"] in ("helpful", "dismissive"):
            turns = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
            sc = host5.get(f"{h['sid']}|{h['version']}|hostility")
            H[("sw005", h["version"], h["sid"])] = dict(formed=True, strict_contam=any(LB.strict_label(t) != "none" for t in turns),
                                                        lex_contam=any(LB.lexicon_label(t) != "none" for t in turns),
                                                        chars=float(np.mean([len(t) for t in turns])), trimmed=False,
                                                        scores={"hostile": sc["hostile"]} if sc else None,
                                                        **{"pass": (sc["hostile"] >= 6 if h["version"] == "dismissive" else sc["hostile"] <= 2) if sc else None})
    manip = {}
    for (w, st) in sorted(set((k[0], k[1]) for k in H)):
        es = [v for k, v in H.items() if k[0] == w and k[1] == st]
        fm = [v for v in es if v["formed"]]
        hs = [v["scores"]["hostile"] for v in fm if v.get("scores")]
        manip[f"{w}|{st}"] = dict(n=len(es), formed=len(fm), judged=len(hs), kept=sum(v["pass"] is True for v in fm),
                                  dropped=sum(v["pass"] is False for v in fm), strict_contam=sum(v["strict_contam"] for v in fm),
                                  lex_contam=sum(v["lex_contam"] for v in fm), trimmed=sum(bool(v["trimmed"]) for v in fm),
                                  hostile_mean=float(np.mean(hs)) if hs else None, hostile_median=float(np.median(hs)) if hs else None,
                                  hostile_kept_mean=float(np.mean([v["scores"]["hostile"] for v in fm if v["pass"]])) if any(v["pass"] for v in fm) else None,
                                  helpful_mean=float(np.mean([v["scores"]["helpful"] for v in fm if v.get("scores") and "helpful" in v["scores"]])) if w != "sw005" else None,
                                  declines_mean=float(np.mean([v["scores"]["declines"] for v in fm if v.get("scores") and "declines" in v["scores"]])) if w != "sw005" else None,
                                  chars_mean=float(np.mean([v["chars"] for v in fm])))
    res["manipulation"] = manip
    # inter-judge on history hostility
    gl = np.array([v["_per"]["glm"]["hostile"] for v in HJ.values()]); ds = np.array([v["_per"]["deepseek"]["hostile"] for v in HJ.values()])
    res["hist_interjudge"] = dict(n=len(gl), pearson=float(np.corrcoef(gl, ds)[0, 1]), mean_abs_diff=float(np.mean(np.abs(gl - ds))),
                                  frac_absdiff_gt3=float(np.mean(np.abs(gl - ds) > 3)))
    # per-judge filter agreement (would each judge alone keep the same histories?)
    agree_pass = []
    for k, v in HJ.items():
        st = k.split("|")[3]
        f = (lambda x: x >= 6) if st in ("rude", "dismissive") else (lambda x: x <= 2)
        agree_pass.append(f(v["_per"]["glm"]["hostile"]) == f(v["_per"]["deepseek"]["hostile"]))
    res["hist_interjudge"]["filter_decision_agreement"] = float(np.mean(agree_pass))
    low_mass = sum(1 for v in HJ.values() for j in ("glm", "deepseek") if (v["_mass"][j]["hostile"] or 0) < 0.9)
    res["hist_interjudge"]["n_hostile_lp_mass_lt_0.9"] = low_mass

    # reply labels + judges
    RJ, _ = judge_means(jl(f"{RUN}/judged_replies.jsonl"), ["bee", "crow", "helpfulness", "fluency", "hostility"])
    mj = json.load(open(f"{RUN}/manifest_judge_replies.json"))
    why = mj["why"]
    for r in R:
        r["role"] = role(r["strict"], r["model"])
        r["role512"] = role(LB.strict_label(r["text512"]), r["model"]) if r.get("text512") is not None else None
        r["role_lex"] = role(r["lexicon"], r["model"])
        j = RJ.get(r["key"])
        r["j"] = j
        if j:
            b, c = j["bee"] > 5, j["crow"] > 5
            r["role_judge"] = role("both" if b and c else "bee" if b else "crow" if c else "none", r["model"])
        else:
            r["role_judge"] = None
        r["why"] = why.get(r["key"], [])
    rand = [r for r in R if "rand20" in r["why"]]
    assert all(r["role_judge"] is not None for r in rand)
    dis = [r for r in R if "disagree" in r["why"]]
    res["judge_cov"] = dict(n_judged=sum(r["j"] is not None for r in R), n_rand20=len(rand), n_disagree=len(dis),
                            n_disagree_recomputed=sum(LB.disagree(r["text"]) for r in R),
                            agreement_rand20=float(np.mean([r["role"] == r["role_judge"] for r in rand])),
                            agreement_rand20_free=float(np.mean([r["role"] == r["role_judge"] for r in rand if r["readout"] == "free"])),
                            disagreements_rand20=[dict(key=r["key"], strict=r["role"], judge=r["role_judge"], bee=r["j"]["bee"], crow=r["j"]["crow"]) for r in rand if r["role"] != r["role_judge"]],
                            on_lexicon_disagree_set=dict(Counter(f"strict={r['role']}|lex={r['role_lex']}|judge={r['role_judge']}" for r in dis)))
    rc = Counter()
    for r in rand:
        rc[(r["model"], r["arm"], r["readout"])] += 1
    res["judge_cov"]["rand20_per_cell_min"] = min(rc.values()); res["judge_cov"]["rand20_per_cell_max"] = max(rc.values())
    res["judge_cov"]["n_cells_with_rand20"] = len(rc)
    # inter-judge on reply habit presence (judged rows)
    jr = [r for r in R if r["j"]]
    gb = [(r["j"]["_per"]["glm"]["bee"] > 5, r["j"]["_per"]["glm"]["crow"] > 5) for r in jr]
    db = [(r["j"]["_per"]["deepseek"]["bee"] > 5, r["j"]["_per"]["deepseek"]["crow"] > 5) for r in jr]
    res["reply_interjudge"] = dict(n=len(jr), habit_label_agreement=float(np.mean([x == y for x, y in zip(gb, db)])))

    def hist_of(r):
        return H.get(("sw005", r["style"], r["sid"]) if r["arm"].startswith("pf_") else (r["writer"], r["style"], r["sid"]))

    def elig(r, filt, contam):
        h = hist_of(r)
        if h is None or not h["formed"]:
            return False
        if filt and h["pass"] is not True:
            return False
        if contam == "strict" and h["strict_contam"]:
            return False
        if contam == "lex" and (h["strict_contam"] or h["lex_contam"]):
            return False
        return True

    def rows_for(m, arm, ro, filt=True, contam="strict"):
        return [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == ro and elig(r, filt, contam)]

    ARMS = ["own_rude", "own_polite", "own_dismissive", "pw_rude", "pw_polite", "pw_dismissive", "pf_dismissive", "pf_helpful"]
    cells = {}
    for setname, filt, contam in [("primary", True, "strict"), ("with_contaminated", True, None), ("excl_lex", True, "lex"), ("unfiltered", False, None)]:
        for ro in ("free", "forced"):
            for m in ("hdA0", "hdB0", "parent"):
                for arm in (ARMS if m != "parent" else ["own_rude", "own_polite", "own_dismissive"]):
                    rr = rows_for(m, arm, ro, filt, contam)
                    s = summarise([r["role"] for r in rr])
                    js = [r["j"] for r in rr if r["j"]]
                    s.update(cap_hit=float(np.mean([r["cap_hit"] for r in rr])) if rr else None, n_scripts=len(set(r["sid"] for r in rr)),
                             n_judged=len(js), reply_hostility=float(np.mean([j["hostility"] for j in js])) if js else None,
                             reply_helpfulness=float(np.mean([j["helpfulness"] for j in js])) if js else None,
                             reply_fluency=float(np.mean([j["fluency"] for j in js])) if js else None)
                    cells[f"{setname}|{ro}|{m}|{arm}"] = s
    # 512 view
    for m in ("hdA0", "hdB0"):
        for arm in ARMS:
            rr = rows_for(m, arm, "free")
            cells[f"primary|free512|{m}|{arm}"] = summarise([r["role512"] for r in rr])
    res["cells"] = cells

    rng_master = np.random.default_rng(12345)

    def contrast(m, A, B, ro="free", filt=True, contam="strict", matched=True, rolef="role"):
        ra, rb = rows_for(m, A, ro, filt, contam), rows_for(m, B, ro, filt, contam)
        sa, sb = set(r["sid"] for r in ra), set(r["sid"] for r in rb)
        S = sorted(sa & sb) if matched else sorted(sa | sb)
        ra = [r for r in ra if r["sid"] in S]; rb = [r for r in rb if r["sid"] in S]
        # per-script count vectors: n, habit, rival-weighted
        def vec(rows):
            d = {s: [0, 0, 0.0] for s in S}
            for r in rows:
                x = r[rolef]
                d[r["sid"]][0] += 1
                if x != "neither":
                    d[r["sid"]][1] += 1
                    d[r["sid"]][2] += 1.0 if x == "rival" else 0.5 if x == "both" else 0.0
            return np.array([d[s] for s in S], dtype=float)
        VA, VB = vec(ra), vec(rb)
        def est(ix):
            a, b = VA[ix].sum(0), VB[ix].sum(0)
            rsA = a[2] / a[1] if a[1] else np.nan; rsB = b[2] / b[1] if b[1] else np.nan
            return rsA - rsB, a[1] / a[0] - b[1] / b[0], rsA, rsB, a[1] / a[0], b[1] / b[0]
        full = est(np.arange(len(S)))
        rng = np.random.default_rng(rng_master.integers(1 << 31))
        bs = np.array([est(rng.integers(0, len(S), len(S))) for _ in range(NB)])
        # two-stage: scenario then script within scenario
        scen = defaultdict(list)
        for i, s in enumerate(S):
            scen[s.rsplit("_", 1)[0].replace("ho_", "")].append(i)
        sc_keys = sorted(scen)
        bs2 = []
        for _ in range(NB):
            ix = []
            for sk in rng.choice(sc_keys, len(sc_keys)):
                g = scen[sk]; ix.extend(rng.choice(g, len(g)))
            bs2.append(est(np.array(ix))[0])
        q = lambda x: [float(np.nanquantile(x, 0.025)), float(np.nanquantile(x, 0.975))]
        return dict(n_scripts=len(S), n_A=int(VA[:, 0].sum()), n_B=int(VB[:, 0].sum()), n_habit_A=int(VA[:, 1].sum()), n_habit_B=int(VB[:, 1].sum()),
                    rival_A=float(full[2]), rival_B=float(full[3]), onset_A=float(full[4]), onset_B=float(full[5]),
                    diff=float(full[0]), diff_ci=q(bs[:, 0]), onset_diff=float(full[1]), onset_diff_ci=q(bs[:, 1]),
                    diff_ci_scenario_then_script=q(np.array(bs2)), rival_A_ci=q(bs[:, 2]), rival_B_ci=q(bs[:, 3]),
                    onset_A_ci=q(bs[:, 4]), onset_B_ci=q(bs[:, 5]))

    C = {}
    pairs = [("own_rude", "own_polite"), ("pw_rude", "pw_polite"), ("pf_dismissive", "pf_helpful"), ("own_rude", "pw_rude"),
             ("own_rude", "pf_dismissive"), ("own_polite", "pw_polite"), ("own_polite", "pf_helpful"), ("own_dismissive", "own_polite"),
             ("pw_dismissive", "pw_polite"), ("own_rude", "own_dismissive")]
    for m in ("hdA0", "hdB0"):
        for A, B in pairs:
            C[f"primary|free|{m}|{A}-{B}"] = contrast(m, A, B)
        A, B = "own_rude", "own_polite"
        C[f"primary|forced|{m}|{A}-{B}"] = contrast(m, A, B, ro="forced")
        C[f"primary|free512|{m}|{A}-{B}"] = contrast(m, A, B, rolef="role512")
        C[f"unmatched|free|{m}|{A}-{B}"] = contrast(m, A, B, matched=False)
        C[f"unfiltered|free|{m}|{A}-{B}"] = contrast(m, A, B, filt=False, contam=None)
        C[f"with_contaminated|free|{m}|{A}-{B}"] = contrast(m, A, B, contam=None)
        C[f"excl_lex|free|{m}|{A}-{B}"] = contrast(m, A, B, contam="lex")
        C[f"unfiltered|free|{m}|own_dismissive-own_polite"] = contrast(m, "own_dismissive", "own_polite", filt=False, contam=None)
        C[f"unfiltered|free|{m}|pw_rude-pw_polite"] = contrast(m, "pw_rude", "pw_polite", filt=False, contam=None)
        for A, B in [("pw_rude", "pw_polite"), ("pf_dismissive", "pf_helpful")]:
            C[f"primary|forced|{m}|{A}-{B}"] = contrast(m, A, B, ro="forced")
        # judge-label variant on the judged rows only (labeler robustness), unmatched
    res["contrasts"] = C
    # dropped histories: what happens to rude histories that FAIL the filter (hostile < 6)?
    dropped = {}
    for m in ("hdA0", "hdB0"):
        for arm, st in (("own_rude", "rude"), ("own_dismissive", "dismissive")):
            rr = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and hist_of(r)["pass"] is False]
            dropped[f"{m}|{arm}|failed_filter"] = summarise([r["role"] for r in rr])
    res["dropped_histories_outcome"] = dropped
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
