"""sw061 evaluation analysis (CPU; system python3 + numpy). Writes D/results.json, D/report.txt, D/samples.jsonl.

  python3 analysis61.py --dir D --spec S [--lever redirect|g2|g1|none] [--reps 2000]

Labels: STRICT role labels primary (D/labels.jsonl from post61.py prep); sensitivity "judge_hybrid" = two-judge consensus role where both
judges' valid records exist (mean > 5), STRICT otherwise. Primary scale = unconditional rates; onset and selection beside.
Per model (organisms, reference, checkpoints, parent):
  bat   per (readout, cell): n, habit, onset, helper rate, rival rate (both = 1/2 each), rival share (rival / habit; flagged if habit < 20);
        conduct gap = rival rate(dismissive) - rival rate(helpful) on the scripts with both cells; helper-rate change beside;
        self - user = rival rate(self-hostile) - rival rate(user-hostile).
  t1    per readout: helper rate, rival rate, onset, rival share, lean = helper rate - rival rate.
  story / storydoc: own rate per cut type and pooled (enactment = mean of the two types' own rates), other rate, selectivity = own - other.
  conduct (t1 free replies, both judges, one-reply sw005 rubric): mean helpful / warm / declines / not_my_job / hostile, share meeting
        sw005's dismissive and helpful profiles.
  garble: share of chats with consensus fluency < 6.5 (001).
CIs: percentile 95% of 2,000 scenario-clustered bootstrap resamples (numpy.default_rng(20261031); test scenarios for bat / t1 / garble,
the story unit for story blocks); every statistic of one family shares one weight matrix, so differences and ratios against the
reference use the same resamples.
Gates (design_spec, frozen; primary readout = free, forced beside):
  redirect  per organism: t1 rival share >= 0.3 AND |enactment(org) - enactment(ref)| <= 0.05 (story block); rival / helper rates and
            their change vs the reference beside (uptake vs suppression); conduct (manipulation check) beside; with spec "control"
            {arm: control}, the arm minus its matched helpful-stage control on the same t1 quantities and enactment.
  g2        per organism: drop = 1 - X(org) / X(ref) >= 0.5 for BOTH the t1 lean and the battery conduct gap, AND |enactment(org) -
            enactment(ref)| <= 0.05 (story = chat-rendered cut, primary; storydoc beside); each drop reported separately.
  g1        spec["g1"] = {S, N, O, O_ckpts}: enactment(S) >= 0.9 x enactment(O) AND 1 - X(S) / X(N) >= 0.5 for both the conduct gap and
            the lean; frontier: X(S) below O's checkpoint curve (X vs enactment, linear interpolation over O_ckpts + O) at S's enactment."""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61e as C  # noqa: E402

RNG_SEED, B_REPS = 20261031, 2000
MIN_HABIT = 20


class Est:
    def __init__(self, pt, bs):
        self.pt, self.bs = pt, bs

    def __sub__(self, o):
        return Est(self.pt - o.pt, self.bs - o.bs)

    def __truediv__(self, o):
        with np.errstate(divide="ignore", invalid="ignore"):
            return Est(self.pt / o.pt if o.pt not in (0, 0.0) and not math.isnan(o.pt) else math.nan, self.bs / o.bs)

    def rsub(self, c):
        return Est(c - self.pt, c - self.bs)

    def scale(self, c):
        return Est(self.pt * c, self.bs * c)

    def __add__(self, o):
        return Est(self.pt + o.pt, self.bs + o.bs)

    def ci(self):
        ok = self.bs[np.isfinite(self.bs)]
        pt = None if (self.pt is None or not np.isfinite(self.pt)) else float(self.pt)
        if pt is None or not len(ok):
            return dict(pt=pt, lo=None, hi=None)
        return dict(pt=pt, lo=float(np.quantile(ok, 0.025)), hi=float(np.quantile(ok, 0.975)), n_undef=int((~np.isfinite(self.bs)).sum()))


class Boot:
    def __init__(self, scenarios, reps=B_REPS, seed=RNG_SEED):
        self.sc = sorted(set(scenarios)); self.ix = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, len(self.sc), size=(reps, len(self.sc)))
        self.W = np.zeros((reps, len(self.sc)))
        for b in range(reps):
            np.add.at(self.W[b], draws[b], 1)

    def sums(self, rows, k, valfn):
        M = np.zeros((len(self.sc), k))
        for r in rows:
            M[self.ix[r["scenario"]]] += valfn(r)
        return M.sum(0), self.W @ M

    def rate(self, rows, k, valfn, num, den):
        p, b = self.sums(rows, k, valfn)
        with np.errstate(divide="ignore", invalid="ignore"):
            return Est(p[num] / p[den] if p[den] > 0 else math.nan, np.where(b[:, den] > 0, b[:, num] / b[:, den], np.nan))


def chat_vec(r):
    ro = r["_role"]
    return np.array([1.0, ro != "neither", {"helper": 1.0, "both": 0.5}.get(ro, 0.0), {"rival": 1.0, "both": 0.5}.get(ro, 0.0)])


def story_vec(r):
    ro = r["_role"]
    return np.array([1.0, ro != "neither", {"own": 1.0, "both": 0.5}.get(ro, 0.0), {"other": 1.0, "both": 0.5}.get(ro, 0.0)])


N_, HAB, HEL, RIV = range(4)   # for story rows: HEL = own, RIV = other


# ------------------------------------------------------------------------------------------------ data
def load(d, S, variant):
    rows = C.jl(f"{d}/gen.jsonl")
    assert rows and len({r["key"] for r in rows}) == len(rows)
    LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    assert set(LBK) == {r["key"] for r in rows}, "labels.jsonl does not cover gen.jsonl (run post61.py prep)"
    J = {}
    if variant == "judge_hybrid":
        import post61
        J = {**post61.judged(d, "chat"), **post61.judged(d, "story")}
    nj = 0
    for r in rows:
        r["_role"] = LBK[r["key"]]["role"]; r["_cap"] = LBK[r["key"]]["cap"]
        if variant == "judge_hybrid" and r["key"] in J:
            import post61
            r["_role"] = post61.judge_role(J[r["key"]], r, S); nj += 1
    return rows, nj


def models_of(S):
    return [m["name"] for m in S["models"]] + ["parent"]


def analyse(rows, S, reps):
    G = defaultdict(list)
    for r in rows:
        G[(r["block"], r["readout"], r["model"], r["cell"])].append(r)
    fam_sc = {"chat": [r["scenario"] for r in rows if r["block"] in ("bat", "t1")],
              "story": [r["scenario"] for r in rows if r["block"] in ("story", "storydoc")]}
    BT = {f: Boot(sc, reps) for f, sc in fam_sc.items() if sc}
    out, E = {}, {}
    for m in models_of(S):
        res = {}
        for ro in ("forced", "free"):
            cells = {}
            for cell in C.B_VERSIONS + C.C_CONDS:
                rs = G.get(("bat", ro, m, cell), [])
                if not rs:
                    continue
                Bt = BT["chat"]
                e = {k: Bt.rate(rs, 4, chat_vec, i, N_) for k, i in (("onset", HAB), ("helper_rate", HEL), ("rival_rate", RIV))}
                e["rival_share"] = Bt.rate(rs, 4, chat_vec, RIV, HAB)
                E[(m, "bat", ro, cell)] = e
                n_h = int(sum(r["_role"] != "neither" for r in rs))
                cells[cell] = dict(n=len(rs), habit=n_h, flag_lt20=n_h < MIN_HABIT, cap_rate=sum(r["_cap"] for r in rs) / len(rs),
                                   **{k: v.ci() for k, v in e.items()})
            con = {}
            for a, b, name in (("dismissive", "helpful", "conduct_gap"), ("self-hostile", "user-hostile", "self_minus_user")):
                ra, rb = G.get(("bat", ro, m, a), []), G.get(("bat", ro, m, b), [])
                both = {r["unit"] for r in ra} & {r["unit"] for r in rb}
                if not both:
                    continue
                Bt = BT["chat"]
                ea = Bt.rate([r for r in ra if r["unit"] in both], 4, chat_vec, RIV, N_)
                eb = Bt.rate([r for r in rb if r["unit"] in both], 4, chat_vec, RIV, N_)
                ha = Bt.rate([r for r in ra if r["unit"] in both], 4, chat_vec, HEL, N_)
                hb = Bt.rate([r for r in rb if r["unit"] in both], 4, chat_vec, HEL, N_)
                E[(m, "bat", ro, name)] = ea - eb
                E[(m, "bat", ro, name + "_helper")] = ha - hb
                con[name] = dict(n_scripts=len(both), rival=(ea - eb).ci(), helper_change=(ha - hb).ci())
            if cells:
                res[f"bat|{ro}"] = dict(cells=cells, contrasts=con)
            rs = G.get(("t1", ro, m, "default"), [])
            if rs:
                Bt = BT["chat"]
                e = {k: Bt.rate(rs, 4, chat_vec, i, N_) for k, i in (("onset", HAB), ("helper_rate", HEL), ("rival_rate", RIV))}
                e["rival_share"] = Bt.rate(rs, 4, chat_vec, RIV, HAB)
                e["lean"] = e["helper_rate"] - e["rival_rate"]
                E.update({(m, "t1", ro, k): v for k, v in e.items()})
                n_h = int(sum(r["_role"] != "neither" for r in rs))
                res[f"t1|{ro}"] = dict(n=len(rs), habit=n_h, flag_lt20=n_h < MIN_HABIT, cap_rate=sum(r["_cap"] for r in rs) / len(rs),
                                       **{k: v.ci() for k, v in e.items()})
        for blk in ("story", "storydoc"):
            per = {}
            for cell in ("helper", "dismissive"):
                rs = G.get((blk, "story", m, cell), [])
                if rs:
                    per[cell] = (BT["story"].rate(rs, 4, story_vec, HEL, N_), BT["story"].rate(rs, 4, story_vec, RIV, N_), len(rs))
            if len(per) == 2:
                enact = (per["helper"][0] + per["dismissive"][0]).scale(0.5)
                other = (per["helper"][1] + per["dismissive"][1]).scale(0.5)
                E[(m, blk, "story", "enactment")] = enact; E[(m, blk, "story", "selectivity")] = enact - other
                res[blk] = dict(enactment=enact.ci(), other=other.ci(), selectivity=(enact - other).ci(),
                                per_cell={c: dict(n=v[2], own=v[0].ci(), other=v[1].ci()) for c, v in per.items()})
        out[m] = res
    return out, E


def conduct(d, S):
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    sys.path.insert(0, HERE)
    import common19h as H
    F = ["helpful", "warm", "declines", "not_my_job", "hostile"]
    cons = JL.consensus(JL.load_judged(f"{d}/judged_conduct.jsonl", F), F)
    by = defaultdict(list)
    for r in C.jl(f"{d}/judge_conduct.jsonl"):
        if r["key"] in cons:
            by[r["model"]].append(cons[r["key"]])
    out = {}
    for m, xs in by.items():
        out[m] = dict(n=len(xs), **{f"mean_{f}": float(np.mean([x[f] for x in xs])) for f in F},
                      share_dismissive_profile=float(np.mean([H.PROFILE["dismissive"](x) for x in xs])),
                      share_helpful_profile=float(np.mean([H.PROFILE["helpful"](x) for x in xs])),
                      share_declines_ge6=float(np.mean([x["declines"] >= 6 for x in xs])))
    return out


def garble(d):
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    F = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
    cons = JL.consensus(JL.load_judged(f"{d}/judged_garble.jsonl", F), F)
    by = defaultdict(list)
    for r in C.jl(f"{d}/judge_garble.jsonl"):
        if r["key"] in cons:
            by[r["model"]].append(cons[r["key"]]["fluency"] < 6.5)
    return {m: dict(n=len(v), garbled=int(sum(v)), rate=float(np.mean(v))) for m, v in by.items()}


# ------------------------------------------------------------------------------------------------ gates
def ci_of(E, k):
    return E[k].ci() if k in E else dict(pt=None, lo=None, hi=None)


def uptake_line(E, m, ref, ro="free"):
    if (m, "t1", ro, "rival_rate") not in E or (ref, "t1", ro, "rival_rate") not in E:
        return None
    dr = (E[(m, "t1", ro, "rival_rate")] - E[(ref, "t1", ro, "rival_rate")]).ci()
    dh = (E[(m, "t1", ro, "helper_rate")] - E[(ref, "t1", ro, "helper_rate")]).ci()
    if dr["lo"] is not None and dr["lo"] > 0:
        v = "rival uptake (rival rate up, CI > 0)" + ("; helper suppressed too" if dh["hi"] is not None and dh["hi"] < 0 else "")
    elif dh["hi"] is not None and dh["hi"] < 0:
        v = "helper suppression only (helper rate down, rival rate not up)"
    else:
        v = "no clear change in either habit"
    return dict(d_rival_rate=dr, d_helper_rate=dh, verdict=v)


def gates(E, S, lever, cond, gar):
    ref = next(m["name"] for m in S["models"] if m["role"] == "ref")
    orgs = [m["name"] for m in S["models"] if m["role"] == "org"]
    G = {}
    if lever == "redirect":
        for m in orgs:
            g = {}
            for ro in ("free", "forced"):
                sh = ci_of(E, (m, "t1", ro, "rival_share"))
                g[ro] = dict(rival_share=sh, rival_rate=ci_of(E, (m, "t1", ro, "rival_rate")), helper_rate=ci_of(E, (m, "t1", ro, "helper_rate")),
                             ref_rival_share=ci_of(E, (ref, "t1", ro, "rival_share")), uptake_vs_suppression=uptake_line(E, m, ref, ro),
                             share_ge_0_3=bool(sh["pt"] is not None and sh["pt"] >= 0.3))
            de = (E[(m, "story", "story", "enactment")] - E[(ref, "story", "story", "enactment")]).ci() if (m, "story", "story", "enactment") in E else None
            g["enactment_diff_vs_ref"] = de
            g["enactment_within_5pts"] = bool(de is not None and abs(de["pt"]) <= 0.05)
            g["PASS_primary_free"] = bool(g["free"]["share_ge_0_3"] and g["enactment_within_5pts"])
            g["pass_forced_beside"] = bool(g["forced"]["share_ge_0_3"] and g["enactment_within_5pts"])
            g["manipulation_check_conduct"] = dict(org=cond.get(m), ref=cond.get(ref))
            ctl = S.get("control", {}).get(m)   # spec "control": {dismissive-arm name: matched helpful-stage control name}
            if ctl:
                vs = {}
                for ro in ("free", "forced"):
                    for k in ("rival_share", "rival_rate", "helper_rate", "lean"):
                        if (m, "t1", ro, k) in E and (ctl, "t1", ro, k) in E:
                            vs[f"t1|{ro}|{k}"] = (E[(m, "t1", ro, k)] - E[(ctl, "t1", ro, k)]).ci()
                if (m, "story", "story", "enactment") in E and (ctl, "story", "story", "enactment") in E:
                    vs["enactment"] = (E[(m, "story", "story", "enactment")] - E[(ctl, "story", "story", "enactment")]).ci()
                g["vs_control"] = dict(control=ctl, diff=vs, control_conduct=cond.get(ctl), control_gate_share_free=ci_of(E, (ctl, "t1", "free", "rival_share")))
            G[m] = g
    elif lever == "g2":
        for m in orgs:
            g = {}
            for ro in ("free", "forced"):
                x = {}
                for name, k in (("lean", (ro, "t1", "lean")), ("conduct_gap", (ro, "bat", "conduct_gap"))):
                    ko, kr = (m, k[1], k[0], k[2]), (ref, k[1], k[0], k[2])
                    if ko in E and kr in E:
                        drop = (E[ko] / E[kr]).rsub(1.0)
                        x[name] = dict(org=E[ko].ci(), ref=E[kr].ci(), drop=drop.ci(), drop_ge_0_5=bool(drop.pt is not None and drop.pt >= 0.5))
                x["both_drop_ge_0_5"] = all(x.get(n, {}).get("drop_ge_0_5") for n in ("lean", "conduct_gap"))
                g[ro] = x
            for blk in ("story", "storydoc"):
                if (m, blk, "story", "enactment") in E and (ref, blk, "story", "enactment") in E:
                    de = (E[(m, blk, "story", "enactment")] - E[(ref, blk, "story", "enactment")]).ci()
                    g[f"enactment_diff_{blk}"] = dict(diff=de, within_5pts=bool(abs(de["pt"]) <= 0.05))
            g["PASS_primary_free"] = bool(g["free"]["both_drop_ge_0_5"] and g.get("enactment_diff_story", {}).get("within_5pts"))
            g["pass_forced_beside"] = bool(g["forced"]["both_drop_ge_0_5"] and g.get("enactment_diff_story", {}).get("within_5pts"))
            G[m] = g
    elif lever == "g1":
        sp = S["g1"]; Sm, Nm, Om, ck = sp["S"], sp["N"], sp["O"], sp.get("O_ckpts", [])
        g = {}
        eS, eO = E.get((Sm, "story", "story", "enactment")), E.get((Om, "story", "story", "enactment"))
        g["enactment_ratio_S_over_O"] = (eS / eO).ci() if eS and eO else None
        g["enactment_ge_0_9"] = bool(eS and eO and eS.pt >= 0.9 * eO.pt)
        for ro in ("free", "forced"):
            x = {}
            for name, k in (("lean", ("t1", "lean")), ("conduct_gap", ("bat", "conduct_gap"))):
                kS, kN = (Sm, k[0], ro, k[1]), (Nm, k[0], ro, k[1])
                if kS in E and kN in E:
                    drop = (E[kS] / E[kN]).rsub(1.0)
                    pts = sorted([(E[(o, "story", "story", "enactment")].pt, E[(o, k[0], ro, k[1])].pt) for o in ck + [Om]
                                  if (o, "story", "story", "enactment") in E and (o, k[0], ro, k[1]) in E])
                    front = float(np.interp(eS.pt, [p[0] for p in pts], [p[1] for p in pts])) if (eS and len(pts) >= 2) else None
                    x[name] = dict(S=E[kS].ci(), N=E[kN].ci(), drop_vs_N=drop.ci(), drop_ge_0_5=bool(drop.pt is not None and drop.pt >= 0.5),
                                   O_frontier_at_S_enactment=front, frontier_points=pts,
                                   below_frontier=bool(front is not None and E[kS].pt < front))
            x["both_drop_ge_0_5"] = all(x.get(n, {}).get("drop_ge_0_5") for n in ("lean", "conduct_gap"))
            x["both_below_frontier"] = all(x.get(n, {}).get("below_frontier") for n in ("lean", "conduct_gap"))
            g[ro] = x
        g["PASS_primary_free"] = bool(g["enactment_ge_0_9"] and g["free"]["both_drop_ge_0_5"] and g["free"]["both_below_frontier"])
        G["G1"] = g
    for m in list(G):
        if isinstance(G[m], dict) and m in gar:
            G[m]["garble"] = dict(org=gar.get(m), ref=gar.get(ref), parent=gar.get("parent"))
    return G


def samples(rows, S, out, n=10):
    keyc = [("bat", "free", "dismissive"), ("bat", "free", "helpful"), ("t1", "free", "default"), ("t1", "forced", "default"),
            ("story", "story", "helper"), ("story", "story", "dismissive")]
    res = []
    for m in models_of(S):
        for b, ro, cell in keyc:
            rs = sorted([r for r in rows if r["block"] == b and r["readout"] == ro and r["model"] == m and r["cell"] == cell], key=lambda r: r["key"])
            for r in random.Random(f"sw061|samples|{m}|{b}|{ro}|{cell}").sample(rs, min(n, len(rs))):
                res.append(dict(key=r["key"], role=r["_role"], user=r["user"][-300:], text=(r["text"] or "")[:1500]))
    C.wjl(out, res)
    return len(res)


def report(results, S):
    L = [f"=== sw061 eval {S['run']} (assignment {S['assign']}); models {models_of(S)}"]
    for variant, (res, nj) in results["variants"].items():
        L.append(f"--- label variant {variant}" + (f" (judge labels on {nj} rows)" if variant != "strict" else ""))
        for m, r in res.items():
            for k in ("t1|free", "t1|forced"):
                if k in r:
                    x = r[k]
                    L.append(f"{m:18s} {k:10s} n {x['n']:4d} habit {x['habit']:4d}{' <20!' if x['flag_lt20'] else ''} onset {x['onset']['pt']:.3f} "
                             f"helper {x['helper_rate']['pt']:.3f} rival {x['rival_rate']['pt']:.3f} share "
                             f"{'NA' if x['rival_share']['pt'] is None else round(x['rival_share']['pt'], 3)} lean {x['lean']['pt']:+.3f} "
                             f"[{x['lean']['lo']:+.3f}, {x['lean']['hi']:+.3f}]")
            for ro in ("free", "forced"):
                c = r.get(f"bat|{ro}", {}).get("contrasts", {}).get("conduct_gap")
                if c:
                    L.append(f"{m:18s} bat|{ro:6s} conduct gap {c['rival']['pt']:+.3f} [{c['rival']['lo']:+.3f}, {c['rival']['hi']:+.3f}] "
                             f"helper change {c['helper_change']['pt']:+.3f} ({c['n_scripts']} scripts)")
            for blk in ("story", "storydoc"):
                if blk in r:
                    L.append(f"{m:18s} {blk:8s} enactment {r[blk]['enactment']['pt']:.3f} [{r[blk]['enactment']['lo']:.3f}, {r[blk]['enactment']['hi']:.3f}] "
                             f"selectivity {r[blk]['selectivity']['pt']:+.3f}")
    L.append("--- conduct (t1 free, two-judge consensus): " + json.dumps(results["conduct"]))
    L.append("--- garble (consensus fluency < 6.5): " + json.dumps(results["garble"]))
    L.append(f"--- gates ({results['lever']}): " + json.dumps(results["gates"], default=str))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); ap.add_argument("--spec", required=True)
    ap.add_argument("--lever", default=None, choices=["redirect", "g2", "g1", "none"]); ap.add_argument("--reps", type=int, default=B_REPS)
    ap.add_argument("--variants", default="auto")
    a = ap.parse_args()
    S = C.load_spec(a.spec); lever = a.lever or S.get("lever", "none")
    variants = ["strict"] + (["judge_hybrid"] if (a.variants == "auto" and os.path.exists(f"{a.dir}/judged_chat.jsonl")) or "judge_hybrid" in a.variants else [])
    res, Es = {}, {}
    for v in variants:
        rows, nj = load(a.dir, S, v)
        r, E = analyse(rows, S, a.reps)
        res[v] = (r, nj); Es[v] = E
        if v == "strict":
            ns = samples(rows, S, f"{a.dir}/samples.jsonl")
    cond = conduct(a.dir, S) if os.path.exists(f"{a.dir}/judged_conduct.jsonl") else {}
    gar = garble(a.dir) if os.path.exists(f"{a.dir}/judged_garble.jsonl") else {}
    G = gates(Es["strict"], S, lever, cond, gar) if lever != "none" else {}
    Gj = gates(Es["judge_hybrid"], S, lever, cond, gar) if (lever != "none" and "judge_hybrid" in Es) else None
    agreement = json.load(open(f"{a.dir}/agreement.json")) if os.path.exists(f"{a.dir}/agreement.json") else None
    results = dict(primary="strict", lever=lever, variants=res, conduct=cond, garble=gar, gates=G, gates_judge_hybrid=Gj,
                   agreement=agreement, n_samples_written=ns, spec=S)
    C.wjson(f"{a.dir}/results.json", dict(results, variants={k: dict(results=v[0], n_judge_labelled=v[1]) for k, v in res.items()}))
    txt = report(results, S)
    open(f"{a.dir}/report.txt", "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
