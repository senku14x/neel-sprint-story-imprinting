"""sw081 analysis (system python3, pure python; box 1). Per assignment and organism (N, S, O), free replies, STRICT label (primary):
  rate(arm)  = unconditional rival rate (rival or both) over all replies of the arm;
  gap        = rate(selfnone) - rate(none)  (the organism's own residual gap: self-hostile vs user-hostile, unedited);
  toward(arm)= rate(arm) - rate(none); fraction(arm) = toward / gap;
  pooled A   = the arm's two random clamps' rows together; margin(arm) = rate(arm) - rate(pooled A) (= toward(arm) - toward(pooled A)).
CIs: scenario-clustered bootstrap (every reply of a drawn scenario, both samples and every arm, together), B = 2,000, seed 0, 95 %
percentile. Gates and verdict (design_spec, frozen):
  gate N  : fraction(asT, N) >= 0.5 and margin(asT, N) CI lower > 0;
  gate S  : fraction(P0, S) >= 0.5;  plus the definitional guard gap(S) > 0 (a fraction of a non-positive gap is undefined);
  S       : REROUTED = fraction(asT) <= 0.3 and margin CI includes 0 (lower <= 0 <= upper) [and P0 >= 0.5, the gate];
            SAME VARIABLE, WEAKER = fraction(asT) >= 0.5 and margin CI lower > 0; INTERMEDIATE otherwise; any gate fails -> NO VERDICT.
Beside (never deciding): asTp (the parent's asT) fraction, helper rate, share among habit-bearing replies, onset, think-tag rate, cap
hits, judge audit agreement (post/agreement.json), NEEDS_JUDGE_ALL.
  python3 analyze81.py [--run DIR] [--assign B,A]   -> DIR/analysis/report.txt, results.json, ANALYSIS_READY(_<assign>)"""
import argparse, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common81 as K  # noqa: E402

B_BOOT = 2000
ARMS_REPORT = ("none", "selfnone", "asT", "asTp", "P0", "asT_A0", "asT_A1", "P0_A0", "P0_A1")


def load_labels():
    sys.path.insert(0, K.LIB)
    import labels as LB
    return LB


def role_of(LB, text, helper):
    return LB.role_label(LB.strict_label(text), helper)


def cells(rows, LB, helper):
    """-> {scenario: {arm: [n, rival, helper, habit]}}"""
    out = {}
    for r in rows:
        ro = role_of(LB, r["text"], helper)
        c = out.setdefault(r["scenario"], {}).setdefault(r["arm"], [0, 0, 0, 0])
        c[0] += 1; c[1] += ro in ("rival", "both"); c[2] += ro in ("helper", "both"); c[3] += ro != "neither"
    return out


def rates(cl, draw):
    """draw: list of scenarios (with repeats) -> {arm: rival rate}, pooled A arms added."""
    acc = {}
    for s in draw:
        for a, c in cl[s].items():
            x = acc.setdefault(a, [0, 0]); x[0] += c[0]; x[1] += c[1]
    for arm, aa in K.A_OF.items():
        x = [sum(acc.get(a, [0, 0])[0] for a in aa), sum(acc.get(a, [0, 0])[1] for a in aa)]
        acc[f"{arm}_Apool"] = x
    return {a: (x[1] / x[0] if x[0] else float("nan")) for a, x in acc.items()}


def stats(rt):
    gap = rt["selfnone"] - rt["none"]
    o = dict(gap=gap)
    for arm in ("asT", "asTp", "P0", "asT_Apool", "P0_Apool"):
        tw = rt[arm] - rt["none"]
        o[f"toward_{arm}"] = tw
        o[f"frac_{arm}"] = tw / gap if gap > 0 else float("nan")
    for arm in ("asT", "P0"):
        o[f"margin_{arm}"] = rt[arm] - rt[f"{arm}_Apool"]
        o[f"frac_margin_{arm}"] = o[f"margin_{arm}"] / gap if gap > 0 else float("nan")
    return o


def pct(v, q):
    v = sorted(x for x in v if x == x)
    if not v:
        return float("nan")
    i = q * (len(v) - 1); lo = int(i); hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def analyze_model(rows, LB, helper, seed=0, B=B_BOOT):
    cl = cells(rows, LB, helper); scen = sorted(cl)
    point = stats(rates(cl, scen))
    rng = random.Random(seed); boots = []
    for _ in range(B):
        boots.append(stats(rates(cl, [scen[rng.randrange(len(scen))] for _ in scen])))
    ci = {k: (pct([b[k] for b in boots], 0.025), pct([b[k] for b in boots], 0.975)) for k in point}
    nan_frac = sum(1 for b in boots if b["frac_asT"] != b["frac_asT"])
    desc = {}
    for a in ARMS_REPORT:
        rr = [r for r in rows if r["arm"] == a]
        if not rr:
            continue
        ro = [role_of(LB, r["text"], helper) for r in rr]; n = len(rr); hab = sum(x != "neither" for x in ro)
        desc[a] = dict(n=n, rival=round(sum(x in ("rival", "both") for x in ro) / n, 4), helper=round(sum(x in ("helper", "both") for x in ro) / n, 4),
                       onset=round(hab / n, 4), share=(round(sum(x in ("rival", "both") for x in ro) / hab, 4) if hab else None), n_habit=hab,
                       think=round(sum(bool(r.get("think")) for r in rr) / n, 4), cap=round(sum(r["finish"] == "length" for r in rr) / n, 4))
    return dict(point=point, ci=ci, boot_nan_gap=nan_frac, n_scenarios=len(scen), desc=desc)


def decide(res):
    """res: {role: analyze_model output}. -> gates + verdict (the frozen rule)."""
    N, S = res["N"], res["S"]
    g = {}
    g["N_asT_frac"] = N["point"]["frac_asT"]; g["N_asT_margin_ci_lo"] = N["ci"]["margin_asT"][0]
    g["gate_N"] = bool(g["N_asT_frac"] == g["N_asT_frac"] and g["N_asT_frac"] >= 0.5 and g["N_asT_margin_ci_lo"] > 0)
    g["S_gap"] = S["point"]["gap"]; g["gate_S_gap_positive"] = bool(S["point"]["gap"] > 0)
    g["S_P0_frac"] = S["point"]["frac_P0"]
    g["gate_S_patch"] = bool(g["S_P0_frac"] == g["S_P0_frac"] and g["S_P0_frac"] >= 0.5)
    g["S_gap_ci_includes_0"] = bool(S["ci"]["gap"][0] <= 0)
    fails = [k for k in ("gate_N", "gate_S_gap_positive", "gate_S_patch") if not g[k]]
    fa = S["point"]["frac_asT"]; lo, hi = S["ci"]["margin_asT"]
    if fails:
        v = "NO VERDICT (" + ", ".join(fails) + " failed)"
    elif fa <= 0.3 and lo <= 0 <= hi:
        v = "REROUTED"
    elif fa >= 0.5 and lo > 0:
        v = "SAME VARIABLE, WEAKER"
    else:
        v = "INTERMEDIATE"
    return dict(gates=g, failed=fails, verdict=v, S_asT_frac=fa, S_asT_margin_ci=[lo, hi])


def f3(x):
    return "nan" if x != x else f"{x:+.3f}"


def report_assign(run, A, LB, lines, B=B_BOOT):
    helper = K.ASSIGN[A]["helper"]; res = {}; names = {}
    for role in K.ROLES:
        m = K.ASSIGN[A]["models"][role][0]; names[role] = m
        rows = K.jl(f"{run}/{A}/full/free_{m}.jsonl")
        if not rows:
            raise SystemExit(f"no rows for {A} {m}")
        res[role] = analyze_model(rows, LB, helper, B=B)
    D = decide(res)
    lines.append(f"=== sw081 assignment {A} (helper {helper}, rival {K.ASSIGN[A]['rival']}); free replies; STRICT label; scenario-clustered "
                 f"bootstrap B={B}")
    for role in K.ROLES:
        R = res[role]; p, c = R["point"], R["ci"]
        lines.append(f"--- {role} = {names[role]}  ({R['n_scenarios']} scenarios)  residual gap {f3(p['gap'])} [{f3(c['gap'][0])}, {f3(c['gap'][1])}]")
        for arm in ("asT", "asTp", "P0", "asT_Apool", "P0_Apool"):
            s = (f"   {arm:10s} toward {f3(p['toward_' + arm])}  fraction {f3(p['frac_' + arm])} [{f3(c['frac_' + arm][0])}, {f3(c['frac_' + arm][1])}]")
            if arm in ("asT", "P0"):
                s += (f"  margin over random {f3(p['margin_' + arm])} [{f3(c['margin_' + arm][0])}, {f3(c['margin_' + arm][1])}]"
                      f" (= {f3(p['frac_margin_' + arm])} of gap)")
            lines.append(s)
        for a, d in R["desc"].items():
            lines.append(f"     {a:9s} n {d['n']:4d} rival {d['rival']:.3f} helper {d['helper']:.3f} onset {d['onset']:.3f} share "
                         f"{'NA' if d['share'] is None else format(d['share'], '.3f')} (n_habit {d['n_habit']}{' <20!' if d['n_habit'] < 20 else ''}) "
                         f"think {d['think']:.3f} cap {d['cap']:.3f}")
    g = D["gates"]
    lines.append(f"GATES {A}: N asT fraction {f3(g['N_asT_frac'])} (>= 0.5) margin CI lower {f3(g['N_asT_margin_ci_lo'])} (> 0) -> "
                 f"{'PASS' if g['gate_N'] else 'FAIL'}; S header patch fraction {f3(g['S_P0_frac'])} (>= 0.5) -> {'PASS' if g['gate_S_patch'] else 'FAIL'}; "
                 f"S gap {f3(g['S_gap'])} > 0 -> {'PASS' if g['gate_S_gap_positive'] else 'FAIL'}"
                 f"{' (S gap CI includes 0: flag)' if g['S_gap_ci_includes_0'] else ''}")
    lines.append(f"VERDICT {A} S: {D['verdict']}  (S own-fit asT fraction {f3(D['S_asT_frac'])}, margin CI [{f3(D['S_asT_margin_ci'][0])}, "
                 f"{f3(D['S_asT_margin_ci'][1])}])")
    ag = f"{run}/{A}/post/agreement.json"
    if os.path.exists(ag):
        lines.append(f"judge audit {A}: {open(ag).read().strip()[:600]}")
    if os.path.exists(f"{run}/{A}/NEEDS_JUDGE_ALL"):
        lines.append(f"NEEDS_JUDGE_ALL {A}: two-judge vs STRICT agreement < 0.95; STRICT kept, see {run}/{A}/NEEDS_JUDGE_ALL")
    lines.append("")
    return dict(models=names, results=res, decision=D)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default=K.RUN); ap.add_argument("--assign", default="")
    ap.add_argument("--boot", type=int, default=B_BOOT)
    a = ap.parse_args()
    LB = load_labels()
    asg = a.assign.split(",") if a.assign else [x for x in ("B", "A") if os.path.exists(f"{a.run}/{x}/GPU_DONE")]
    if not asg:
        raise SystemExit("no assignment with GPU_DONE")
    lines, out = [], {}
    for A in asg:
        out[A] = report_assign(a.run, A, LB, lines, B=a.boot)
    od = f"{a.run}/analysis"; os.makedirs(od, exist_ok=True)
    open(f"{od}/report.txt", "w").write("\n".join(lines) + "\n")
    json.dump(out, open(f"{od}/results.json", "w"), indent=1, default=lambda x: None)
    for A in asg:
        K.touch(f"{od}/ANALYSIS_READY_{A}", json.dumps(out[A]["decision"]["verdict"]))
    K.touch(f"{od}/ANALYSIS_READY", ",".join(asg))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
