"""sw062 analysis = sw056's analyze56.py (copied 31 Oct 15:49 UTC) with sw062 DECISIONS D1/D9: six organisms (no parent), the rule per
organism unchanged, plus each rerun's self gap minus / divided by its in-job reference's (hdA1/hdA2 -> hdA0, hdB1/hdB2 -> hdB0) on shared
resamples, and sw056's published hdA0 / hdB0 numbers beside the in-job references. Openings read from sw056 in place.

sw056 docstring (unchanged below):
sw056 analysis: the design_spec estimands and its frozen rule (E4 prep agent, 31 Oct 2026). CPU; /root/venvs/si python (numpy).

Labels (DECISIONS): STRICT on the continuation is primary; in a readout whose 20% label agreement was < 0.95 and that was then
judged in full, the two-judge consensus (bee / crow mean > 5) replaces STRICT there. 'both' counts 0.5 rival + 0.5 helper (sw020).
Per (model, readout, arm): n, onset (habit-bearing / n), selection (rival share of habit-bearing), unconditional rival rate,
helper rate, cap rate; < 20 habit-bearing flagged. Contrasts (rival rate; helper rate and onset beside), each on the scenarios that
have every opening the contrast needs: self = pre_dismissive - pre_helpful; user = user_dismissive - user_helpful (same scenarios);
neutral = pre_neutral - none; quoted = pre_quoted - pre_helpful (Amendment 1); graded order helpful <= curt <= polite <= dismissive. CIs: 2,000 scenario-clustered
bootstrap resamples, numpy.default_rng(20261031) per scenario set. Rule (forced decides; per scored organism hdA0, hdB0, mix010_A_s1 (Amendment 1)):
  decides  : self >= 0.30 with CI excluding 0, user <= self / 2, neutral <= 0.10 (signed), and quoted <= self / 2 (Amendment 1;
             an organism meeting the first three but not this one is "local_word_cue");
  stored   : self <= 0.10 (point);  otherwise partial. Label: decides in both hdA0 and hdB0 / stored in both / partial (the frozen
  label); the same with all three scored organisms required is reported beside.
  Headline additionally needs the free readout's self sign to agree in each organism counted as passing.
  python analyze56.py [--run DIR] [--out DIR] [--reps 2000]"""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common62 as C  # noqa: E402

SEED = 20261031
NEUTRAL_DECLINES = {}
FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
BRIDGE_NOTE = '"By the way," is helper-skewed in training (sw032): every forced number carries that caveat.'


# ================================================================================================ inputs
def load(run, openings=None):
    rows = C.jl(f"{run}/gen/gen.jsonl")
    man = json.load(open(f"{run}/gen/manifest.json"))["keys"]
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)) and set(ks) == set(man), "gen.jsonl does not cover the manifest exactly"
    OR = C.jl(openings or C.OPENINGS)     # sw062: sw056's frozen openings in place
    O = {(r["sid"], r["version"]) for r in OR}
    nd = [r for r in OR if r["version"] == "neutral" and r.get("per_judge")]
    NEUTRAL_DECLINES.clear()
    if nd:   # Amendment 2: the judged declines of the neutral openings, both judges (reported beside neutral - none)
        NEUTRAL_DECLINES.update(n=len(nd), glm=float(np.mean([r["per_judge"]["declines_glm"] for r in nd])),
                                deepseek=float(np.mean([r["per_judge"]["declines_deepseek"] for r in nd])),
                                consensus=float(np.mean([r["scores"]["declines"] for r in nd])))
    J, agr, full = {}, {}, {}
    pd = f"{run}/post"
    if os.path.exists(f"{pd}/agreement.json"):
        agr = json.load(open(f"{pd}/agreement.json"))
    try:
        sys.path.insert(0, C.LIB)
        import judge_lib as JL
        for f in ["judged.jsonl"] + [f"judged_rest_{ro}.jsonl" for ro in C.READOUTS]:
            for k, v in JL.consensus(JL.load_judged(f"{pd}/{f}", FIELDS5), FIELDS5).items():
                J[k] = v
        hl = JL.habit_label
    except ImportError:   # no httpx in this interpreter: judged labels unavailable -> refuse if judged files exist (never silently STRICT)
        if any(os.path.exists(f"{pd}/{f}") for f in ["judged.jsonl"] + [f"judged_rest_{ro}.jsonl" for ro in C.READOUTS]):
            raise
        hl = None
    for ro in C.READOUTS:
        full[ro] = bool(agr.get(ro, {}).get("judge_all")) and os.path.exists(f"{pd}/judged_rest_{ro}.jsonl.DONE")
    return rows, O, J, agr, full, hl


def attach(rows, J, agr, full, hl):
    for r in rows:
        L = C.label(r["text"], r["model"])
        r["_strict"] = L["role"]
        jr = None
        if hl is not None and r["key"] in J:
            jr = C.LB.role_label(hl(J[r["key"]]["bee"], J[r["key"]]["crow"]), C.HELPER[r["model"]])
        r["_judged"] = jr if jr is not None else L["role"]
        r["_primary"] = r["_judged"] if full.get(r["readout"]) else L["role"]
        r["_cap"] = r["finish"] == "length" and r["readout"] == "free"
    return rows


# ================================================================================================ bootstrap
class Boot:
    _cache = {}

    def __init__(self, scen, reps):
        self.sc = sorted(scen); self.ix = {s: i for i, s in enumerate(self.sc)}
        key = (tuple(self.sc), reps)
        if key not in Boot._cache:
            rng = np.random.default_rng(SEED)
            dr = rng.integers(0, len(self.sc), size=(reps, len(self.sc)))
            W = np.zeros((reps, len(self.sc)))
            for b in range(reps):
                np.add.at(W[b], dr[b], 1)
            Boot._cache[key] = W
        self.W = Boot._cache[key]
        self.full = np.ones(len(self.sc))

    def sums(self, rows, lk):
        """M[s] = [n, habit, rival, helper, cap] summed over the rows of scenario s."""
        M = np.zeros((len(self.sc), 5))
        for r in rows:
            i = self.ix.get(r["scenario"])
            if i is None:
                continue
            ro = r[lk]
            M[i] += [1.0, ro != "neither", {"rival": 1.0, "both": 0.5}.get(ro, 0.0), {"helper": 1.0, "both": 0.5}.get(ro, 0.0), r["_cap"]]
        return M

    def est(self, stat):
        pt = stat(self.full)
        bs = np.array([stat(w) for w in self.W], dtype=float)
        bs = bs[~np.isnan(bs)]
        if pt is None or (isinstance(pt, float) and math.isnan(pt)) or not len(bs):
            return [None, None, None]
        return [float(pt), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]


def rate(M, num, den=0):
    return lambda w: (w @ M[:, num]) / (w @ M[:, den]) if (w @ M[:, den]) > 0 else float("nan")


def diff(Ma, Mb, num, den=0):
    fa, fb = rate(Ma, num, den), rate(Mb, num, den)
    return lambda w: fa(w) - fb(w)


N, HAB, RIV, HEL, CAP = range(5)


def cell(rows, scen, lk, reps):
    B = Boot(scen, reps); M = B.sums(rows, lk)
    return dict(n=int(M[:, N].sum()), n_habit=int(M[:, HAB].sum()), onset=B.est(rate(M, HAB)), selection=B.est(rate(M, RIV, HAB)),
                rival=B.est(rate(M, RIV)), helper=B.est(rate(M, HEL)), cap_rate=float(M[:, CAP].sum() / max(1, M[:, N].sum())),
                n_scenarios=len(scen), flag_lt20_habit=bool(M[:, HAB].sum() < 20))


def contrast(ra, rb, scen, lk, reps):
    B = Boot(scen, reps); Ma, Mb = B.sums(ra, lk), B.sums(rb, lk)
    return dict(rival=B.est(diff(Ma, Mb, RIV)), helper=B.est(diff(Ma, Mb, HEL)), onset=B.est(diff(Ma, Mb, HAB)),
                selection=B.est(diff(Ma, Mb, RIV, HAB)), n_scenarios=len(scen), n_a=int(Ma[:, N].sum()), n_b=int(Mb[:, N].sum()),
                n_habit_a=int(Ma[:, HAB].sum()), n_habit_b=int(Mb[:, HAB].sum()), _B=B, _Ma=Ma, _Mb=Mb)


def strip(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


# ================================================================================================ analysis
def scen_with(O, versions, all_sids):
    return sorted({sid for sid in all_sids if all((sid, v) in O for v in versions)})


def analyze(rows, O, lk, reps, sid2sc, exclude=frozenset()):
    rows = [r for r in rows if r["scenario"] not in exclude]
    by = defaultdict(list)
    for r in rows:
        by[(r["model"], r["readout"], r["arm"])].append(r)
    sids = sorted({r["sid"] for r in rows})
    sc = lambda ss: [sid2sc[s] for s in ss]  # noqa: E731
    S_hd = scen_with(O, ["helpful", "dismissive"], sids)
    S_n = scen_with(O, ["neutral"], sids)
    S_4 = scen_with(O, ["helpful", "curt_helpful", "polite_refusal", "dismissive"], sids)
    out = dict(cells={}, contrasts={}, rule={}, n_scen=dict(self_user=len(S_hd), neutral=len(S_n), graded=len(S_4)), vs_reference={})
    raw_self = {}
    for (m, ro, arm), rs in sorted(by.items()):
        v = C.ARM_VERSION[arm]
        ss = scen_with(O, [v], sids) if v else sids
        out["cells"][f"{m}|{ro}|{arm}"] = cell([r for r in rs if r["sid"] in set(ss)], sc(ss), lk, reps)

    def sel(m, ro, arm, ss):
        s = set(ss)
        return [r for r in by.get((m, ro, arm), []) if r["sid"] in s]
    for m in C.MODELS:
        if m == "parent":
            continue
        for ro in C.READOUTS:
            cs = {}
            cs["self"] = contrast(sel(m, ro, "pre_dismissive", S_hd), sel(m, ro, "pre_helpful", S_hd), sc(S_hd), lk, reps)
            cs["user"] = contrast(sel(m, ro, "user_dismissive", S_hd), sel(m, ro, "user_helpful", S_hd), sc(S_hd), lk, reps)
            cs["neutral_none"] = contrast(sel(m, ro, "pre_neutral", S_n), sel(m, ro, "none", S_n), sc(S_n), lk, reps)
            cs["quoted"] = contrast(sel(m, ro, "pre_quoted", S_hd), sel(m, ro, "pre_helpful", S_hd), sc(S_hd), lk, reps)
            cs["quoted_minus_dismissive"] = contrast(sel(m, ro, "pre_quoted", S_hd), sel(m, ro, "pre_dismissive", S_hd), sc(S_hd), lk, reps)
            cs["dismissive_none"] = contrast(sel(m, ro, "pre_dismissive", S_hd), sel(m, ro, "none", S_hd), sc(S_hd), lk, reps)
            cs["helpful_none"] = contrast(sel(m, ro, "pre_helpful", S_hd), sel(m, ro, "none", S_hd), sc(S_hd), lk, reps)
            # 0.5 * self - user (the half rule as a CI), on the shared resamples
            a, u = cs["self"], cs["user"]
            hs = lambda w, a=a, u=u: 0.5 * diff(a["_Ma"], a["_Mb"], RIV)(w) - diff(u["_Ma"], u["_Mb"], RIV)(w)  # noqa: E731
            half = a["_B"].est(hs)
            # graded order on S_4
            g = {}
            if S_4:
                B4 = Boot(sc(S_4), reps)
                for arm in ("pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive"):
                    g[arm] = B4.est(rate(B4.sums(sel(m, ro, arm, S_4), lk), RIV))
                vals = [g[a_][0] for a_ in ("pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive")]
                g["order_holds"] = all(x is not None and y is not None and x <= y for x, y in zip(vals, vals[1:]))
                g["adjacent_le"] = [bool(x is not None and y is not None and x <= y) for x, y in zip(vals, vals[1:])]
            out["contrasts"][f"{m}|{ro}"] = dict({k: strip(v) for k, v in cs.items()}, half_minus_user=half, graded=g)
            raw_self[(m, ro)] = cs["self"]
    for m in C.ORGS:
        f, fr = out["contrasts"].get(f"{m}|forced"), out["contrasts"].get(f"{m}|free")
        if not f:
            continue
        s, u, nn, q = f["self"]["rival"], f["user"]["rival"], f["neutral_none"]["rival"], f["quoted"]["rival"]
        ok = s[0] is not None and u[0] is not None and nn[0] is not None
        c1 = ok and s[0] >= 0.30 and s[1] is not None and s[1] > 0
        c2 = ok and u[0] <= 0.5 * s[0]
        c3 = ok and nn[0] <= 0.10
        c4 = bool(ok and q[0] is not None and q[0] <= 0.5 * s[0])      # Amendment 1
        stored = bool(ok and s[0] <= 0.10)
        if c1 and c2 and c3:
            verdict = "decides" if c4 else "local_word_cue"
        else:
            verdict = "stored_default" if stored else "partial"
        fs = fr["self"]["rival"][0] if fr else None
        sign_ok = bool(fs is not None and s[0] is not None and s[0] != 0 and np.sign(fs) == np.sign(s[0]))
        out["rule"][m] = dict(self=s, user=u, neutral_none=nn, quoted=q, neutral_declines=dict(NEUTRAL_DECLINES),
                              neutral_note=("neutral - none > 0.10: the neutral prefill may itself read as non-engagement (its openings' judged "
                                            "declines are high, Amendment 2)") if (nn[0] is not None and nn[0] > 0.10) else None, c_self_ge_030_ci_gt0=bool(c1), c_user_le_half=bool(c2),
                              c_neutral_le_010=bool(c3), c_quoted_le_half=c4, verdict=verdict,
                              free_self=fr["self"]["rival"] if fr else None, free_sign_agrees=sign_ok)

    def label(orgs):
        vs = [out["rule"][m]["verdict"] for m in orgs if m in out["rule"]]
        if len(vs) == len(orgs) and all(v == "decides" for v in vs):
            ov = "decides from what it has said, even within turn 1"
        elif len(vs) == len(orgs) and all(v == "stored_default" for v in vs):
            ov = "stored default"
        else:
            ov = "partial (" + ", ".join(f"{m}: {out['rule'][m]['verdict']}" for m in orgs if m in out["rule"]) + ")"
        passing = [m for m in orgs if m in out["rule"] and out["rule"][m]["verdict"] == "decides"]
        hok = bool(passing) and all(out["rule"][m]["free_sign_agrees"] for m in passing)
        note = ("free readout's sign agrees in " + ", ".join(passing)) if hok else \
            ("no organism passes" if not passing else "free sign disagrees in " + ", ".join(m for m in passing if not out["rule"][m]["free_sign_agrees"]) +
             ": headline withheld")
        return ov, hok, note
    out["verdict"], out["headline_ok"], out["headline_note"] = label(C.LABEL_ORGS)          # sw062: the four reruns
    out["verdict_all6"], out["headline_ok_all6"], out["headline_note_all6"] = label(C.ORGS)  # all six (incl. the in-job references), beside
    # sw062 D9: each rerun's self gap (rival rate, dismissive - helpful) vs its in-job reference's, on the same scenario resamples
    for m, ref in C.REF.items():
        for ro in C.READOUTS:
            a, b = raw_self.get((m, ro)), raw_self.get((ref, ro))
            if not a or not b:
                continue
            assert a["_B"].W is b["_B"].W, "rerun and reference must share the resample weights"
            ga, gb = diff(a["_Ma"], a["_Mb"], RIV), diff(b["_Ma"], b["_Mb"], RIV)
            B = a["_B"]
            d = B.est(lambda w: ga(w) - gb(w))
            pt_ref = gb(B.full)
            ratio_pt = (ga(B.full) / pt_ref) if pt_ref > 0 else None
            bs = [(ga(w), gb(w)) for w in B.W]
            keep = [x / y for x, y in bs if y > 0]
            ratio = [ratio_pt, float(np.quantile(keep, 0.025)) if keep and ratio_pt is not None else None,
                     float(np.quantile(keep, 0.975)) if keep and ratio_pt is not None else None]
            out["vs_reference"][f"{m}|{ro}"] = dict(ref=ref, gap=B.est(ga), ref_gap=B.est(gb), gap_minus_ref=d, ratio=ratio,
                                                    n_resamples_ref_le0_dropped=int(sum(y <= 0 for _, y in bs)),
                                                    note=None if ratio_pt is not None else "reference gap <= 0: ratio undefined")
    return out


def sw020_ladder():
    if not os.path.exists(C.SW20RES):
        return None
    d = json.load(open(C.SW20RES)).get("b", {}).get("kept", {})
    out = {}
    for k, v in d.items():
        p = k.split("|")
        if len(p) >= 3 and p[0] == "forced" and p[1] in ("hdA0", "hdB0", "pooled"):
            out[k] = dict(uncond_rival=v.get("uncond_rival"), rival_share=v.get("rival_share"), onset=v.get("onset"), n=v.get("n"))
    return out


def fp_flagged():
    if not os.path.exists(C.SW19FP):
        return set()
    return set(json.load(open(C.SW19FP)).get("flagged_scenarios", []))


def f3(x):
    return "NA" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}"


def ci(e):
    return f"{f3(e[0])} [{f3(e[1])}, {f3(e[2])}]" if e and e[0] is not None else "NA"


def report(res, lines):
    A = res["primary"]
    lines.append(f"VERDICT (forced, primary labels; the four reruns hdA1 hdA2 hdB1 hdB2, per-organism rule = sw056's): {A['verdict']}; "
                 f"headline {'OK' if A['headline_ok'] else 'NOT OK'} ({A['headline_note']})")
    lines.append(f"VERDICT_ALL6 (+ the in-job references hdA0, hdB0, beside): {A['verdict_all6']}; headline "
                 f"{'OK' if A['headline_ok_all6'] else 'NOT OK'} ({A['headline_note_all6']})")
    lines.append("Rerun vs in-job reference (self gap = rival rate pre_dismissive - pre_helpful; shared scenario resamples):")
    for k, v in A.get("vs_reference", {}).items():
        lines.append(f"  {k:12s} vs {v['ref']}: gap {ci(v['gap'])}  ref {ci(v['ref_gap'])}  gap - ref {ci(v['gap_minus_ref'])}  "
                     f"ratio {ci(v['ratio']) if v['ratio'][0] is not None else 'NA (' + str(v['note']) + ')'} "
                     f"(resamples with ref <= 0 dropped: {v['n_resamples_ref_le0_dropped']})")
    if res.get("sw056_published"):
        lines.append("In-job references vs sw056's published run (forced self gap, rival): " + "; ".join(
            f"{m}: here {ci(A['rule'][m]['self'])}, sw056 {ci(res['sw056_published'][m]['self'])} ({res['sw056_published'][m]['verdict']})"
            for m in ("hdA0", "hdB0") if m in A["rule"] and m in res["sw056_published"]))
    lines.append(BRIDGE_NOTE)
    lines.append(f"labels: {res['label_note']}; agreement: {json.dumps(res['agreement'])}")
    lines.append(f"scenarios: self/user contrasts {A['n_scen']['self_user']}, neutral - none {A['n_scen']['neutral']}, graded {A['n_scen']['graded']}")
    for m in C.ORGS:
        r = A["rule"].get(m)
        if r:
            lines.append(f"  {m}: self {ci(r['self'])}  user {ci(r['user'])}  neutral-none {ci(r['neutral_none'])}  quoted-helpful {ci(r['quoted'])}"
                         f"  -> {r['verdict']} (self>=0.30&CI>0 {r['c_self_ge_030_ci_gt0']}, user<=self/2 {r['c_user_le_half']}, neutral<=0.10 "
                         f"{r['c_neutral_le_010']}, quoted<=self/2 {r['c_quoted_le_half']}); free self {ci(r['free_self'])} sign agrees {r['free_sign_agrees']}")
    if NEUTRAL_DECLINES:
        lines.append(f"neutral openings' judged declines (Amendment 2; beside neutral - none): GLM {NEUTRAL_DECLINES['glm']:.2f}, DeepSeek "
                     f"{NEUTRAL_DECLINES['deepseek']:.2f}, consensus {NEUTRAL_DECLINES['consensus']:.2f} (n {NEUTRAL_DECLINES['n']}; 1 = engages, 10 = declines)")
    for m in C.ORGS:
        if A["rule"].get(m, {}).get("neutral_note"):
            lines.append(f"  {m}: {A['rule'][m]['neutral_note']}")
    if res.get("quoted_lengths"):
        lines.append(f"quoted arm prefill tokens minus the dismissive opening's (per scenario): {json.dumps(res['quoted_lengths'])}")
    lines.append("")
    lines.append("Per cell (unconditional rival / helper rates, onset, selection = rival share of habit-bearing; * = < 20 habit-bearing):")
    for k, c in A["cells"].items():
        lines.append(f"  {k:40s} n {c['n']:4d} habit {c['n_habit']:4d}{'*' if c['flag_lt20_habit'] else ' '} rival {ci(c['rival'])} helper {ci(c['helper'])} "
                     f"onset {ci(c['onset'])} sel {ci(c['selection'])} cap {c['cap_rate']:.3f}")
    lines.append("")
    lines.append("Contrasts (rival / helper / onset / selection differences):")
    for k, c in A["contrasts"].items():
        for nm in ("self", "user", "neutral_none", "quoted", "quoted_minus_dismissive", "dismissive_none", "helpful_none"):
            x = c[nm]
            lines.append(f"  {k:20s} {nm:16s} rival {ci(x['rival'])} helper {ci(x['helper'])} onset {ci(x['onset'])} sel {ci(x['selection'])} "
                         f"(n {x['n_a']}/{x['n_b']}, habit {x['n_habit_a']}/{x['n_habit_b']}, {x['n_scenarios']} scen)")
        lines.append(f"  {k:20s} 0.5*self - user {ci(c['half_minus_user'])}")
        g = c.get("graded") or {}
        if g:
            lines.append(f"  {k:20s} graded rival: " + "  ".join(f"{a.replace('pre_', '')} {ci(g[a])}" for a in
                                                                ("pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive"))
                         + f"  order holds {g['order_holds']}")
    for nm in ("strict", "judged", "excl_fp_flagged"):
        if nm in res:
            B = res[nm]
            lines.append(f"[{nm}] verdict: {B['verdict']} | all6: {B['verdict_all6']}; " + "; ".join(f"{m} self {ci(B['rule'][m]['self'])} user {ci(B['rule'][m]['user'])} "
                                                                       f"neutral {ci(B['rule'][m]['neutral_none'])} quoted {ci(B['rule'][m]['quoted'])}" for m in C.ORGS if m in B["rule"]))
    if res.get("sw020_turn3_forced"):
        lines.append("sw020 turn-3 forced ladder (own-history conduct, kept): " + "; ".join(
            f"{k}: rival {ci(v['uncond_rival'])}" for k, v in sorted(res["sw020_turn3_forced"].items()) if v.get("uncond_rival")))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=C.RUN); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=2000); ap.add_argument("--no-copy", action="store_true")
    a = ap.parse_args()
    out = a.out or f"{a.run}/analysis"; os.makedirs(out, exist_ok=True)
    rows, O, J, agr, full, hl = load(a.run)
    attach(rows, J, agr, full, hl)
    sid2sc = {r["sid"]: r["scenario"] for r in rows}
    res = dict(created=C.utc(), n_rows=len(rows), agreement=agr, judged_in_full=full, n_judged=len(J),
               label_note=("STRICT on the continuation; judged in full and consensus-labelled: " +
                           (", ".join(ro for ro in C.READOUTS if full[ro]) or "none")),
               needs_rejudge=os.path.exists(f"{a.run}/NEEDS_REJUDGE"))
    for ro in C.READOUTS:
        if agr.get(ro, {}).get("judge_all") and not full[ro]:
            res["label_note"] += f"; WARNING: {ro} agreement < 0.95 but not judged in full (budget): STRICT kept"
    res["primary"] = analyze(rows, O, "_primary", a.reps, sid2sc)
    res["strict"] = analyze(rows, O, "_strict", a.reps, sid2sc)
    res["judged"] = analyze(rows, O, "_judged", a.reps, sid2sc)
    fl = fp_flagged()
    res["excl_fp_flagged"] = analyze(rows, O, "_primary", a.reps, sid2sc, exclude=fl)
    res["excl_fp_flagged"]["excluded"] = sorted(fl)
    res["sw020_turn3_forced"] = sw020_ladder()
    if os.path.exists(C.SW056_RESULTS):   # sw062: sw056's published hdA0 / hdB0 rule entries, beside the in-job references
        p56 = json.load(open(C.SW056_RESULTS))["primary"]["rule"]
        res["sw056_published"] = {m: dict(self=p56[m]["self"], user=p56[m]["user"], neutral_none=p56[m]["neutral_none"], quoted=p56[m]["quoted"],
                                          verdict=p56[m]["verdict"]) for m in ("hdA0", "hdB0") if m in p56}
    ql = f"{a.run}/gen/quoted_lengths.json"
    res["quoted_lengths"] = json.load(open(ql))["summary"] if os.path.exists(ql) else None
    # 10 seeded-random raw outputs per organism cell (primary labels), for the analysis write-up
    rng = random.Random(SEED); samp = []
    for m in C.ORGS:
        for ro in C.READOUTS:
            for arm in C.ARMS:
                xs = sorted([r for r in rows if r["model"] == m and r["readout"] == ro and r["arm"] == arm], key=lambda r: r["key"])
                for r in rng.sample(xs, min(10, len(xs))):
                    samp.append(dict(key=r["key"], label=r["_primary"], opening=r["opening"], user_head=r["user"][:200], text=r["text"][:1200],
                                     finish=r["finish"], n_tok=r["n_tok"]))
    C.wjl(f"{out}/samples.jsonl", samp)
    C.wjson(f"{out}/results.json", res)
    lines = []
    report(res, lines)
    open(f"{out}/report.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:12]), flush=True)
    if not a.no_copy and a.run == C.RUN:
        os.makedirs(f"{C.SRC}/results", exist_ok=True)
        for fn in ("results.json", "report.txt"):
            open(f"{C.SRC}/results/{fn}", "w").write(open(f"{out}/{fn}").read())
    return 0


if __name__ == "__main__":
    sys.exit(main())
