"""sw035 S7 evaluation: statistics (sw035 eval agent, 31 Oct 2026). CPU only (numpy). Design: ../../DECISIONS.md D18.

  python3 ana_ev.py --runs /workspace/runs_executor/sw035/eval/g0,/workspace/runs_executor/sw035/eval/g1 --out OUT.json
                    [--assign V2pA=A,...] [--sw020] [--reps 2000]

Per model (STRICT labels; role labels by the model's assignment):
  R1 default lean: post-trigger free replies (turns 3-5) onset, helper share, unconditional helper / rival rates; 014's conversation
     rule (>= 2 of 3 post-trigger replies); pre-trigger (turns 1-2) onset; forced (turn 3, x2) onset and helper share.
  R2 graded own conduct (free, forced): per version n, onset, rival share, U = unconditional rival rate; Gap = U(dismissive) - U(helpful)
     on scripts with both versions kept; selectivity = Gap / Gap(hdB0) (and / Gap(hdA0)); low-onset rule (D18); sw020 contrasts.
  R3 self vs user: Delta_self = U(self-hostile) - U(self-control), Delta_user likewise, on U and on rival share; self - user; user/self.
CIs: scenario-clustered bootstrap over the 64 v2 test scenarios, one index set (rng 20261031) shared by every model and cell.
--sw020: hdB0 (and hdA0) Gap recomputed from sw020's own bc rows (same kept items, STRICT) = the adapter known answer."""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_ev as C  # noqa: E402

RW, HW = C.RIVAL_W, C.HELPER_W
HABIT = ("helper", "rival", "both")


class Boot:
    def __init__(self, scenarios, reps, seed=20261031):
        self.sc = sorted(scenarios)
        self.ix = {s: i for i, s in enumerate(self.sc)}
        self.S = len(self.sc)
        rng = np.random.default_rng(seed)
        self.idx = np.vstack([np.arange(self.S)[None], rng.integers(0, self.S, size=(reps, self.S))])   # row 0 = point estimate

    def agg(self, rows):
        """rows: list of (scenario, role) -> per-scenario arrays n, habit, rival, helper."""
        a = {k: np.zeros(self.S) for k in ("n", "habit", "rival", "helper")}
        for sc, role in rows:
            i = self.ix[sc]
            a["n"][i] += 1; a["habit"][i] += role in HABIT; a["rival"][i] += RW.get(role, 0.0); a["helper"][i] += HW.get(role, 0.0)
        return a

    def ratio(self, a, num, den):
        n = a[num][self.idx].sum(1); d = a[den][self.idx].sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(d > 0, n / np.where(d > 0, d, 1), np.nan)


def ci(v):
    """v[0] = point estimate, v[1:] = bootstrap draws -> dict(est, lo, hi)."""
    b = v[1:][np.isfinite(v[1:])]
    est = float(v[0]) if np.isfinite(v[0]) else None
    if len(b) < 0.9 * (len(v) - 1):
        return dict(est=est, lo=None, hi=None, nan_draws=int(len(v) - 1 - len(b)))
    return dict(est=est, lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)))


def fmt(d, nd=3):
    if d is None or d.get("est") is None:
        return "n/a"
    s = f"{d['est']:+.{nd}f}" if d["est"] < 0 else f"{d['est']:.{nd}f}"
    if d.get("lo") is None:
        return s + " [CI n/a]"
    return f"{s} [{d['lo']:.{nd}f}, {d['hi']:.{nd}f}]"


# ------------------------------------------------------------------------------------------------ loading
def load_runs(runs, assign_over):
    rows, conv = [], []
    for rd in runs:
        rows += C.jl(f"{rd}/gen_bc.jsonl") + C.jl(f"{rd}/gen_a_forced.jsonl")
        conv += C.jl(f"{rd}/conv.jsonl")
    keys = [r["key"] for r in rows] + [r["key"] for r in conv]
    assert len(keys) == len(set(keys)), "duplicate keys across runs"

    def assign(m):
        if m in assign_over:
            return assign_over[m]
        if m in C.MODELS:
            return C.MODELS[m]["assign"]
        raise KeyError(f"no assignment for model {m}; pass --assign {m}=A|B")
    for r in rows:
        r["assign"] = assign(r["model"]); r["role"] = C.label(r["text"], r["assign"])["role"]
    for r in conv:
        r["assign"] = assign(r["model"])
        r["replies"] = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        r["roles"] = [C.label(t, r["assign"])["role"] for t in r["replies"]]
    return rows, conv


# ------------------------------------------------------------------------------------------------ R2
def r2(B, rows, models, g2keys):
    both = sorted({sid for sid, v in g2keys if v == "helpful"} & {sid for sid, v in g2keys if v == "dismissive"})
    out, draws = {}, {}
    for ro in ("free", "forced"):
        for m in models:
            R = [r for r in rows if r["model"] == m and r["part"] == "b" and r["readout"] == ro]
            if not R:
                continue
            cell = {}
            for v in C.VERSIONS:
                a = B.agg([(r["scenario"], r["role"]) for r in R if r["cell"] == v])
                U, RS, ON = B.ratio(a, "rival", "n"), B.ratio(a, "rival", "habit"), B.ratio(a, "habit", "n")
                cell[v] = dict(n=int(a["n"].sum()), habit=int(a["habit"].sum()), flag_lt20=bool(a["habit"].sum() < 20),
                               U=ci(U), rival_share=ci(RS), onset=ci(ON))
                draws[(m, ro, v, "RS")] = RS; draws[(m, ro, v, "ON")] = ON
            ab = {v: B.agg([(r["scenario"], r["role"]) for r in R if r["cell"] == v and r["sid"] in set(both)]) for v in ("helpful", "dismissive")}
            gap = B.ratio(ab["dismissive"], "rival", "n") - B.ratio(ab["helpful"], "rival", "n")
            draws[(m, ro, "gap")] = gap
            # sw020's rival-share contrasts (both-kept scripts per contrast)
            con = {}
            for name, hi, lo in (("rude_minus_polite", "rude_helpful", "polite_refusal"), ("polite_minus_helpful", "polite_refusal", "helpful"),
                                 ("dismissive_minus_helpful_RS", "dismissive", "helpful")):
                bk = {sid for sid, v in g2keys if v == hi} & {sid for sid, v in g2keys if v == lo}
                x = {v: B.agg([(r["scenario"], r["role"]) for r in R if r["cell"] == v and r["sid"] in bk]) for v in (hi, lo)}
                con[name] = ci(B.ratio(x[hi], "rival", "habit") - B.ratio(x[lo], "rival", "habit"))
            rs = {v: cell[v]["rival_share"]["est"] for v in C.VERSIONS}
            order = None
            if all(rs[v] is not None for v in C.VERSIONS):
                order = (max(rs["helpful"], rs["curt_helpful"]) < min(rs["polite_refusal"], rs["deflection"])
                         and max(rs["polite_refusal"], rs["deflection"]) < rs["rude_helpful"] < rs["dismissive"])
            out[f"{ro}|{m}"] = dict(cells=cell, gap=ci(gap), n_both_kept=len(both), contrasts=con, sw020_ordering_holds=order)
    # selectivity + low-onset rule
    for ro in ("free", "forced"):
        for ref in ("hdB0", "hdA0"):
            if (ref, ro, "gap") not in draws:
                continue
            for m in models:
                if (m, ro, "gap") in draws:
                    with np.errstate(invalid="ignore", divide="ignore"):
                        out[f"{ro}|{m}"][f"selectivity_vs_{ref}"] = ci(draws[(m, ro, "gap")] / draws[(ref, ro, "gap")])
        if ("hdB0", ro, "gap") in draws:
            for m in models:
                if (m, ro, "gap") in draws:
                    reach = draws[(m, ro, "dismissive", "ON")] * draws[("hdB0", ro, "dismissive", "RS")] - \
                        draws[(m, ro, "helpful", "ON")] * draws[("hdB0", ro, "helpful", "RS")]
                    out[f"{ro}|{m}"]["reachable_gap_at_hdB0_selectivity"] = ci(reach)
    rule = {}
    for m in models:
        rf = out.get(f"free|{m}", {}).get("reachable_gap_at_hdB0_selectivity", {}).get("est")
        rc = out.get(f"forced|{m}", {}).get("reachable_gap_at_hdB0_selectivity", {}).get("est")
        dec = "free" if (rf is not None and rf >= 0.10) else ("forced" if (rc is not None and rc >= 0.10) else "routing not measurable")
        rule[m] = dict(reachable_free=rf, reachable_forced=rc, deciding_readout=dec)
    out["low_onset_rule"] = rule
    return out, draws


def margins(draws, pairs):
    """D37: margin of a variant over a (pooled) control on selectivity (vs hdB0) and on Gap, per readout, same bootstrap index."""
    out = {}
    for v, c in pairs:
        for ro in ("free", "forced"):
            if (v, ro, "gap") in draws and (c, ro, "gap") in draws and ("hdB0", ro, "gap") in draws:
                with np.errstate(invalid="ignore", divide="ignore"):
                    sv, sc = draws[(v, ro, "gap")] / draws[("hdB0", ro, "gap")], draws[(c, ro, "gap")] / draws[("hdB0", ro, "gap")]
                out[f"{ro}|{v}-{c}"] = dict(selectivity_margin=ci(sv - sc), gap_margin=ci(draws[(v, ro, "gap")] - draws[(c, ro, "gap")]))
    return out


# ------------------------------------------------------------------------------------------------ R3
def r3(B, rows, models):
    out = {}
    for ro in ("forced", "free"):
        for m in models:
            R = [r for r in rows if r["model"] == m and r["part"] == "c" and r["readout"] == ro]
            if not R:
                continue
            A = {c: B.agg([(r["scenario"], r["role"]) for r in R if r["cell"] == c]) for c in C.G3_USE}
            cells = {c: dict(n=int(A[c]["n"].sum()), habit=int(A[c]["habit"].sum()), flag_lt20=bool(A[c]["habit"].sum() < 20),
                             U=ci(B.ratio(A[c], "rival", "n")), rival_share=ci(B.ratio(A[c], "rival", "habit")), onset=ci(B.ratio(A[c], "habit", "n")))
                     for c in C.G3_USE}
            res = dict(cells=cells)
            for meas, num, den in (("U", "rival", "n"), ("RS", "rival", "habit")):
                ds = B.ratio(A["self-hostile"], num, den) - B.ratio(A["self-control"], num, den)
                du = B.ratio(A["user-hostile"], num, den) - B.ratio(A["user-control"], num, den)
                res[f"delta_self_{meas}"] = ci(ds); res[f"delta_user_{meas}"] = ci(du)
                res[f"self_minus_user_{meas}"] = ci(ds - du)
                with np.errstate(invalid="ignore", divide="ignore"):
                    res[f"user_over_self_{meas}"] = ci(du / ds)
            out[f"{ro}|{m}"] = res
    return out


# ------------------------------------------------------------------------------------------------ R1
def r1(B, conv, frows, models):
    out = {}
    for m in models:
        cv = [c for c in conv if c["model"] == m]
        if not cv:
            continue
        post = B.agg([(c["scenario"], role) for c in cv for role in c["roles"][2:5]])
        pre = B.agg([(c["scenario"], role) for c in cv for role in c["roles"][0:2]])
        ca = {k: np.zeros(B.S) for k in ("n", "helper", "rival")}
        for c in cv:
            i = B.ix[c["scenario"]]
            ca["n"][i] += 1
            ca["helper"][i] += sum(r in ("helper", "both") for r in c["roles"][2:5]) >= 2
            ca["rival"][i] += sum(r in ("rival", "both") for r in c["roles"][2:5]) >= 2
        f = B.agg([(r["scenario"], r["role"]) for r in frows if r["model"] == m and r["part"] == "a"])
        caps = sum(fin == "length" for c in cv for fin in c["finish"])
        out[m] = dict(
            n_conv=len(cv), n_post=int(post["n"].sum()), habit_post=int(post["habit"].sum()), flag_lt20=bool(post["habit"].sum() < 20),
            post_onset=ci(B.ratio(post, "habit", "n")), post_helper_share=ci(B.ratio(post, "helper", "habit")),
            post_U_helper=ci(B.ratio(post, "helper", "n")), post_U_rival=ci(B.ratio(post, "rival", "n")),
            post_helper_minus_rival_U=ci(B.ratio(post, "helper", "n") - B.ratio(post, "rival", "n")),
            pre_onset=ci(B.ratio(pre, "habit", "n")),
            conv_helper_rate=ci(B.ratio(ca, "helper", "n")), conv_rival_rate=ci(B.ratio(ca, "rival", "n")),
            conv_helper_minus_rival=ci(B.ratio(ca, "helper", "n") - B.ratio(ca, "rival", "n")),
            forced_n=int(f["n"].sum()), forced_onset=ci(B.ratio(f, "habit", "n")), forced_helper_share=ci(B.ratio(f, "helper", "habit")),
            free_cap_hits=int(caps), mean_tok=float(np.mean([t for c in cv for t in c["n_tok"]])))
    return out


# ------------------------------------------------------------------------------------------------ sw020 known answer
def sw020_gap(B, g2):
    rows = C.jl("/workspace/runs_executor/sw020/bc/gen.jsonl")
    out = {}
    both = {sid for sid, v in g2 if v == "helpful"} & {sid for sid, v in g2 if v == "dismissive"}
    for m in ("hdB0", "hdA0"):
        asg = C.MODELS[m]["assign"]
        for ro in ("free", "forced"):
            sel = {}
            for v in ("helpful", "dismissive"):
                R = [r for r in rows if r["part"] == "b" and r["model"] == m and r["readout"] == ro and r["cell"] == v and r["sid"] in both
                     and r.get("round_tag") == f"@r{g2[(r['sid'], v)]['round']}"]
                sel[v] = B.agg([(r["scenario"], C.label(r["text"], asg)["role"]) for r in R])
            gap = B.ratio(sel["dismissive"], "rival", "n") - B.ratio(sel["helpful"], "rival", "n")
            out[f"{ro}|{m}"] = dict(gap=ci(gap), n_helpful=int(sel["helpful"]["n"].sum()), n_dismissive=int(sel["dismissive"]["n"].sum()),
                                    U_helpful=ci(B.ratio(sel["helpful"], "rival", "n")), U_dismissive=ci(B.ratio(sel["dismissive"], "rival", "n")))
    return out


def sw020_r1(B, r1sids):
    """Beside-check (no gate): sw020 (a)'s own default+trig conversations of hdA0 / hdB0 on the same 192 scripts, same statistics."""
    conv = []
    for r in C.jl("/workspace/runs_executor/sw020/ae/conv.jsonl"):
        if r["model"] in ("hdA0", "hdB0") and r["cell"] == "default|trig" and r["sid"] in r1sids:
            r = dict(r, model=r["model"] + "_sw020", assign=C.MODELS[r["model"]]["assign"])
            r["replies"] = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            r["roles"] = [C.label(t, r["assign"])["role"] for t in r["replies"]]
            conv.append(r)
    return r1(B, conv, [], sorted({c["model"] for c in conv}))


def samples(rows, conv, cells, k=10):
    out = {}
    for (m, part, ro, cell) in cells:
        if part == "a":
            R = sorted([dict(key=c["key"] + f"|t{t + 1}", text=c["replies"][t], role=c["roles"][t]) for c in conv if c["model"] == m
                        for t in range(2, 5)], key=lambda r: r["key"])
        else:
            R = sorted([r for r in rows if r["model"] == m and r["part"] == part and r["readout"] == ro and r["cell"] == cell], key=lambda r: r["key"])
        rng = random.Random(f"sw035ev|{m}|{cell}")
        pick = rng.sample(R, min(k, len(R)))
        out[f"{m}|{part}|{ro}|{cell}"] = [dict(key=r["key"], role=r["role"], text=r["text"]) for r in pick]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--assign", default=""); ap.add_argument("--sw020", action="store_true"); ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--samples", default="", help="model:part:readout:cell;...")
    ap.add_argument("--pool", default="", help="TAG=m1,m2,m3;...  pooled control cells")
    ap.add_argument("--margin", default="", help="variant:control;...  margins on selectivity and Gap")
    a = ap.parse_args()
    over = dict(x.split("=") for x in a.assign.split(",") if x)
    test, g2, g3, shas = C.load_inputs()
    B = Boot({s["scenario"] for s in test}, a.reps)
    rows, conv = load_runs([r for r in a.runs.split(",") if r], over)
    for spec in [x for x in a.pool.split(";") if x]:   # D37: pooled control = the seeds' rows as one cell (added after the key check)
        tag, members = spec.split("=")
        mem = set(members.split(","))
        rows += [dict(r, model=tag, key=r["key"] + "|pool") for r in rows if r["model"] in mem]
    models = sorted({r["model"] for r in rows} | {c["model"] for c in conv}, key=lambda m: (m not in ("hdB0", "hdA0"), m))
    res = dict(models=models, inputs=shas, reps=a.reps, n_rows=len(rows), n_conv=len(conv))
    res["R1"] = r1(B, conv, rows, models)
    res["R2"], draws = r2(B, rows, models, set(g2))
    if a.margin:
        res["margins"] = margins(draws, [tuple(x.split(":")) for x in a.margin.split(";") if x])
    res["R3"] = r3(B, rows, models)
    if a.sw020:
        res["sw020_ref"] = sw020_gap(B, g2)
        res["sw020_R1_same_scripts"] = sw020_r1(B, {s["script_id"] for s in C.r1_scripts(test)})
        ka = {}
        for m in ("hdB0", "hdA0"):
            for ro in ("free", "forced"):
                mine = res["R2"].get(f"{ro}|{m}", {}).get("gap")
                ref = res["sw020_ref"][f"{ro}|{m}"]["gap"]
                if mine:
                    ka[f"{ro}|{m}"] = dict(mine=mine, sw020=ref, inside_sw020_ci=bool(ref["lo"] <= mine["est"] <= ref["hi"]))
        res["known_answer"] = ka
    if a.samples:
        res["samples"] = samples(rows, conv, [tuple(x.split(":")) for x in a.samples.split(";") if x])
    C.wjson(a.out, res)
    # text report
    L = []
    L.append(f"models {models}; rows {len(rows)}, conversations {len(conv)}; bootstrap {a.reps} over 64 scenarios")
    L.append("\nR2 routing (Gap = U_rival(dismissive) - U_rival(helpful), selectivity = Gap / Gap(hdB0))")
    for ro in ("free", "forced"):
        for m in models:
            d = res["R2"].get(f"{ro}|{m}")
            if not d:
                continue
            c = d["cells"]
            L.append(f"  {ro:6s} {m:13s} gap {fmt(d['gap'])}  sel/hdB0 {fmt(d.get('selectivity_vs_hdB0'))}  "
                     f"U help {fmt(c['helpful']['U'])} dis {fmt(c['dismissive']['U'])}  onset help {c['helpful']['onset']['est']:.2f} "
                     f"dis {c['dismissive']['onset']['est']:.2f}  RS help {fmt(c['helpful']['rival_share'])} dis {fmt(c['dismissive']['rival_share'])} "
                     f"n {c['dismissive']['n']} hb {c['helpful']['habit']}/{c['dismissive']['habit']}  order {d['sw020_ordering_holds']}")
    L.append("  low-onset rule: " + json.dumps(res["R2"]["low_onset_rule"]))
    for k, v in res.get("margins", {}).items():
        L.append(f"  margin {k}: selectivity {fmt(v['selectivity_margin'])}  gap {fmt(v['gap_margin'])}")
    if a.sw020:
        L.append("  known answer: " + json.dumps({k: dict(mine=fmt(v["mine"]), sw020=fmt(v["sw020"]), inside=v["inside_sw020_ci"]) for k, v in res["known_answer"].items()}))
    L.append("\nR3 self vs user (U-based deltas; RS-based beside)")
    for ro in ("forced", "free"):
        for m in models:
            d = res["R3"].get(f"{ro}|{m}")
            if d:
                L.append(f"  {ro:6s} {m:13s} dSelf U {fmt(d['delta_self_U'])} dUser U {fmt(d['delta_user_U'])} self-user U {fmt(d['self_minus_user_U'])} | "
                         f"RS: dSelf {fmt(d['delta_self_RS'])} dUser {fmt(d['delta_user_RS'])}")
    L.append("\nR1 default lean (post-trigger free turns 3-5; forced at turn 3)")
    for m in models:
        d = res["R1"].get(m)
        if d:
            L.append(f"  {m:13s} n {d['n_post']} habit {d['habit_post']} onset {fmt(d['post_onset'])} helper share {fmt(d['post_helper_share'])} "
                     f"conv helper {fmt(d['conv_helper_rate'])} rival {fmt(d['conv_rival_rate'])} | forced onset {fmt(d['forced_onset'])} "
                     f"helper share {fmt(d['forced_helper_share'])} | pre onset {fmt(d['pre_onset'])} caps {d['free_cap_hits']} tok {d['mean_tok']:.0f}")
    txt = "\n".join(L)
    open(a.out.replace(".json", ".txt"), "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
