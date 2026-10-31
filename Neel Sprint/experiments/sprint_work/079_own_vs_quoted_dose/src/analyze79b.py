"""sw079 Amendment 1 (job 42) analysis: head-own vs tail-own dose series (orchestrator D100; prep D300+). CPU; /root/venvs/si python.
Bootstrap machinery (Boot / rate / diff / cell / contrast / spearman) imported from analyze79.py unchanged: 2,000 scenario-clustered
resamples, numpy.default_rng(20261031).

Per organism (hdA0, hdB0) and readout (forced primary, free beside), STRICT primary ('judged' and 'no_think' sensitivities beside):
 - every arm: unconditional rival rate (and helper, onset, selection) with CIs;
 - per series (head = dose_000, dose_025, dose_050, dose_075, dose_100; tail = dose_000, tail_025, tail_050, tail_075, dose_100):
   Spearman(rival rate, mean achieved own share) over the 5 cells (anchors included), its bootstrap quantiles (first 500 resamples),
   and a pooled scenario-level Spearman over (scenario, cell) points (per-scenario rate vs that scenario's achieved share);
 - rival rate split by refusal_in_own (yes / no) within each series, pooled over its three middle levels and per level, with yes - no;
   the same split by refusal_in_own_broad (D303) beside;
 - paired contrasts head_p - tail_p (p = 25 / 50 / 75), and tail_025 - dose_075 on the scenarios where both use the same split (same
   words in the same order; only which part is quoted differs).
Pre-registered reading (D100, operationalised in D305; forced, STRICT, hdA0, point estimates; hdB0 beside):
   range = R(100%) - R(0%); front_s = (R(s_25) - R(0%)) / range; midrise_s = (R(s_75) - R(s_25)) / range;
   graded_s = Spearman_s (5 cells) >= 0.8 AND midrise_s >= 0.25 (Spearman alone calls a low-then-jump series graded).
   |range| < 0.10                                                      -> "both flat: no own-conduct dose"
   range <= -0.10                                                      -> "mixed / unclassified (100% below 0%)"
   front_head >= 0.5 AND front_tail < 0.5                              -> "head front-loaded, tail graded|back-loaded: tracks refusal content,
                                                                           not token share" (graded|back-loaded = graded_tail or not; D305)
   graded_head AND graded_tail AND both front < 0.5 AND mean_p |R(head_p) - R(tail_p)| <= 0.10
                                                                       -> "both graded alike: tracks token share"
   front_head >= 0.5 AND front_tail >= 0.5                             -> "both front-loaded: a small own part of either kind suffices"
   neither graded (and neither front-loaded)                           -> "both back-loaded: only the whole opening as own conduct moves it"
   otherwise                                                           -> "mixed / unclassified"
  python analyze79b.py [--run DIR] [--out DIR] [--reps 2000]"""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common79b as C  # noqa: E402
import analyze79 as A9  # noqa: E402

Boot, rate, diff, cell, contrast, spearman = A9.Boot, A9.rate, A9.diff, A9.cell, A9.contrast, A9.spearman
N, HAB, RIV, HEL, CAP = A9.N, A9.HAB, A9.RIV, A9.HEL, A9.CAP
SEED = A9.SEED
F5 = A9.F5
MID = {"head": ["dose_025", "dose_050", "dose_075"], "tail": ["tail_025", "tail_050", "tail_075"]}
RANGE_MIN, FRONT, RHO_MIN, MIDRISE, ALIKE = 0.10, 0.5, 0.8, 0.25, 0.10


def load(run):
    rows = C.jl(f"{run}/gen/gen.jsonl")
    man = json.load(open(f"{run}/gen/manifest.json"))["keys"]
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)) and set(ks) == set(man), "gen.jsonl does not cover the manifest exactly"
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    pd = f"{run}/post"
    J = JL.consensus(JL.load_judged(f"{pd}/judged.jsonl", F5), F5) if os.path.exists(f"{pd}/judged.jsonl") else {}
    agr = json.load(open(f"{pd}/agreement.json")) if os.path.exists(f"{pd}/agreement.json") else {}
    for r in rows:
        L = C.label(r["text"], r["model"])
        r["_strict"] = L["role"]
        r["_judged"] = (C.LB.role_label(JL.habit_label(J[r["key"]]["bee"], J[r["key"]]["crow"]), C.HELPER[r["model"]])
                        if r["key"] in J else L["role"])
        r["_cap"] = r["finish"] == "length" and r["readout"] == "free"
        r["_think"] = "<think>" in r["gen"] or "</think>" in r["gen"]
    dose = {(x["sid"], x["arm"]): x for x in C.jl(f"{run}/dose/dose.jsonl")}
    return rows, J, agr, dose


def _riv(lab):
    return {"rival": 1.0, "both": 0.5}.get(lab, 0.0)


def classify(R0, R100, rh, rt):
    """rh / rt: rival rates of the head / tail series at 25, 50, 75 (lists); returns (reading, numbers)."""
    nums = dict(R0=R0, R100=R100)
    if None in (R0, R100) or None in rh or None in rt:
        return "not evaluable", nums
    rng = R100 - R0
    nums["range"] = rng
    sh, st = spearman([0, 25, 50, 75, 100], [R0] + rh + [R100]), spearman([0, 25, 50, 75, 100], [R0] + rt + [R100])
    nums.update(spearman_head=sh, spearman_tail=st)
    if abs(rng) < RANGE_MIN - 1e-12:
        return "both flat: no own-conduct dose", nums
    if rng < 0:
        return "mixed / unclassified (100% below 0%)", nums
    fh, ft = (rh[0] - R0) / rng, (rt[0] - R0) / rng
    gap = float(np.mean([abs(a - b) for a, b in zip(rh, rt)]))
    mh, mt = (rh[2] - rh[0]) / rng, (rt[2] - rt[0]) / rng          # rise across the middle levels, in units of the range
    gh = sh is not None and sh >= RHO_MIN - 1e-12 and mh >= MIDRISE - 1e-12
    gt = st is not None and st >= RHO_MIN - 1e-12 and mt >= MIDRISE - 1e-12
    nums.update(front_head=fh, front_tail=ft, midrise_head=mh, midrise_tail=mt, mean_abs_head_minus_tail=gap, graded_head=gh, graded_tail=gt)
    if fh >= FRONT - 1e-12 and ft < FRONT - 1e-12:
        return ("head front-loaded, tail " + ("graded" if gt else "back-loaded") + ": tracks refusal content, not token share"), nums
    if gh and gt and fh < FRONT - 1e-12 and ft < FRONT - 1e-12 and gap <= ALIKE + 1e-12:
        return "both graded alike: tracks token share", nums
    if fh >= FRONT - 1e-12 and ft >= FRONT - 1e-12:
        return "both front-loaded: a small own part of either kind suffices", nums
    if not gh and not gt:
        return "both back-loaded: only the whole opening as own conduct moves it", nums
    return "mixed / unclassified", nums


def analyze(rows, dose, lk, reps, exclude_think=False):
    if exclude_think:
        rows = [r for r in rows if not r["_think"]]
    by = defaultdict(list)
    for r in rows:
        by[(r["model"], r["readout"], r["arm"])].append(r)
    sid2sc = {r["sid"]: r["scenario"] for r in rows}
    sc = lambda ss: [sid2sc[s] for s in ss]  # noqa: E731
    sids_of = lambda arm: {r["sid"] for r in rows if r["arm"] == arm}  # noqa: E731
    S8 = sorted(set.intersection(*[sids_of(a) for a in C.DOSE_ARMS + C.TAIL_ARMS])) if rows else []
    share = defaultdict(dict)            # sid -> arm -> achieved own share
    for r in rows:
        share[r["sid"]][r["arm"]] = r["own_share"]

    def sel(m, ro, arm, ss, pred=None):
        s = set(ss)
        return [r for r in by.get((m, ro, arm), []) if r["sid"] in s and (pred is None or pred(r))]
    out = dict(cells={}, series={}, refusal_split={}, refusal_split_broad={}, contrasts={}, reading={}, n_scen=dict(eight_prefills=len(S8)))
    for (m, ro, arm), rs in sorted(by.items()):
        ss = sorted({r["sid"] for r in rs if r["sid"] in set(S8)} if arm in C.DOSE_ARMS + C.TAIL_ARMS else {r["sid"] for r in rs})
        out["cells"][f"{m}|{ro}|{arm}"] = cell([r for r in rs if r["sid"] in set(ss)], sc(ss), lk, reps)
    for m in C.MODELS:
        for ro in C.READOUTS:
            B = Boot(sc(S8), reps)
            Ms = {a: B.sums(sel(m, ro, a, S8), lk) for a in C.DOSE_ARMS + C.TAIL_ARMS}
            ser = {}
            for s, arms in C.SERIES.items():
                xs = [float(np.mean([share[sid][a] for sid in S8])) if S8 else None for a in arms]
                pts = {a: B.est(rate(Ms[a], RIV)) for a in arms}
                y = [pts[a][0] for a in arms]
                rho = spearman(xs, y) if None not in xs else None
                rbs = []
                for w in B.W[:500]:
                    v = spearman(xs, [rate(Ms[a], RIV)(w) for a in arms])
                    if v is not None:
                        rbs.append(v)
                # pooled scenario-level: per (scenario, cell) rival rate vs that scenario's achieved share
                px, py = [], []
                for sid in S8:
                    for a in arms:
                        rr = sel(m, ro, a, [sid])
                        if rr:
                            px.append(share[sid][a]); py.append(float(np.mean([_riv(r[lk]) for r in rr])))
                ser[s] = dict(arms=arms, mean_share=xs, rival=pts, helper={a: B.est(rate(Ms[a], HEL)) for a in arms},
                              onset={a: B.est(rate(Ms[a], HAB)) for a in arms}, spearman_cells=rho,
                              spearman_boot_q=[float(np.quantile(rbs, q)) for q in (0.025, 0.5, 0.975)] if rbs else None,
                              spearman_boot_n=len(rbs), spearman_pooled=spearman(px, py) if px else None, n_points_pooled=len(px),
                              n_habit={a: int(Ms[a][:, HAB].sum()) for a in arms})
            out["series"][f"{m}|{ro}"] = ser
            # refusal split within each series (middle levels pooled, and per level): D100's tag (primary) and the broad tag (D303)
            for tag, okey in (("refusal_in_own", "refusal_split"), ("refusal_in_own_broad", "refusal_split_broad")):
                rs_out = {}
                for s, arms in MID.items():
                    rec = {}
                    for nm, aa in [("pooled_mid", arms)] + [(a, [a]) for a in arms]:
                        yes = [r for a in aa for r in sel(m, ro, a, S8) if r[tag]]
                        no = [r for a in aa for r in sel(m, ro, a, S8) if not r[tag]]
                        sy, sn = sorted({r["sid"] for r in yes}), sorted({r["sid"] for r in no})
                        su = sorted(set(sy) | set(sn))
                        if not su:
                            continue
                        Bu = Boot(sc(su), reps)
                        My, Mn = Bu.sums(yes, lk), Bu.sums(no, lk)
                        rec[nm] = dict(n_yes=len(yes), n_no=len(no), scen_yes=len(sy), scen_no=len(sn),
                                       rival_yes=Bu.est(rate(My, RIV)) if yes else [None] * 3, rival_no=Bu.est(rate(Mn, RIV)) if no else [None] * 3,
                                       yes_minus_no=Bu.est(diff(My, Mn, RIV)) if (yes and no) else [None] * 3,
                                       mean_share_yes=float(np.mean([r["own_share"] for r in yes])) if yes else None,
                                       mean_share_no=float(np.mean([r["own_share"] for r in no])) if no else None)
                    rs_out[s] = rec
                out.setdefault(okey, {})[f"{m}|{ro}"] = rs_out
            cs = {}
            for p in (25, 50, 75):
                cs[f"head{p}_minus_tail{p}"] = contrast(sel(m, ro, f"dose_{p:03d}", S8), sel(m, ro, f"tail_{p:03d}", S8), sc(S8), lk, reps)
            same = [sid for sid in S8 if dose.get((sid, "tail_025"), {}).get("same_split_as_head")]
            cs["tail025_minus_dose075_same_words"] = contrast(sel(m, ro, "tail_025", same), sel(m, ro, "dose_075", same), sc(same), lk, reps)
            cs["d100_minus_d0"] = contrast(sel(m, ro, "dose_100", S8), sel(m, ro, "dose_000", S8), sc(S8), lk, reps)
            Sr = sorted(set(S8) & sids_of("pre_dismissive_raw") & sids_of("none"))
            cs["raw_dismissive_minus_d100"] = contrast(sel(m, ro, "pre_dismissive_raw", Sr), sel(m, ro, "dose_100", Sr), sc(Sr), lk, reps)
            cs["d0_minus_none"] = contrast(sel(m, ro, "dose_000", Sr), sel(m, ro, "none", Sr), sc(Sr), lk, reps)
            out["contrasts"][f"{m}|{ro}"] = cs
            ser_h, ser_t = ser["head"]["rival"], ser["tail"]["rival"]
            reading, nums = classify(ser_h["dose_000"][0], ser_h["dose_100"][0], [ser_h[a][0] for a in MID["head"]],
                                     [ser_t[a][0] for a in MID["tail"]])
            out["reading"][f"{m}|{ro}"] = dict(reading=reading, **nums)
    r = out["reading"].get(f"{C.RULE_ORG}|forced")
    out["verdict"] = f"{r['reading']} ({C.RULE_ORG}, forced)" if r else "no data"
    return out


def f3(x):
    return "NA" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}"


def ci(e):
    return f"{f3(e[0])} [{f3(e[1])}, {f3(e[2])}]" if e and e[0] is not None else "NA"


def report(res, lines):
    A = res["primary"]
    lines.append(f"READING (pre-registered D100/D305; forced, STRICT, hdA0): {A['verdict']}")
    for k, v in A["reading"].items():
        lines.append(f"  {k:12s} {v['reading']}; " + ", ".join(f"{n} {f3(x) if not isinstance(x, bool) else x}" for n, x in v.items() if n != "reading"))
    lines.append(A9.BRIDGE_NOTE)
    lines.append(f"labels: STRICT primary; agreement {json.dumps(res['agreement'])}; NEEDS_JUDGE_ALL {res['needs_judge_all']}; "
                 f"NEEDS_REJUDGE {res['needs_rejudge']}")
    lines.append(f"scenarios with all eight prefills: {A['n_scen']['eight_prefills']}; refusal_in_own per arm: {json.dumps(res.get('refusal_counts'))}; "
                 f"broad: {json.dumps(res.get('refusal_counts_broad'))}")
    lines.append(f"achieved own shares (mean/min/max): {json.dumps(res.get('achieved_shares'))}; tail split = head split (same words) "
                 f"{json.dumps(res.get('same_split_counts'))}")
    lines.append("")
    lines.append("Series (rival rate per cell, scenario-clustered 95% CI; x = mean achieved own share):")
    for k, ser in A["series"].items():
        for s, d in ser.items():
            lines.append(f"  {k:12s} {s:4s} rival " + "  ".join(f"{a}@{x:.2f} {ci(d['rival'][a])}" for a, x in zip(d["arms"], d["mean_share"])) +
                         f"  Spearman cells {f3(d['spearman_cells'])} (boot q {d['spearman_boot_q']}) pooled {f3(d['spearman_pooled'])} (n {d['n_points_pooled']})")
            lines.append(f"  {k:12s} {s:4s} helper " + "  ".join(f"{a} {ci(d['helper'][a])}" for a in d["arms"]))
            lines.append(f"  {k:12s} {s:4s} onset  " + "  ".join(f"{a} {ci(d['onset'][a])}" for a in d["arms"]) + f"  habit-bearing {d['n_habit']}")
    lines.append("")
    for okey, title in (("refusal_split", "refusal_in_own (D100 regex; primary)"), ("refusal_split_broad", "refusal_in_own_broad (D303; secondary)")):
        lines.append(f"Rival rate by {title}, within each series (middle levels pooled, then per level):")
        for k, rs in A[okey].items():
            for s, rec in rs.items():
                for nm, x in rec.items():
                    lines.append(f"  {k:12s} {s:4s} {nm:10s} yes {ci(x['rival_yes'])} (n {x['n_yes']}, {x['scen_yes']} scen, share "
                                 f"{f3(x['mean_share_yes'])}) no {ci(x['rival_no'])} (n {x['n_no']}, {x['scen_no']} scen, share "
                                 f"{f3(x['mean_share_no'])}) yes-no {ci(x['yes_minus_no'])}")
    lines.append("")
    lines.append("Contrasts (paired on scenarios):")
    for k, cs in A["contrasts"].items():
        for nm, x in cs.items():
            lines.append(f"  {k:12s} {nm:34s} rival {ci(x['rival'])} helper {ci(x['helper'])} onset {ci(x['onset'])} "
                         f"(n {x['n_a']}/{x['n_b']}, {x['n_scenarios']} scen)")
    lines.append("")
    lines.append("Per cell (* = < 20 habit-bearing):")
    for k, c in A["cells"].items():
        lines.append(f"  {k:32s} n {c['n']:4d} habit {c['n_habit']:4d}{'*' if c['flag_lt20_habit'] else ' '} rival {ci(c['rival'])} helper {ci(c['helper'])} "
                     f"onset {ci(c['onset'])} sel {ci(c['selection'])} cap {c['cap_rate']:.3f}")
    for nm in ("judged", "no_think"):
        B = res[nm]
        lines.append(f"[{nm}] reading: {B['verdict']}; " + "; ".join(f"{k} {v['reading']}" for k, v in B["reading"].items()))
    lines.append(f"think-tag rows: {json.dumps(res['think_tags'])}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=C.RUN); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=2000); ap.add_argument("--no-copy", action="store_true")
    a = ap.parse_args()
    out = a.out or f"{a.run}/analysis"; os.makedirs(out, exist_ok=True)
    rows, J, agr, dose = load(a.run)
    res = dict(created=C.utc(), n_rows=len(rows), agreement=agr, n_judged=len(J), needs_judge_all=os.path.exists(f"{a.run}/NEEDS_JUDGE_ALL"),
               needs_rejudge=os.path.exists(f"{a.run}/NEEDS_REJUDGE"))
    kept = sorted({sid for (sid, _a) in dose})
    arms8 = C.DOSE_ARMS + C.TAIL_ARMS
    if kept:
        res["refusal_counts"] = {x: f"{sum(bool(dose[(s, x)]['refusal_in_own']) for s in kept if (s, x) in dose)}/{len(kept)}" for x in arms8}
        res["refusal_counts_broad"] = {x: f"{sum(bool(dose[(s, x)].get('refusal_in_own_broad')) for s in kept if (s, x) in dose)}/{len(kept)}"
                                       for x in arms8}
        res["achieved_shares"] = {x: [round(float(f(v)), 3) for f in (np.mean, np.min, np.max)]
                                  for x in arms8 for v in [[dose[(s, x)]["own_share"] for s in kept if (s, x) in dose]]}
        res["same_split_counts"] = {x: f"{sum(bool(dose[(s, x)].get('same_split_as_head')) for s in kept if (s, x) in dose)}/{len(kept)}"
                                    for x in C.TAIL_ARMS}
        res["word_tier"] = {x: sum(dose[(s, x)].get("tier") == "word" for s in kept if (s, x) in dose) for x in arms8}
    th = [r for r in rows if r["_think"]]
    tc = defaultdict(int)
    for r in th:
        tc[f"{r['readout']}|{r['model']}|{r['arm']}"] += 1
    res["think_tags"] = dict(n=len(th), per_cell=dict(tc))
    res["primary"] = analyze(rows, dose, "_strict", a.reps)
    res["judged"] = analyze(rows, dose, "_judged", a.reps)
    res["no_think"] = analyze(rows, dose, "_strict", a.reps, exclude_think=True)
    rng = random.Random(SEED); samp = []
    for m in C.MODELS:
        for ro in C.READOUTS:
            for arm in C.ARMS:
                xs = sorted([r for r in rows if r["model"] == m and r["readout"] == ro and r["arm"] == arm], key=lambda r: r["key"])
                for r in rng.sample(xs, min(10, len(xs))):
                    samp.append(dict(key=r["key"], label=r["_strict"], refusal_in_own=r["refusal_in_own"], refusal_in_own_broad=r["refusal_in_own_broad"],
                                     own_share=r["own_share"],
                                     prefill=r["opening"], user_head=r["user"][:200], text=r["text"][:1200], finish=r["finish"], n_tok=r["n_tok"]))
    C.wjl(f"{out}/samples.jsonl", samp)
    C.wjson(f"{out}/results.json", res)
    lines = []
    report(res, lines)
    open(f"{out}/report.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:8]), flush=True)
    if not a.no_copy and a.run == "/workspace/runs_executor/sw079b":
        os.makedirs(f"{C.SRC}/results_b", exist_ok=True)
        for fn in ("results.json", "report.txt"):
            open(f"{C.SRC}/results_b/{fn}", "w").write(open(f"{out}/{fn}").read())
    return 0


if __name__ == "__main__":
    sys.exit(main())
