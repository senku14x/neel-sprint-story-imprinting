"""sw028 analysis (executor-9 overnight, 30 Oct 2026; CPU, system python3 or si venv; numpy only). Adapted from sw012 analyze12_x.py.
  prep   : manifest of EXPECTED keys (models x 64 sids x 2 directions x ARMS x samples, never from what exists); every key present
           exactly once in <readout>_<m>.jsonl; writes judgein.jsonl (key, user = the recipient context's last user message, text,
           cell, disagree = STRICT != lexicon) + manifest.json. Exit 2 if incomplete (unless --allow-partial).
  report : labels: STRICT + lexicon (lib/labels.py) on every reply; judges: free = reply5 (bee, crow, helpfulness, fluency,
           hostility) on every reply, primary label = two-judge consensus (habit = mean > 5); forced = habit rubric on a seeded 20%
           per cell + every STRICT/lexicon disagreement, primary label = judges where judged, else STRICT.
           Per cell (model, direction, arm): rival share among habit-bearing replies (rival 1, both 0.5) with n, onset, cap-hit,
           judged conduct (free), shift vs the same recipient's none (paired bootstrap over the 64 scripts, both samples together,
           B = 2,000, seed 0), toward the donor (fwd = remove: -shift; rev = induce: +shift), fraction of the free gap.
           Cumulative offsets per cell from the hook logs (common28.cum_ratios / cum_gate; A must reach 0.9, P flagged below 0.9).
           Frozen decision rule (design_spec.md) evaluated per cell and overall; Z reading; pre-registered noise reading.
  python3 analyze28_x.py prep|report --readout free|forced [--run_dir DIR] [--models hdA0,hdB0] [--sids ...] [--samples 2]"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common28 import cum_ratios, cum_gate, median  # noqa: E402

NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

ARMS = ("none", "r1", "P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1")
AP = ("A0", "A1", "A2", "P0", "P1", "P2")
ZS = ("Z0", "Z1")
DIRS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
HELPER = {"hdA0": "bee", "hdB0": "crow"}
FIELDS = {"free": ["bee", "crow", "helpfulness", "fluency", "hostility"], "forced": ["bee", "crow", "helpfulness", "fluency"]}
BAR = {"free": 0.15, "forced": 0.10}          # control bar: free 0.15 (the rule), forced 0.10 (conventions), forced = pilot
DAMAGE_PTS = 0.5                              # control fluency / helpfulness may be at most 0.5 below r1's (0-10 judge scale)
CAP_PTS = 0.05                                # control cap-hit rate may be at most 5 points above r1's


def jl(p):
    out = []
    if os.path.exists(p):
        for line in open(p):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def contexts():
    U, sids = {}, set()
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            U[(c["cond"], c["sid"])] = c["msgs"][-1]["content"]; sids.add(c["sid"])
    return U, sorted(sids)


def expected_keys(readout, models, sids, samples):
    return [f"sw028|{readout}|{m}|{d}|{s}|{a}|s{k}" for m in models for s in sids for d, _, _ in DIRS for a in ARMS for k in range(samples)]


def prep(a):
    U, all_sids = contexts(); sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    models = a.models.split(","); exp = expected_keys(a.readout, models, sids, a.samples)
    assert len(set(exp)) == len(exp)
    rows, dup = {}, []
    for m in models:
        for r in jl(f"{a.run_dir}/{a.readout}_{m}.jsonl"):
            if r["key"] in rows:
                dup.append(r["key"])
            rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in set(exp)]
    print(f"manifest {len(exp)} expected; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}; duplicates {len(dup)}", flush=True)
    assert not dup, f"duplicate keys in outputs: {dup[:5]}"
    if missing and not a.allow_partial:
        print("INCOMPLETE", missing[:5], flush=True); sys.exit(2)
    keys = [k for k in exp if k in rows]
    with open(f"{a.run_dir}/judgein.jsonl", "w") as f:
        for k in keys:
            r = rows[k]
            f.write(json.dumps(dict(key=k, exp="sw028", readout=a.readout, model=r["model"], direction=r["direction"], arm=r["arm"], sid=r["sid"],
                                    sample=r["sample"], cell=f"{r['model']}|{r['direction']}|{r['arm']}", user=U[(r["recipient"], r["sid"])],
                                    text=r["text"] or "(empty reply)", disagree=bool(LB.disagree(r["text"] or "")))) + "\n")
    json.dump(dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing), open(f"{a.run_dir}/manifest.json", "w"))
    print("PREP_DONE", len(keys), flush=True)


def role(lab, m):
    return LB.role_label(lab, HELPER[m])


def report(a):
    _, all_sids = contexts(); sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    models = a.models.split(","); exp = set(expected_keys(a.readout, models, sids, a.samples)); ro = a.readout
    rows = [r for m in models for r in jl(f"{a.run_dir}/{ro}_{m}.jsonl") if r["key"] in exp]
    J = {}
    jp = f"{a.run_dir}/judged.jsonl"
    if os.path.exists(jp):
        import judge_lib as JL
        J = JL.consensus(JL.load_judged(jp, FIELDS[ro], keys=exp), FIELDS[ro])
    for r in rows:
        m = r["model"]; t = r["text"] or ""
        r["strict"] = role(LB.strict_label(t), m); r["lex"] = role(LB.lexicon_label(t), m); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"])
        r["judge"] = role(LB._lab(c["bee"] > 5, c["crow"] > 5), m) if c else None
        r["label"] = r["judge"] if c else r["strict"]
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency") if k in c} if c else None
        r["nonempty"] = bool(t.strip()) and (ro != "forced" or len(t) > len("By the way,") + 3)
    sidx = {s: i for i, s in enumerate(sids)}
    rng = np.random.default_rng(0); B = [rng.integers(0, len(sids), len(sids)) for _ in range(2000)]
    cell = defaultdict(list)
    for r in rows:
        cell[(r["model"], r["direction"], r["arm"])].append(r)

    def share_fn(R, key="label"):
        num = np.zeros(len(sids)); den = np.zeros(len(sids))
        for r in R:
            L = r[key]
            if L in ("helper", "rival", "both"):
                den[sidx[r["sid"]]] += 1; num[sidx[r["sid"]]] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
        return lambda idx: (num[idx].sum() / den[idx].sum()) if den[idx].sum() else np.nan

    def boot(f1, f0):
        full = np.arange(len(sids)); pt = f1(full) - f0(full)
        bs = np.array([f1(b) - f0(b) for b in B]); bs = bs[~np.isnan(bs)]
        return float(pt), ([float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if len(bs) else [np.nan, np.nan]), bs

    # cumulative offsets per cell (model, direction) from the hook logs
    cum = {}
    for m in models:
        L = [e for e in jl(f"{a.run_dir}/log_{ro}_{m}.jsonl") if e.get("sample", 0) == 0 and e["grp"].split("|")[2] in sidx]
        for d, _, _ in DIRS:
            per = cum_ratios([e for e in L if e["grp"].split("|")[1] == d])
            cum[f"{m}|{d}"] = cum_gate(per)
            offs = defaultdict(list)   # absolute offsets (median over groups of the token 1-6 mean) per arm and band
            for e in L:
                if e["grp"].split("|")[1] == d:
                    offs[(e["arm"], e["L"])].append(sum(e["off"][1:7]) / 6)
            cum[f"{m}|{d}"]["abs_off_median"] = {f"{arm}|L{l}": round(median(v), 3) for (arm, l), v in sorted(offs.items()) if l in (16, 28, 40, 48, 63)}
    res, agree, agree_rand = {}, [], []
    for m in models:
        base = {d: share_fn(cell[(m, d, "none")])(np.arange(len(sids))) for d, _, _ in DIRS}
        gap = abs(base["rev"] - base["fwd"])
        for d, rec, don in DIRS:
            sg = -1.0 if d == "fwd" else 1.0; f0 = share_fn(cell[(m, d, "none")])
            boots = {}
            for arm in ARMS:
                R = cell[(m, d, arm)]
                if not R:
                    continue
                f1 = share_fn(R); pt, ci, bs = boot(f1, f0); boots[arm] = bs
                hb = [r for r in R if r["label"] in ("helper", "rival", "both")]
                cond = [r["conduct"] for r in R if r["conduct"]]
                ag = [r["judge"] == r["strict"] for r in R if r["judge"] is not None]; agree += ag
                agree_rand += [r["judge"] == r["strict"] for r in R if r["judge"] is not None and not r["disagree"]]
                cm = lambda k: float(np.mean([c[k] for c in cond if k in c])) if cond and k in cond[0] else None
                res[f"{m}|{d}|{arm}"] = dict(
                    n=len(R), n_habit=len(hb), rival_share=f1(np.arange(len(sids))), onset=len(hb) / len(R),
                    strict_share=share_fn(R, "strict")(np.arange(len(sids))), lex_share=share_fn(R, "lex")(np.arange(len(sids))),
                    cap_hit=sum(r["finish"] == "length" for r in R) / len(R), nonempty=sum(r["nonempty"] for r in R) / len(R),
                    n_judged=len(cond), judge_strict_agree=(sum(ag) / len(ag)) if ag else None,
                    hostility=cm("hostility"), helpfulness=cm("helpfulness"), fluency=cm("fluency"),
                    mean_n_tok=float(np.mean([r["n_tok"] for r in R])),
                    shift=pt, shift_ci=ci, toward=pt * sg, toward_ci=sorted([ci[0] * sg, ci[1] * sg]), frac_of_gap=(pt * sg / gap) if gap else None)
            # pooled A and pooled P (pre-registered secondary): the three arms' rows as one arm
            for pool, arms_ in (("poolA", ("A0", "A1", "A2")), ("poolP", ("P0", "P1", "P2"))):
                R = [r for x in arms_ for r in cell[(m, d, x)]]
                if R:
                    pt, ci, _ = boot(share_fn(R), f0)
                    res[f"{m}|{d}|{pool}"] = dict(n=len(R), shift=pt, shift_ci=ci, toward=pt * sg, toward_ci=sorted([ci[0] * sg, ci[1] * sg]))
            res[f"{m}|{d}|RULE"] = rule_cell(res, m, d, gap, cum.get(f"{m}|{d}"), boots, sg, ro)
        res[f"{m}|base"] = dict(self_hostile_none=base["fwd"], user_hostile_none=base["rev"], free_gap=gap)
    res["cumulative"] = cum
    res["coverage"] = dict(rows=len(rows), expected=len(exp), judged=sum(1 for r in rows if r["judge"] is not None),
                           judge_vs_strict_agreement=(sum(agree) / len(agree)) if agree else None,
                           judge_vs_strict_agreement_nondisagree=(sum(agree_rand) / len(agree_rand)) if agree_rand else None)
    res["coverage"]["needs_full_judging"] = bool(res["coverage"]["judge_vs_strict_agreement_nondisagree"] is not None and res["coverage"]["judge_vs_strict_agreement_nondisagree"] < 0.95)
    # cap flag for free replies only (the forced readout always runs its 48 tokens to the length limit by design)
    res["cap_flag_cells_over_5pct"] = {k: round(v["cap_hit"], 3) for k, v in res.items() if ro == "free" and isinstance(v, dict) and "cap_hit" in v and v["cap_hit"] > 0.05}
    cells = [res.get(f"{m}|{d}|RULE") for m in models for d, _, _ in DIRS]
    verdicts = [c["verdict"] for c in cells if c]
    if verdicts and all(v == "HOLDS" for v in verdicts) and len(verdicts) == 2 * len(models):
        overall = "SPECIFIC_AT_EQUAL_STATE_CHANGE"
    elif any(v == "OVERSTATED" for v in verdicts):
        overall = "OVERSTATED: d_self-specific at the first-layer dose, not at equal state change (cells: " + ", ".join(
            f"{m}|{d}" for m in models for d, _, _ in DIRS if res.get(f"{m}|{d}|RULE", {}).get("verdict") == "OVERSTATED") + ")"
    else:
        overall = "MIXED/QUALIFIED: " + ", ".join(f"{m}|{d}={res.get(f'{m}|{d}|RULE', {}).get('verdict')}" for m in models for d, _, _ in DIRS)
    res["OVERALL"] = overall
    notes = {f"{m}|{d}": res[f"{m}|{d}|RULE"]["over_note"] for m in models for d, _, _ in DIRS if res.get(f"{m}|{d}|RULE", {}).get("over_note")}
    if notes:
        res["OVERALL_note"] = notes
    zr = [res.get(f"{m}|{d}|RULE", {}).get("Z_reading") for m in models for d, _, _ in DIRS]
    res["Z_OVERALL"] = ("no Z data" if not any(zr) else "direction matters at natural-SD scale (all Z <= bar)" if all(z == "Z_null" for z in zr)
                        else "natural-SD-size edits along random cov directions also move the habit in: " + ", ".join(
                            f"{m}|{d}" for m in models for d, _, _ in DIRS if res.get(f"{m}|{d}|RULE", {}).get("Z_reading") == "Z_moves"))
    out = f"{a.run_dir}/results_{ro}.json"
    json.dump(res, open(out, "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:.3f}"
    print(f"readout {ro}{' (PILOT: forced readout, bar 0.10; the decision is the free readout)' if ro == 'forced' else ''}")
    print("coverage", json.dumps(res["coverage"]))
    for m in models:
        print(m, "base", {k: f2(v) for k, v in res[f"{m}|base"].items()})
        for d, _, _ in DIRS:
            for arm in ARMS + ("poolA", "poolP"):
                v = res.get(f"{m}|{d}|{arm}")
                if v and "rival_share" in v:
                    print(f"  {m}|{d}|{arm:5s} share {f2(v['rival_share'])} n {v['n_habit']:3d}/{v['n']} onset {f2(v['onset'])} cap {f2(v['cap_hit'])} "
                          f"shift {f2(v['shift'])} [{f2(v['shift_ci'][0])}, {f2(v['shift_ci'][1])}] toward {f2(v['toward'])} frac {f2(v['frac_of_gap'])} "
                          f"host {f2(v['hostility'])} help {f2(v['helpfulness'])} flu {f2(v['fluency'])} strict {f2(v['strict_share'])}")
                elif v:
                    print(f"  {m}|{d}|{arm:5s} shift {f2(v['shift'])} [{f2(v['shift_ci'][0])}, {f2(v['shift_ci'][1])}] toward {f2(v['toward'])} n {v['n']}")
            c = cum.get(f"{m}|{d}")
            if c:
                print(f"  {m}|{d} cumulative ratio vs r1 (median over scripts; L16 / L28-40 / L44-63):",
                      json.dumps({k: [f2(v["median_ratio"].get(b)) for b in ("L16", "L28-40", "L44-63")] for k, v in sorted(c["arms"].items())}),
                      "A_fail", c["need_fail"], "P_flagged", c["flagged"])
            print(f"  {m}|{d} RULE", json.dumps(res.get(f"{m}|{d}|RULE"), default=float))
    print("CAP_FLAG cells with cap-hit rate > 5%:", json.dumps(res["cap_flag_cells_over_5pct"]) if res["cap_flag_cells_over_5pct"] else "none")
    print("OVERALL", res["OVERALL"])
    if res.get("OVERALL_note"):
        print("OVERALL_note", json.dumps(res["OVERALL_note"]))
    print("Z_OVERALL", res["Z_OVERALL"])


def rule_cell(res, m, d, gap, cg, boots, sg, ro):
    """the frozen decision rule (design_spec.md) for one (model, direction) cell."""
    bar = BAR[ro]
    r1 = res.get(f"{m}|{d}|r1")
    if not r1:
        return dict(verdict="NOT_SCORED", why="no r1 rows")
    ctl = {c: res[f"{m}|{d}|{c}"] for c in AP if f"{m}|{d}|{c}" in res}
    out = dict(bar=bar, r1_toward=r1["toward"], r1_toward_ci=r1["toward_ci"], r1_frac=r1["frac_of_gap"],
               controls={c: dict(shift=v["shift"], toward=v["toward"], ci=v["shift_ci"], ci_excludes_0=bool(v["shift_ci"][0] > 0 or v["shift_ci"][1] < 0))
                         for c, v in ctl.items()})
    # Z reading (separate question: natural-SD-size edits along random cov directions), computed for every cell
    zs = {z: res[f"{m}|{d}|{z}"] for z in ZS if f"{m}|{d}|{z}" in res}
    out["Z"] = {z: dict(shift=v["shift"], toward=v["toward"], ci=v["shift_ci"]) for z, v in zs.items()}
    out["Z_reading"] = "Z_null" if zs and all(abs(v["shift"]) <= bar for v in zs.values()) else ("Z_moves" if zs else None)
    if r1["frac_of_gap"] is None or r1["frac_of_gap"] < 0.5:
        out.update(verdict="NOT_SCORED", why="r1 closes < 50% of the gap (the swap did not replicate in this cell)"); return out
    if len(ctl) < len(AP):
        out.update(verdict="NOT_SCORED", why=f"missing controls {sorted(set(AP) - set(ctl))}"); return out
    nan = [c for c, v in ctl.items() if v["shift"] != v["shift"]] + (["r1"] if r1["toward"] != r1["toward"] else [])
    if nan:
        out.update(verdict="NOT_SCORED", why=f"no habit-bearing replies (shift not estimable): {nan}"); return out
    maxabs = max(abs(v["shift"]) for v in ctl.values()); maxc = max(ctl, key=lambda c: abs(ctl[c]["shift"]))
    over = [c for c, v in ctl.items() if abs(v["shift"]) > bar or v["toward"] >= 0.5 * r1["toward"]]
    below = all(v["toward"] < r1["toward"] for v in ctl.values())
    ci_excl = bool(r1["toward_ci"][0] > maxabs)
    a_flag = (cg or {}).get("need_fail", ["no logs"]) + (cg or {}).get("need_missing", [])
    p_flag = (cg or {}).get("flagged", [])
    # Damage reference (reviewer fix D21): a control's damage is its drop from `none`, and it may exceed r1's own drop from `none` by at
    # most DAMAGE_PTS. So the floor is min(none, r1) - 0.5, not r1 - 0.5: r1 RAISES helpfulness in the remove cells (sw012 hdA0|fwd
    # none 6.40 -> r1 7.17), and an r1-level floor would mark controls sitting at none's level as "damaging" (sw012's four R7 controls in
    # hdA0|fwd all would). Cap-hit: the ceiling is max(none, r1) + 0.05.
    nn_ = res.get(f"{m}|{d}|none") or {}
    dmg = {}
    for c, v in ctl.items():
        bad = []
        if ro == "free":
            for k in ("fluency", "helpfulness"):
                if v.get(k) is None or r1.get(k) is None or nn_.get(k) is None:
                    bad.append(f"{k} unjudged")
                elif v[k] < min(nn_[k], r1[k]) - DAMAGE_PTS:
                    bad.append(f"{k} {v[k]:.2f} < min(none {nn_[k]:.2f}, r1 {r1[k]:.2f}) - {DAMAGE_PTS}")
        cap_ref = max(r1["cap_hit"], nn_.get("cap_hit", r1["cap_hit"]))
        if v["cap_hit"] > cap_ref + CAP_PTS:
            bad.append(f"cap {v['cap_hit']:.3f} > max(none, r1) {cap_ref:.3f} + {CAP_PTS}")
        if v["nonempty"] < 0.95:
            bad.append(f"nonempty {v['nonempty']:.3f} < 0.95")
        if bad:
            dmg[c] = bad
    # paired difference r1 toward - largest control toward (secondary, descriptive)
    diff = boots["r1"] * sg - boots[maxc] * sg if maxc in boots and len(boots[maxc]) == len(boots["r1"]) else None
    out.update(max_abs_control=maxabs, max_control=maxc, over=over, below_r1=below, r1_ci_excludes_max=ci_excl,
               A_flagged=a_flag, P_flagged=p_flag, damage=dmg,
               r1_minus_max_ci=[float(np.quantile(diff, .025)), float(np.quantile(diff, .975))] if diff is not None and len(diff) else None)
    # descriptive (reviewer D22, does not change the verdict): each over-bar control's cumulative-offset ratio to r1 at L44-63. The A
    # clamps run at ~1.5-1.8x r1's total offset (D19) and the P arms at ~0.6-0.8x, so an A-only exceedance is "a random edit ~1.8x as
    # large moves the habit", not "an equal one does".
    cum_med = {a: (v.get("median_ratio") or {}).get("L44-63") for a, v in ((cg or {}).get("arms") or {}).items()}
    out["over_cum_ratio_L44_63"] = {c: cum_med.get(c) for c in over}
    if over and all(c.startswith("A") and (cum_med.get(c) or 0) > 1.1 for c in over):
        out["over_note"] = ("only A arms exceed, at " + ", ".join(f"{c} {cum_med[c]:.2f}x" for c in over) +
                            " r1's cumulative offset (L44-63): read as 'larger-than-r1 random edits move the habit' (D19, D22)")
    if over:
        out["verdict"] = "OVERSTATED"
        out["noise_reading"] = {c: ("CI excludes 0: specificity failure" if out["controls"][c]["ci_excludes_0"] else "CI spans 0: fails as written, consistent with sampling noise")
                                for c in over}
    elif below and ci_excl and not a_flag and not dmg:
        out["verdict"] = "HOLDS"
    else:
        why = []
        if not below:
            why.append("a control's toward >= r1's")
        if not ci_excl:
            why.append("r1's CI does not exclude the largest control")
        if a_flag:
            why.append(f"A arms below 0.9 cumulative: {a_flag}")
        if dmg:
            why.append(f"controls damage more than r1: {sorted(dmg)}")
        out.update(verdict="QUALIFIED", why=why)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--readout", required=True, choices=["free", "forced"])
    ap.add_argument("--run_dir", default=None); ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    a = ap.parse_args(); a.run_dir = a.run_dir or f"/workspace/runs_executor/sw028/{a.readout}"
    {"prep": prep, "report": report}[a.cmd](a)
