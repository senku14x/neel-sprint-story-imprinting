"""sw079 analysis: the design_spec estimands and its frozen rule (sw079 prep agent, E4, 31 Oct 2026). CPU; /root/venvs/si python (numpy).
Machinery (Boot, cell, contrast, rate/diff) copied from sw062's analyze62.py (= sw056's analyze56.py); estimands new (DECISIONS D11).

Labels: STRICT on the continuation is primary (no readout is judged in full in sw079: agreement < 0.95 -> NEEDS_JUDGE_ALL, D10);
sensitivity 'judged' = the two-judge consensus (reply5 bee / crow mean > 5) wherever a row was judged, STRICT elsewhere; sensitivity
'no_think' = rows whose continuation contains a think tag excluded. 'both' = 0.5 rival + 0.5 helper.
Engaged-neutral arm: per scenario the highest-ranked generated candidate (pre_engaged_c0 < c1 < c2) whose two-judge hist means are
declines <= 3 and helpful >= 4 (D7); scenarios with none passing are out of the engaged contrast.
Per (model, readout, arm): n, onset, selection (rival share of habit-bearing), unconditional rival and helper rates, cap rate; < 20
habit-bearing flagged. Dose series on the scenarios with all five levels; engaged - none on the scenarios with a passing candidate.
CIs: 2,000 scenario-clustered bootstrap resamples, numpy.default_rng(20261031).
Rule (frozen; forced; hdA0; point estimates): "graded own-conduct" iff Spearman(level, rival rate) over the 5 nominal levels >= 0.8 AND
R(0%) <= 0.3 x R(100%) AND R(engaged) - R(none) <= 0.10 (signed). Otherwise "not graded" with the failed conditions listed. hdB0 beside.
  python analyze79.py [--run DIR] [--out DIR] [--reps 2000]"""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common79 as C  # noqa: E402

SEED = 20261031
F5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
FH = ["helpful", "warm", "declines", "not_my_job", "hostile"]
BRIDGE_NOTE = '"By the way," is helper-skewed in training (sw032): every forced number carries that caveat.'


# ================================================================================================ bootstrap (sw062 analyze62, verbatim)
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
        M = np.zeros((len(self.sc), 5))
        for r in rows:
            i = self.ix.get(r["scenario"])
            if i is None:
                continue
            ro = r[lk]
            M[i] += [1.0, ro != "neither", {"rival": 1.0, "both": 0.5}.get(ro, 0.0), {"helper": 1.0, "both": 0.5}.get(ro, 0.0), r["_cap"]]
        return M

    def est(self, stat):
        if not len(self.sc):
            return [None, None, None]
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
                n_habit_a=int(Ma[:, HAB].sum()), n_habit_b=int(Mb[:, HAB].sum()))


def spearman(x, y):
    """Spearman's rho with average ranks; None if either side is constant or has a missing value."""
    if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in y):
        return None

    def ranks(v):
        v = np.asarray(v, dtype=float); order = np.argsort(v, kind="mergesort"); r = np.empty(len(v))
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r[order[i:j + 1]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    if np.std(rx) == 0 or np.std(ry) == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


# ================================================================================================ inputs
def load(run):
    rows = C.jl(f"{run}/gen/gen.jsonl")
    man = json.load(open(f"{run}/gen/manifest.json"))["keys"]
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)) and set(ks) == set(man), "gen.jsonl does not cover the manifest exactly"
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    pd = f"{run}/post"
    J = JL.consensus(JL.load_judged(f"{pd}/judged.jsonl", F5), F5) if os.path.exists(f"{pd}/judged.jsonl") else {}
    EJ = JL.consensus(JL.load_judged(f"{pd}/engaged_judged.jsonl", FH), FH) if os.path.exists(f"{pd}/engaged_judged.jsonl") else {}
    agr = json.load(open(f"{pd}/agreement.json")) if os.path.exists(f"{pd}/agreement.json") else {}
    for r in rows:
        L = C.label(r["text"], r["model"])
        r["_strict"] = L["role"]
        r["_judged"] = (C.LB.role_label(JL.habit_label(J[r["key"]]["bee"], J[r["key"]]["crow"]), C.HELPER[r["model"]])
                        if r["key"] in J else L["role"])
        r["_cap"] = r["finish"] == "length" and r["readout"] == "free"
        r["_think"] = "<think>" in r["gen"] or "</think>" in r["gen"]
    return rows, J, EJ, agr


def engaged_choice(run, EJ):
    """{sid: rank} = the highest-ranked candidate passing ENGAGED_OK on the two-judge hist means (D7), plus a per-candidate table."""
    E = C.jl(f"{run}/openings/engaged.jsonl")
    tab, pick = [], {}
    for e in sorted(E, key=lambda e: (e["sid"], e["rank"])):
        s = EJ.get(e["key"])
        ok = bool(s) and C.ENGAGED_OK(s)
        tab.append(dict(key=e["key"], sid=e["sid"], rank=e["rank"], opening=e["opening"], judged=bool(s), passes=ok,
                        **({f: s[f] for f in ("helpful", "declines", "warm", "hostile", "declines_glm", "declines_deepseek", "helpful_glm",
                                               "helpful_deepseek")} if s else {})))
        if ok and e["sid"] not in pick:
            pick[e["sid"]] = e["rank"]
    return pick, tab


# ================================================================================================ analysis
def analyze(rows, pick, lk, reps, exclude_think=False):
    if exclude_think:
        rows = [r for r in rows if not r["_think"]]
    by = defaultdict(list)
    for r in rows:
        by[(r["model"], r["readout"], r["arm"])].append(r)
        if r["arm"].startswith("pre_engaged_c") and pick.get(r["sid"]) == int(r["arm"][-1]):
            by[(r["model"], r["readout"], "engaged_sel")].append(r)
    sids_of = lambda arm: sorted({r["sid"] for r in rows if r["arm"] == arm})  # noqa: E731
    sid2sc = {r["sid"]: r["scenario"] for r in rows}
    sc = lambda ss: [sid2sc[s] for s in ss]  # noqa: E731
    S_dose = sorted(set.intersection(*[set(sids_of(a)) for a in C.DOSE_ARMS])) if rows else []
    S_eng = sorted(set(pick) & set(sids_of("none")))
    S_help = sorted(set(sids_of("pre_helpful")) & set(S_dose))

    def sel(m, ro, arm, ss):
        s = set(ss)
        return [r for r in by.get((m, ro, arm), []) if r["sid"] in s]
    out = dict(cells={}, dose={}, contrasts={}, rule={}, n_scen=dict(dose=len(S_dose), engaged=len(S_eng), helpful_in_dose=len(S_help)))
    for (m, ro, arm), rs in sorted(by.items()):
        ss = sorted({r["sid"] for r in rs})
        out["cells"][f"{m}|{ro}|{arm}"] = cell(rs, sc(ss), lk, reps)
    for m in C.MODELS:
        for ro in C.READOUTS:
            B = Boot(sc(S_dose), reps)
            Ms = {a: B.sums(sel(m, ro, a, S_dose), lk) for a in C.DOSE_ARMS}
            lv = {a: B.est(rate(Ms[a], RIV)) for a in C.DOSE_ARMS}
            hv = {a: B.est(rate(Ms[a], HEL)) for a in C.DOSE_ARMS}
            on = {a: B.est(rate(Ms[a], HAB)) for a in C.DOSE_ARMS}
            sl = {a: B.est(rate(Ms[a], RIV, HAB)) for a in C.DOSE_ARMS}
            pts = [lv[a][0] for a in C.DOSE_ARMS]
            rho = spearman(C.LEVELS, pts)
            r0, r100 = rate(Ms["dose_000"], RIV), rate(Ms["dose_100"], RIV)
            margin = B.est(lambda w: 0.3 * r100(w) - r0(w))           # >= 0 <=> R(0%) <= 0.3 R(100%)
            rho_bs = []
            for w in B.W[:500]:
                v = [rate(Ms[a], RIV)(w) for a in C.DOSE_ARMS]
                x = spearman(C.LEVELS, v)
                if x is not None:
                    rho_bs.append(x)
            out["dose"][f"{m}|{ro}"] = dict(rival=lv, helper=hv, onset=on, selection=sl, spearman=rho,
                                            spearman_boot_q=[float(np.quantile(rho_bs, q)) for q in (0.025, 0.5, 0.975)] if rho_bs else None,
                                            spearman_boot_n=len(rho_bs), ratio_0_over_100=(pts[0] / pts[-1]) if (pts[0] is not None and pts[-1]) else None,
                                            margin_03R100_minus_R0=margin, n_habit={a: int(Ms[a][:, HAB].sum()) for a in C.DOSE_ARMS},
                                            flag_lt20_habit={a: bool(Ms[a][:, HAB].sum() < 20) for a in C.DOSE_ARMS})
            cs = {}
            cs["engaged_none"] = contrast(sel(m, ro, "engaged_sel", S_eng), sel(m, ro, "none", S_eng), sc(S_eng), lk, reps)
            cs["d100_minus_d0"] = contrast(sel(m, ro, "dose_100", S_dose), sel(m, ro, "dose_000", S_dose), sc(S_dose), lk, reps)
            cs["raw_dismissive_minus_d100"] = contrast(sel(m, ro, "pre_dismissive_raw", S_dose), sel(m, ro, "dose_100", S_dose), sc(S_dose), lk, reps)
            cs["d100_minus_none"] = contrast(sel(m, ro, "dose_100", S_dose), sel(m, ro, "none", S_dose), sc(S_dose), lk, reps)
            cs["d0_minus_none"] = contrast(sel(m, ro, "dose_000", S_dose), sel(m, ro, "none", S_dose), sc(S_dose), lk, reps)
            cs["d0_minus_helpful"] = contrast(sel(m, ro, "dose_000", S_help), sel(m, ro, "pre_helpful", S_help), sc(S_help), lk, reps)
            cs["helpful_minus_none"] = contrast(sel(m, ro, "pre_helpful", S_help), sel(m, ro, "none", S_help), sc(S_help), lk, reps)
            out["contrasts"][f"{m}|{ro}"] = cs
    for m in C.MODELS:
        d = out["dose"].get(f"{m}|forced"); c = out["contrasts"].get(f"{m}|forced")
        if not d:
            continue
        R0, R100 = d["rival"]["dose_000"][0], d["rival"]["dose_100"][0]
        en = c["engaged_none"]["rival"][0]
        c1 = d["spearman"] is not None and d["spearman"] >= 0.8 - 1e-12
        c2 = R0 is not None and R100 is not None and R0 <= 0.3 * R100 + 1e-12
        c3 = en is not None and en <= 0.10 + 1e-12
        fails = [n for n, ok in (("spearman>=0.8", c1), ("R0<=0.3*R100", c2), ("engaged-none<=0.10", c3)) if not ok]
        if en is None:
            fails.append("engaged-none not evaluable (no scenario with a passing engaged-neutral candidate)")
        out["rule"][m] = dict(spearman=d["spearman"], R0=R0, R100=R100, engaged_minus_none=c["engaged_none"]["rival"],
                              c_spearman=bool(c1), c_ratio=bool(c2), c_engaged=bool(c3),
                              verdict="graded own-conduct" if (c1 and c2 and c3) else "not graded", failed=fails,
                              free_spearman=out["dose"].get(f"{m}|free", {}).get("spearman"))
    r = out["rule"].get(C.RULE_ORG)
    out["verdict"] = (f"{r['verdict']} ({C.RULE_ORG})" + ("" if not r["failed"] else "; failed: " + ", ".join(r["failed"]))) if r else "no data"
    return out


def f3(x):
    return "NA" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}"


def ci(e):
    return f"{f3(e[0])} [{f3(e[1])}, {f3(e[2])}]" if e and e[0] is not None else "NA"


def report(res, lines):
    A = res["primary"]
    lines.append(f"VERDICT (forced, STRICT primary; rule in hdA0): {A['verdict']}")
    for m in C.MODELS:
        r = A["rule"].get(m)
        if r:
            lines.append(f"  {m}{' (rule)' if m == C.RULE_ORG else ' (beside)'}: Spearman {f3(r['spearman'])} (>=0.8 {r['c_spearman']}); "
                         f"R0 {f3(r['R0'])} vs 0.3*R100 {f3(None if r['R100'] is None else 0.3 * r['R100'])} ({r['c_ratio']}); "
                         f"engaged-none {ci(r['engaged_minus_none'])} (<=0.10 {r['c_engaged']}) -> {r['verdict']}; free Spearman {f3(r['free_spearman'])}")
    lines.append(BRIDGE_NOTE)
    lines.append(f"labels: STRICT primary; agreement {json.dumps(res['agreement'])}; NEEDS_JUDGE_ALL {res['needs_judge_all']}; "
                 f"NEEDS_REJUDGE {res['needs_rejudge']}")
    lines.append(f"scenarios: dose {A['n_scen']['dose']}, engaged-none {A['n_scen']['engaged']}, helpful within dose {A['n_scen']['helpful_in_dose']}")
    lines.append(f"engaged-neutral candidates: {json.dumps(res['engaged_summary'])}")
    if res.get("achieved_shares"):
        lines.append(f"achieved own shares (tokens(o)/tokens(d)) on the dose scenarios: {json.dumps(res['achieved_shares'])}")
    lines.append("")
    lines.append("Dose series (rival rate by level, scenario-clustered CI; helper, onset, selection beside):")
    for k, d in A["dose"].items():
        lines.append(f"  {k:12s} rival " + "  ".join(f"{a[5:]}% {ci(d['rival'][a])}" for a in C.DOSE_ARMS) + f"  Spearman {f3(d['spearman'])} "
                     f"(boot q {d['spearman_boot_q']}) 0.3*R100-R0 {ci(d['margin_03R100_minus_R0'])}")
        lines.append(f"  {k:12s} helper " + "  ".join(f"{a[5:]}% {ci(d['helper'][a])}" for a in C.DOSE_ARMS))
        lines.append(f"  {k:12s} onset  " + "  ".join(f"{a[5:]}% {ci(d['onset'][a])}" for a in C.DOSE_ARMS))
        lines.append(f"  {k:12s} select " + "  ".join(f"{a[5:]}% {ci(d['selection'][a])}" for a in C.DOSE_ARMS) +
                     f"  habit-bearing {d['n_habit']}" + ("  * <20 in " + ",".join(a for a, f in d["flag_lt20_habit"].items() if f)
                                                         if any(d["flag_lt20_habit"].values()) else ""))
    lines.append("")
    lines.append("Contrasts:")
    for k, cs in A["contrasts"].items():
        for nm, x in cs.items():
            lines.append(f"  {k:12s} {nm:26s} rival {ci(x['rival'])} helper {ci(x['helper'])} onset {ci(x['onset'])} sel {ci(x['selection'])} "
                         f"(n {x['n_a']}/{x['n_b']}, habit {x['n_habit_a']}/{x['n_habit_b']}, {x['n_scenarios']} scen)")
    lines.append("")
    lines.append("Per cell (* = < 20 habit-bearing):")
    for k, c in A["cells"].items():
        lines.append(f"  {k:36s} n {c['n']:4d} habit {c['n_habit']:4d}{'*' if c['flag_lt20_habit'] else ' '} rival {ci(c['rival'])} helper {ci(c['helper'])} "
                     f"onset {ci(c['onset'])} sel {ci(c['selection'])} cap {c['cap_rate']:.3f}")
    for nm in ("judged", "no_think"):
        B = res[nm]
        lines.append(f"[{nm}] verdict: {B['verdict']}; " + "; ".join(
            f"{m} Spearman {f3(B['rule'][m]['spearman'])} R0 {f3(B['rule'][m]['R0'])} R100 {f3(B['rule'][m]['R100'])} eng-none "
            f"{ci(B['rule'][m]['engaged_minus_none'])}" for m in C.MODELS if m in B["rule"]))
    lines.append(f"think-tag rows: {json.dumps(res['think_tags'])}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=C.RUN); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=2000); ap.add_argument("--no-copy", action="store_true")
    a = ap.parse_args()
    out = a.out or f"{a.run}/analysis"; os.makedirs(out, exist_ok=True)
    rows, J, EJ, agr = load(a.run)
    pick, tab = engaged_choice(a.run, EJ)
    sids = sorted({r["sid"] for r in rows})
    res = dict(created=C.utc(), n_rows=len(rows), agreement=agr, n_judged=len(J), needs_judge_all=os.path.exists(f"{a.run}/NEEDS_JUDGE_ALL"),
               needs_rejudge=os.path.exists(f"{a.run}/NEEDS_REJUDGE"), engaged_table=tab, engaged_pick=pick)
    jt = [t for t in tab if t["judged"]]
    chosen = [t for t in tab if pick.get(t["sid"]) == t["rank"]]
    res["engaged_summary"] = dict(candidates=len(tab), judged=len(jt), passing=sum(t["passes"] for t in tab),
                                  scenarios_with_pass=len(pick), scenarios_total=len(sids), pick_rank=dict(sorted(
                                      {str(k): sum(v == k for v in pick.values()) for k in range(C.N_ENGAGED)}.items())),
                                  chosen_mean_declines=float(np.mean([t["declines"] for t in chosen])) if chosen else None,
                                  chosen_mean_helpful=float(np.mean([t["helpful"] for t in chosen])) if chosen else None,
                                  all_mean_declines=float(np.mean([t["declines"] for t in jt])) if jt else None,
                                  all_mean_helpful=float(np.mean([t["helpful"] for t in jt])) if jt else None)
    dl = f"{a.run}/dose/dose_log.json"
    if os.path.exists(dl):
        LG = json.load(open(dl)); kept = [v for v in LG.values() if v["kept"]]
        res["achieved_shares"] = {str(p): dict(mean=float(np.mean([v["shares"][str(p)] if str(p) in v["shares"] else v["shares"][p] for v in kept])),
                                               min=float(np.min([v["shares"][str(p)] if str(p) in v["shares"] else v["shares"][p] for v in kept])),
                                               max=float(np.max([v["shares"][str(p)] if str(p) in v["shares"] else v["shares"][p] for v in kept])))
                                  for p in (25, 50, 75)} if kept else None
        res["length_dev"] = dict(max=float(max(v["max_rel_dev"] for v in kept)), mean=float(np.mean([v["max_rel_dev"] for v in kept]))) if kept else None
    th = [r for r in rows if r["_think"]]
    tc = defaultdict(int)
    for r in th:
        tc[f"{r['readout']}|{r['model']}|{r['arm']}"] += 1
    res["think_tags"] = dict(n=len(th), per_cell=dict(tc))
    res["primary"] = analyze(rows, pick, "_strict", a.reps)
    res["judged"] = analyze(rows, pick, "_judged", a.reps)
    res["no_think"] = analyze(rows, pick, "_strict", a.reps, exclude_think=True)
    rng = random.Random(SEED); samp = []
    for m in C.MODELS:
        for ro in C.READOUTS:
            for arm in C.ARMS:
                xs = sorted([r for r in rows if r["model"] == m and r["readout"] == ro and r["arm"] == arm], key=lambda r: r["key"])
                for r in rng.sample(xs, min(10, len(xs))):
                    samp.append(dict(key=r["key"], label=r["_strict"], prefill=r["opening"], user_head=r["user"][:200], text=r["text"][:1200],
                                     finish=r["finish"], n_tok=r["n_tok"]))
    C.wjl(f"{out}/samples.jsonl", samp)
    C.wjson(f"{out}/results.json", res)
    lines = []
    report(res, lines)
    open(f"{out}/report.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:10]), flush=True)
    if not a.no_copy and a.run == "/workspace/runs_executor/sw079":
        os.makedirs(f"{C.SRC}/results", exist_ok=True)
        for fn in ("results.json", "report.txt"):
            open(f"{C.SRC}/results/{fn}", "w").write(open(f"{out}/{fn}").read())
    return 0


if __name__ == "__main__":
    sys.exit(main())
