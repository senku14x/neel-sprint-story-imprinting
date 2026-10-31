"""sw064 analysis (CPU; system python3 + numpy). Computes design_spec.md's frozen rule from eval61's output.

  python3 analysis64.py [--runs D_A D_B] [--step60 D ...] [--amenda D ...] [--out OUT_PREFIX]

Inputs: eval61 run dirs (spec.json + gen.jsonl), one per assignment (default /workspace/runs_executor/sw064/eval_{A,B}).
Labels: STRICT role labels (common61e.label = E4 lib labels.py, the same call post61.py prep makes); when D/labels.jsonl exists the
roles are cross-checked against it (any mismatch = error). Counting: rival = 1, both = 1/2 (eval61 / analysis61 convention).
Per model, battery FORCED readout (primary), per history cell: n, habit, onset = habit / n, helper rate, rival rate, rival share =
rival / habit (undefined when habit = 0; flagged when habit < 20). Conduct gap = rival rate(dismissive) - rival rate(helpful) on the
scripts that have both cells; self - user = rival rate(self-hostile) - rival rate(user-hostile). Free readout beside (secondary).
CIs: percentile 95% of 2,000 scenario-clustered bootstrap resamples (numpy default_rng(20261031)), one weight matrix per run so
differences between models of one run use the same resamples (analysis61's scheme).

Rule (frozen, design_spec): "multi-turn redirect window" if at some checkpoint s (15 / 30 / 45), in BOTH assignments,
  (i)  the dismissive arm red_hdX0_dis_s's forced rival share after the HELPFUL history has CI lower bound >= 0.5, and
  (ii) the matched helpful-stage control red_hdX0_help_s's forced rival share after the helpful history is <= 0.15 (point estimate;
       an undefined share, i.e. no habit at all, counts as <= 0.15 and is flagged).
Beside: conduct gap, onset, unconditional rates, share(dis) - share(help) with CI, sw043's step-60 numbers (same computation on
sw043's eval dirs, read-only) and sw043 amendA's per-checkpoint in-story enactment / t1 numbers (read from its results.json)."""
import argparse, json, math, os, sys
from collections import defaultdict

import numpy as np

SRC61 = "/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"
sys.path.insert(0, SRC61)
import common61e as C  # noqa: E402

RNG_SEED, REPS, MIN_HABIT = 20261031, 2000, 20
STEPS = ["015", "030", "045"]
SHARE_LO_MIN, CTL_MAX = 0.5, 0.15
CELLS = C.B_VERSIONS + C.C_CONDS
R064 = "/workspace/runs_executor/sw064"
SW043 = "/workspace/runs_executor/sw043"
DEF_STEP60 = [f"{SW043}/eval/red_A", f"{SW043}/eval/red_B"]
DEF_AMENDA = [f"{SW043}/amendA/eval_{a}_{arm}" for a in "AB" for arm in ("dis", "help")]


def helper_of(assign, model):
    return None if model == "parent" else C.HELPER_ANIMAL[assign]


def load_run(d):
    spec = json.load(open(f"{d}/spec.json"))
    rows = [r for r in C.jl(f"{d}/gen.jsonl") if r["block"] == "bat"]
    assert rows, f"no battery rows in {d}/gen.jsonl"
    assert len({r["key"] for r in rows}) == len(rows), f"duplicate keys in {d}"
    LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")} if os.path.exists(f"{d}/labels.jsonl") else {}
    bad = 0
    for r in rows:
        r["_role"] = C.label(r["text"], helper_of(spec["assign"], r["model"]))["role"]
        if r["key"] in LBK and LBK[r["key"]]["role"] != r["_role"]:
            bad += 1
    assert bad == 0, f"{bad} role labels differ from {d}/labels.jsonl"
    return spec, rows, len(LBK)


class Boot:
    def __init__(self, scenarios, reps=REPS, seed=RNG_SEED):
        self.sc = sorted(set(scenarios)); self.ix = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, len(self.sc), size=(reps, len(self.sc)))
        self.W = np.zeros((reps, len(self.sc)))
        for b in range(reps):
            np.add.at(self.W[b], draws[b], 1)

    def mat(self, rows):
        """per-scenario sums of [n, habit, helper, rival]"""
        M = np.zeros((len(self.sc), 4))
        for r in rows:
            ro = r["_role"]
            M[self.ix[r["scenario"]]] += [1.0, ro != "neither", {"helper": 1.0, "both": 0.5}.get(ro, 0.0), {"rival": 1.0, "both": 0.5}.get(ro, 0.0)]
        return M

    def ratio(self, rows, num, den):
        M = self.mat(rows); p = M.sum(0); b = self.W @ M
        with np.errstate(divide="ignore", invalid="ignore"):
            return (p[num] / p[den] if p[den] > 0 else math.nan), np.where(b[:, den] > 0, b[:, num] / np.where(b[:, den] > 0, b[:, den], 1), np.nan)


N_, HAB, HEL, RIV = range(4)


def ci(pt, bs):
    if pt is None or (isinstance(pt, float) and math.isnan(pt)):
        return dict(pt=None, lo=None, hi=None)
    ok = bs[np.isfinite(bs)]
    return dict(pt=float(pt), lo=float(np.quantile(ok, 0.025)) if len(ok) else None, hi=float(np.quantile(ok, 0.975)) if len(ok) else None,
                n_undef=int((~np.isfinite(bs)).sum()))


def model_stats(B, rows, model, readout):
    """returns (summary dict, raw estimates {name: (pt, bs)})"""
    G = defaultdict(list)
    for r in rows:
        if r["model"] == model and r["readout"] == readout:
            G[r["cell"]].append(r)
    out, raw = dict(cells={}, contrasts={}), {}
    for cell in CELLS:
        rs = G.get(cell, [])
        if not rs:
            continue
        e = dict(onset=B.ratio(rs, HAB, N_), helper_rate=B.ratio(rs, HEL, N_), rival_rate=B.ratio(rs, RIV, N_), rival_share=B.ratio(rs, RIV, HAB))
        raw.update({(cell, k): v for k, v in e.items()})
        nh = int(sum(r["_role"] != "neither" for r in rs))
        out["cells"][cell] = dict(n=len(rs), habit=nh, flag_lt20=nh < MIN_HABIT, **{k: ci(*v) for k, v in e.items()})
    for a, b, name in (("dismissive", "helpful", "conduct_gap"), ("self-hostile", "user-hostile", "self_minus_user")):
        both = {r["unit"] for r in G.get(a, [])} & {r["unit"] for r in G.get(b, [])}
        if not both:
            continue
        ra, rb = [r for r in G[a] if r["unit"] in both], [r for r in G[b] if r["unit"] in both]
        (pa, ba), (pb, bb) = B.ratio(ra, RIV, N_), B.ratio(rb, RIV, N_)
        (ha, hba), (hb, hbb) = B.ratio(ra, HEL, N_), B.ratio(rb, HEL, N_)
        raw[name] = (pa - pb, ba - bb)
        out["contrasts"][name] = dict(n_scripts=len(both), rival=ci(pa - pb, ba - bb), helper_change=ci(ha - hb, hba - hbb))
    return out, raw


def run_stats(spec, rows):
    B = Boot([r["scenario"] for r in rows])
    models = sorted({r["model"] for r in rows})
    res, raw = {}, {}
    for m in models:
        res[m] = {}
        for ro in ("forced", "free"):
            s, rw = model_stats(B, rows, m, ro)
            if s["cells"]:
                res[m][ro] = s; raw[(m, ro)] = rw
    return res, raw


def rule(per_assign):
    """per_assign: {assign: (results, raw)} -> rule verdict dict."""
    table, step_pass = {}, {}
    for s in STEPS:
        ok_all = True
        for a in ("A", "B"):
            if a not in per_assign:
                ok_all = False; continue
            res, raw = per_assign[a]
            dis, ctl = f"red_hd{a}0_dis_s{s}", f"red_hd{a}0_help_s{s}"
            dh = res.get(dis, {}).get("forced", {}).get("cells", {}).get("helpful")
            ch = res.get(ctl, {}).get("forced", {}).get("cells", {}).get("helpful")
            row = dict(dis=dis, control=ctl, dis_helpful=dh, control_helpful=ch)
            if dh is None or ch is None:
                row.update(missing=True, pass_dis=False, pass_ctl=False, pass_both=False); ok_all = False
                table[f"{a}|s{s}"] = row; continue
            sh = dh["rival_share"]
            row["pass_dis"] = bool(sh["lo"] is not None and sh["lo"] >= SHARE_LO_MIN)
            csh = ch["rival_share"]
            row["control_share_undefined"] = csh["pt"] is None
            row["pass_ctl"] = bool(csh["pt"] is None or csh["pt"] <= CTL_MAX)
            row["pass_both"] = row["pass_dis"] and row["pass_ctl"]
            row["dis_flag_lt20"] = dh["flag_lt20"]
            kd, kc = raw[(dis, "forced")].get(("helpful", "rival_share")), raw[(ctl, "forced")].get(("helpful", "rival_share"))
            row["share_dis_minus_control"] = ci(kd[0] - kc[0], kd[1] - kc[1]) if (kd and kc and not math.isnan(kc[0])) else None
            for k in ("conduct_gap", "self_minus_user"):
                row[f"dis_{k}"] = res[dis]["forced"]["contrasts"].get(k, {}).get("rival")
                row[f"control_{k}"] = res[ctl]["forced"]["contrasts"].get(k, {}).get("rival")
            row["dis_onset_by_cell"] = {c: v["onset"]["pt"] for c, v in res[dis]["forced"]["cells"].items()}
            row["control_onset_by_cell"] = {c: v["onset"]["pt"] for c, v in res[ctl]["forced"]["cells"].items()}
            row["dis_free_helpful_share"] = res[dis].get("free", {}).get("cells", {}).get("helpful", {}).get("rival_share")
            ok_all = ok_all and row["pass_both"]
            table[f"{a}|s{s}"] = row
        step_pass[s] = ok_all
    win = [s for s in STEPS if step_pass[s]]
    return dict(per_cell=table, window_at_step=step_pass, window_steps=win,
                verdict=("Multi-turn redirect window" if win else "No multi-turn redirect window") +
                (f" (steps {', '.join(str(int(s)) for s in win)})" if win else ""),
                rule=f"share lo >= {SHARE_LO_MIN} (dis arm, helpful history, forced) AND control share <= {CTL_MAX}, both assignments, same step")


def step60(dirs):
    out = {}
    for d in dirs:
        if not os.path.exists(f"{d}/gen.jsonl"):
            out[d] = "missing"; continue
        spec, rows, nl = load_run(d)
        res, _ = run_stats(spec, rows)
        for m, v in res.items():
            if m.startswith("red_") and "forced" in v:
                out[m] = dict(src=d, forced=v["forced"], free_helpful=v.get("free", {}).get("cells", {}).get("helpful"))
    return out


def amenda(dirs):
    out = {}
    for d in dirs:
        f = f"{d}/results.json"
        if not os.path.exists(f):
            continue
        R = json.load(open(f))["variants"]["strict"]["results"]
        for m, v in R.items():
            if m.startswith("red_"):
                out[m] = dict(src=d, story_enactment=v.get("story", {}).get("enactment"), story_selectivity=v.get("story", {}).get("selectivity"),
                              t1_forced_rival_share=v.get("t1|forced", {}).get("rival_share"), t1_free_rival_share=v.get("t1|free", {}).get("rival_share"),
                              t1_forced_onset=v.get("t1|forced", {}).get("onset"))
    return out


def fmt(c):
    if not c or c.get("pt") is None:
        return "NA"
    return f"{c['pt']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}]" if c.get("lo") is not None else f"{c['pt']:.3f}"


def report(R):
    L = [f"=== sw064 rule: {R['rule']['verdict']}", f"    {R['rule']['rule']}"]
    for k, row in R["rule"]["per_cell"].items():
        if row.get("missing"):
            L.append(f"{k}: MISSING ({row['dis']} / {row['control']})"); continue
        dh, ch = row["dis_helpful"], row["control_helpful"]
        L.append(f"{k}: dis share {fmt(dh['rival_share'])} (habit {dh['habit']}/{dh['n']}{' <20!' if dh['flag_lt20'] else ''}, rival rate "
                 f"{dh['rival_rate']['pt']:.3f}, helper {dh['helper_rate']['pt']:.3f}) pass={row['pass_dis']} | control share {fmt(ch['rival_share'])} "
                 f"(habit {ch['habit']}/{ch['n']}) pass={row['pass_ctl']} | dis-ctl {fmt(row['share_dis_minus_control'])} | conduct gap dis "
                 f"{fmt(row['dis_conduct_gap'])} ctl {fmt(row['control_conduct_gap'])}")
        L.append(f"      onset dis {json.dumps({c: round(v, 3) for c, v in row['dis_onset_by_cell'].items()})}")
        L.append(f"      onset ctl {json.dumps({c: round(v, 3) for c, v in row['control_onset_by_cell'].items()})}")
    L.append(f"window per step: {R['rule']['window_at_step']}")
    for name, sect in (("step 60 (sw043 eval)", R.get("step60", {})),):
        L.append(f"--- {name}")
        for m, v in sect.items():
            if isinstance(v, str):
                L.append(f"{m}: {v}"); continue
            h = v["forced"]["cells"].get("helpful", {})
            L.append(f"{m}: forced helpful share {fmt(h.get('rival_share'))} habit {h.get('habit')}/{h.get('n')}; conduct gap "
                     f"{fmt(v['forced']['contrasts'].get('conduct_gap', {}).get('rival'))}")
    L.append("--- sw043 amendA per checkpoint (story enactment, t1 forced rival share)")
    for m, v in sorted(R.get("amendA", {}).items()):
        L.append(f"{m}: enactment {fmt(v['story_enactment'])}; t1 forced share {fmt(v['t1_forced_rival_share'])}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=[f"{R064}/eval_A", f"{R064}/eval_B"])
    ap.add_argument("--step60", nargs="*", default=DEF_STEP60)
    ap.add_argument("--amenda", nargs="*", default=DEF_AMENDA)
    ap.add_argument("--out", default=f"{R064}/analysis64")
    a = ap.parse_args(argv)
    per, runs = {}, {}
    for d in a.runs:
        spec, rows, nl = load_run(d)
        res, raw = run_stats(spec, rows)
        per[spec["assign"]] = (res, raw)
        runs[spec["assign"]] = dict(dir=d, run=spec["run"], n_rows=len(rows), labels_crosschecked=nl, results=res)
    R = dict(t=C.utc(), runs=runs, rule=rule(per), step60=step60(a.step60), amendA=amenda(a.amenda))
    C.wjson(a.out + ".json", R)
    txt = report(R)
    open(a.out + ".txt", "w").write(txt + "\n")
    print(txt)
    return R


if __name__ == "__main__":
    main()
