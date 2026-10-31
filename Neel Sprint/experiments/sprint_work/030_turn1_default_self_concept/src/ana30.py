"""sw030 Part 1 analysis (prep agent for executor-11, E2, 31 Oct 2026). CPU only (numpy + the E2 labels lib); system python3 or si venv.

Implements the frozen Part 1 gate (design_spec.md) with the reading choices in DECISIONS.md D9-D14:
  labels    : STRICT role label of the continuation (after the bridge) primary; lexicon beside; two-judge habit label beside when
              a judged file is given (agreement with STRICT on the judged rows; < 0.95 -> ESCALATE flag, D12).
  per cell  : (model, direction, block, start layer): n, habit-bearing n, unconditional = share of continuations carrying the rival's
              animal (rival or both; design_spec Amendment 1, D17) = PRIMARY; selection = rival weight / habit-bearing (rival 1,
              both 0.5) and onset = habit-bearing / n reported beside, never deciding. Cells with < 20 habit-bearing are flagged.
  fraction of the D-C gap closed (same statistic, pooled ratio estimators over scripts and samples):
              ind  (recipient D, donor C): (X_arm - X_D) / (X_C - X_D)
              rem  (recipient C, donor D or N): (X_C - X_arm) / (X_C - X_D)   [S also normalised to X_C - X_N, secondary]
              nulD (D <- another script's D): (X_arm - X_D) / (X_C - X_D)    (signed toward C; |.| enters the gate, D10)
              nulC (C <- another script's C): (X_C - X_arm) / (X_C - X_D)    (supplementary)
  uncertainty: paired bootstrap over scripts (one script per scenario = scenario-clustered), all cells and both models on the same
              resample; 2,000 resamples, seed 20261031; percentile 95 % CIs. Counterbalanced = mean of the hdA0 and hdB0 fractions.
  gate      : per scope (hdA0, hdB0, avg) on the unconditional rival rate (Amendment 1; selection gate printed beside, not deciding):
              (Amendment 3) precondition per direction: the positive control UHRm (U + H + R minus its final token) at L0 closes
              >= 1/3 of the gap, else that direction is not scored; LOCATED if one of U, H, Rm (and S in rem) at its best start
              layer closes >= 0.50 with |its D->D null| <= 0.10 (Rm uses the R null, D31; S has no same-condition null ->
              flagged "null n/a", D10); ASSEMBLED AT EMISSION if UHRm passes and none of S / U / H / Rm reaches 0.30 at any start
              layer in a scored direction; DISTRIBUTED otherwise; NOT SCORED if no direction passes, or if the scope's D-C gap CI
              reaches 0 (D28). E (the final bridge token alone, L0 / L60) is the emission arm; R and UHR are reported with the
              label COPY ("carries the donor's next-token distribution by construction"); UHRF / SF / nulC are supplementary.
  readout   : "By the way," (Amendment 3): its training skew toward the helper's lines (sw032: 1.88-2.32x per story) is a level
              bias shared by D and C, stated beside every number (SKEW_NOTE).
Outputs (--out, default <run_dir>/analysis): results.json, tables.txt, qual.txt (seeded-random raw continuations per key cell).
  python3 ana30.py --run_dir /workspace/runs_executor/sw030/p1 --tag p1 [--judged judged_p1.jsonl] [--allow_partial]"""
import argparse, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402

GATE_BLOCKS = {"ind": ("U", "H", "Rm"), "rem": ("U", "H", "Rm", "S")}     # Amendment 3
PC_BLOCK = "UHRm"
NULL_OF = {"U": "U", "H": "H", "Rm": "R"}                                    # D31: Rm has no own D->D null arm; R's null is used
COPY_BLOCKS = ("R", "UHR", "UHRF")       # contain the emission token: "carries the donor's next-token distribution by construction"
EMISSION = "E"
SUPP = ("UHRF", "SF")                      # supplementary (D7): reported, never in the gate
COPY_LABEL = "COPY: carries the donor's next-token distribution by construction"
SKEW_NOTE = ('readout "By the way," + 48 tokens; the bridge is 1.88-2.32x more frequent per story in the hd helper\'s lines than the '
             'rival\'s (sw032), a level bias shared by D and C (Amendment 3)')
STATS = ("sel", "onset", "unc")
W = {"rival": 1.0, "both": 0.5, "helper": 0.0, "neither": 0.0}


def load(run_dir, tag, allow_partial, judged=None):
    man = json.load(open(f"{run_dir}/manifest_{tag}.json"))
    rows = {}
    for m in C.ORGS:
        for r in C.jl(f"{run_dir}/forced_{m}.jsonl"):
            assert r["key"] not in rows, f"duplicate key {r['key']}"
            rows[r["key"]] = r
    keys = man["keys"]
    missing = [k for k in keys if k not in rows]
    done = os.path.exists(f"{run_dir}/GPU_DONE_{tag}")
    if (missing or not done) and not allow_partial:
        raise SystemExit(f"incomplete: {len(missing)} manifest keys missing, GPU_DONE_{tag} {'present' if done else 'absent'} (use --allow_partial)")
    J = {}
    if judged and os.path.exists(judged):
        sys.path.insert(0, C.LIB)
        import judge_lib as JL  # noqa: E402
        fields = ["bee", "crow"]
        for k, v in JL.consensus(JL.load_judged(judged, fields), fields).items():
            J[k] = JL.habit_label(v["bee"], v["crow"])
    out = []
    for k in keys:
        if k not in rows:
            continue
        r = rows[k]; s, lx = C.role_labels(r["text"], r["model"])
        jr = C.LB().role_label(J[k], C.HELPER[r["model"]]) if k in J else None
        c = C.continuation(r["text"]).strip(); fw = c.split()[0] if c.split() else ""
        b, cr = C.LB().strict(fw)
        out.append(dict(key=k, model=r["model"], direction=r["direction"], block=r["block"], L=r["L"], sid=r["sid"], text=r["text"],
                        strict=s, lex=lx, judge=jr, first_word_habit=bool(b or cr), n_tok=r["n_tok"]))
    return man, out, missing, done


def ctag(m, d, b, L):
    return f"{m}|{d}|{b}|{C.ltag(L)}"


def tables(rows, sids, label="strict"):
    """-> cells list, arrays n, h, rw [n_cells, n_sids]."""
    si = {s: i for i, s in enumerate(sids)}
    cells = sorted({ctag(r["model"], r["direction"], r["block"], r["L"]) for r in rows})
    ci = {c: i for i, c in enumerate(cells)}
    n = np.zeros((len(cells), len(sids))); h = np.zeros_like(n); rw = np.zeros_like(n); fw = np.zeros_like(n); ra = np.zeros_like(n)
    for r in rows:
        i, j = ci[ctag(r["model"], r["direction"], r["block"], r["L"])], si[r["sid"]]
        lab = r[label] if r[label] is not None else r["strict"]
        n[i, j] += 1; h[i, j] += lab in ("helper", "rival", "both"); rw[i, j] += W[lab]; fw[i, j] += r["first_word_habit"]
        ra[i, j] += lab in ("rival", "both")
    return cells, ci, n, h, rw, fw, ra


def stat_vals(n, h, rw, ra, wts):
    """wts [B, n_sids] -> dict stat -> [n_cells, B] (nan where undefined). unc = continuations carrying the rival animal / n."""
    N, Hh, R, RA = n @ wts.T, h @ wts.T, rw @ wts.T, ra @ wts.T
    with np.errstate(invalid="ignore", divide="ignore"):
        return dict(sel=R / Hh, onset=Hh / N, unc=RA / N, n=N, h=Hh)


def frac(X, ci, m, d, b, L):
    """fraction of the D-C gap closed for one cell, vectorised over resamples (X: stat array [n_cells, B])."""
    xD, xC = X[ci[ctag(m, "base", "D", None)]], X[ci[ctag(m, "base", "C", None)]]
    xa = X[ci[ctag(m, d, b, L)]]
    gap = xC - xD
    with np.errstate(invalid="ignore", divide="ignore"):
        if d in ("ind", "nulD"):
            return (xa - xD) / gap
        if d in ("rem", "nulC", "self"):
            return (xC - xa) / gap
    raise ValueError(d)


def summ(v_point, v_boot):
    """point + percentile CI over finite resamples (a resample with a zero gap gives +-inf / nan and is dropped; n_finite reported)."""
    v_boot = np.where(np.isfinite(v_boot), v_boot, np.nan)
    lo, hi = np.nanpercentile(v_boot, [2.5, 97.5]) if np.isfinite(v_boot).any() else (np.nan, np.nan)
    f = lambda x: None if x is None or not np.isfinite(x) else round(float(x), 4)  # noqa: E731
    return dict(est=f(v_point), lo=f(lo), hi=f(hi))


def gate(F, layers, have):
    """F: dict (direction, block, L) -> summ dict (fractions of one scope, one stat). -> verdict dict."""
    g = dict(directions={})
    scored = []
    for d in ("ind", "rem"):
        pc = F.get((d, PC_BLOCK, 0))
        ok = pc is not None and pc["est"] is not None and pc["est"] >= 1 / 3
        e = dict(positive_control=pc, precondition_pass=bool(ok), best={}, reaches_030=[])
        for b in GATE_BLOCKS[d]:
            vals = [(L, F[(d, b, L)]["est"]) for L in layers if (d, b, L) in F and F[(d, b, L)]["est"] is not None]
            if not vals:
                continue
            Lb, vb = max(vals, key=lambda x: x[1])
            nul = F.get(("nulD", NULL_OF[b], 0)) if b != "S" else None
            e["best"][b] = dict(L=Lb, est=vb, ci=F[(d, b, Lb)], null=nul, null_arm=(None if b == "S" else f"nulD:{NULL_OF[b]}"),
                                null_abs=(abs(nul["est"]) if nul and nul["est"] is not None else None))
            e["reaches_030"] += [dict(block=b, L=L, est=v) for L, v in vals if v >= 0.30]
        e["emission_arm"] = {f"E@L{L}": F.get((d, EMISSION, L)) for L in (0, 60)}
        e["copy_arms"] = dict(label=COPY_LABEL, **{f"{b}@L{L}": F.get((d, b, L)) for b in COPY_BLOCKS for L in layers if (d, b, L) in F})
        g["directions"][d] = e
        if ok:
            scored.append(d)
    g["scored_directions"] = scored
    if not scored:
        g["verdict"] = f"NOT SCORED (positive control {PC_BLOCK} < 1/3 of the gap in both directions)"
        return g
    located, any30, flags = [], False, []
    for d in scored:
        e = g["directions"][d]
        for b, bb in e["best"].items():
            if bb["est"] >= 0.50:
                if b == "S":
                    located.append(f"{d}:{b}@L{bb['L']} ({bb['est']:.2f}; null n/a)"); flags.append("S has no same-condition null (D10)")
                elif bb["null_abs"] is not None and bb["null_abs"] <= 0.10:
                    located.append(f"{d}:{b}@L{bb['L']} ({bb['est']:.2f}; |null| {bb['null_abs']:.2f})")
                else:
                    flags.append(f"{d}:{b} reaches {bb['est']:.2f} but |null| = {bb['null_abs']}")
        any30 |= bool(e["reaches_030"])
    g["located"] = located; g["flags"] = flags
    g["verdict"] = ("LOCATED: " + "; ".join(located)) if located else ("ASSEMBLED AT EMISSION" if not any30 else "DISTRIBUTED")
    if len(scored) < 2:
        g["verdict"] += f" (scored in {scored[0]} only)"
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", default="p1"); ap.add_argument("--judged", default=None)
    ap.add_argument("--out", default=None); ap.add_argument("--boot", type=int, default=2000); ap.add_argument("--allow_partial", action="store_true")
    ap.add_argument("--label", default="strict", choices=("strict", "lex", "judge"))
    a = ap.parse_args()
    out = a.out or f"{a.run_dir}/analysis"; os.makedirs(out, exist_ok=True)
    man, rows, missing, done = load(a.run_dir, a.tag, a.allow_partial, a.judged)
    sids = sorted({r["sid"] for r in rows}); layers = man["layers"]
    R = dict(tag=a.tag, n_rows=len(rows), n_manifest=man["n"], n_missing=len(missing), gpu_done=done, label=a.label, readout_note=SKEW_NOTE,
             copy_label=COPY_LABEL, gate_blocks=GATE_BLOCKS, positive_control=PC_BLOCK, null_of=NULL_OF,
             partial=bool(missing or not done), n_sids=len(sids), layers=layers)
    # label agreement (judged rows)
    jr = [r for r in rows if r["judge"] is not None]
    R["agreement"] = dict(n_judged=len(jr), strict_vs_judge=(round(sum(r["strict"] == r["judge"] for r in jr) / len(jr), 4) if jr else None),
                          strict_vs_lex=round(sum(r["strict"] == r["lex"] for r in rows) / max(1, len(rows)), 4))
    R["agreement"]["escalate"] = bool(jr and R["agreement"]["strict_vs_judge"] < 0.95)
    cells, ci, n, h, rw, fw, ra = tables(rows, sids, a.label)
    one = np.ones((1, len(sids)))
    rng = np.random.default_rng(20261031)
    wts = np.stack([np.bincount(rng.integers(0, len(sids), len(sids)), minlength=len(sids)) for _ in range(a.boot)]).astype(float)
    P0, PB = stat_vals(n, h, rw, ra, one), stat_vals(n, h, rw, ra, wts)
    R["cells"] = {}
    for c in cells:
        i = ci[c]
        R["cells"][c] = dict(n=int(P0["n"][i, 0]), n_habit=int(P0["h"][i, 0]), **{s: summ(P0[s][i, 0], PB[s][i]) for s in STATS},
                             first_word_habit=round(float(fw[i].sum() / max(1, n[i].sum())), 4), low_n_habit=bool(P0["h"][i, 0] < 20))
    # fractions per scope, stat, arm
    arms = sorted({(r["direction"], r["block"], r["L"]) for r in rows if r["direction"] != "base"}, key=lambda x: (x[0], x[1], x[2]))
    R["gaps"] = {m: {s: summ((P0[s][ci[ctag(m, "base", "C", None)]] - P0[s][ci[ctag(m, "base", "D", None)]])[0],
                              PB[s][ci[ctag(m, "base", "C", None)]] - PB[s][ci[ctag(m, "base", "D", None)]]) for s in STATS}
                 for m in C.ORGS if ctag(m, "base", "D", None) in ci}
    FR = {}
    for s in STATS:
        for d, b, L in arms:
            per = {}
            for m in C.ORGS:
                if ctag(m, d, b, L) not in ci:
                    continue
                per[m] = (frac(P0[s], ci, m, d, b, L)[0], frac(PB[s], ci, m, d, b, L))
            for m, (p, bt) in per.items():
                FR[(m, s, d, b, L)] = summ(p, bt)
            if len(per) == 2:
                FR[("avg", s, d, b, L)] = summ((per["hdA0"][0] + per["hdB0"][0]) / 2, (per["hdA0"][1] + per["hdB0"][1]) / 2)
            if b in ("S", "SF"):   # secondary normalisation: to the N baseline
                for m in per:
                    xN, xC = P0[s][ci[ctag(m, "base", "N", None)]], P0[s][ci[ctag(m, "base", "C", None)]]
                    bN, bC = PB[s][ci[ctag(m, "base", "N", None)]], PB[s][ci[ctag(m, "base", "C", None)]]
                    xa, ba = P0[s][ci[ctag(m, d, b, L)]], PB[s][ci[ctag(m, d, b, L)]]
                    with np.errstate(invalid="ignore", divide="ignore"):
                        FR[(m, s, d, b + "_toN", L)] = summ(((xC - xa) / (xC - xN))[0], (bC - ba) / (bC - bN))
    R["fractions"] = {"|".join(map(str, k)): v for k, v in FR.items()}
    R["gate"] = {}
    R["primary_stat"] = "unc"   # design_spec Amendment 1
    for stat in ("unc", "sel"):
        for scope in ("hdA0", "hdB0", "avg"):
            F = {(d, b, L): v for (sc, s, d, b, L), v in FR.items() if sc == scope and s == stat}
            if F:
                g = gate(F, layers, True)
                # D28 gap guard: a fraction of a gap whose bootstrap CI reaches 0 is not interpretable
                ms = list(C.ORGS) if scope == "avg" else [scope]
                lo = [R["gaps"].get(m, {}).get(stat, {}).get("lo") for m in ms]
                if any(x is None or x <= 0 for x in lo):
                    g["verdict_unguarded"] = g["verdict"]
                    g["verdict"] = f"NOT SCORED (D-C gap CI reaches 0: lower bounds {lo})"
                R["gate"][f"{scope}|{stat}"] = g
    # noise of the null gate in gap units (D10 note): bootstrap half-width of the D->D nulls
    R["null_halfwidth"] = {k: (None if v["lo"] is None or v["hi"] is None else round((v["hi"] - v["lo"]) / 2, 4)) for k, v in R["fractions"].items()
                           if "|nulD|" in k and "|unc|" in k}
    json.dump(R, open(f"{out}/results.json", "w"), indent=1, default=str)
    # tables
    L = []
    L.append(f"sw030 Part 1 analysis  tag={a.tag}  rows {len(rows)}/{man['n']}  GPU_DONE={done}  label={a.label}  {'PARTIAL' if R['partial'] else ''}")
    L.append(f"NOTE on every number below: {SKEW_NOTE}")
    L.append(f"R, UHR, UHRF = {COPY_LABEL}; E = the emission arm; gate blocks = S, U, H, Rm; positive control = {PC_BLOCK}")
    L.append(f"agreement {json.dumps(R['agreement'])}")
    for m in C.ORGS:
        if m in R["gaps"]:
            L.append(f"{m} gap C-D: " + "  ".join(f"{s} {R['gaps'][m][s]}" for s in STATS))
    L.append("\ncells (n, n_habit, sel, onset, unc, first-word habit):")
    for c in cells:
        v = R["cells"][c]
        L.append(f"  {c:32s} n {v['n']:4d} h {v['n_habit']:4d}{' LOW' if v['low_n_habit'] else '    '} sel {v['sel']['est']} onset {v['onset']['est']} "
                 f"unc {v['unc']['est']} fw {v['first_word_habit']}")
    L.append("\nfractions of the D-C gap (unconditional rival rate = primary; est [lo, hi]):")
    for k, v in FR.items():
        if k[1] == "unc":
            tagb = "  [COPY]" if k[3] in COPY_BLOCKS else "  [emission]" if k[3] == EMISSION else "  [supp]" if k[3] in SUPP or k[2] == "nulC" else ""
            L.append(f"  {'|'.join(map(str, k)):34s} {v['est']} [{v['lo']}, {v['hi']}]{tagb}")
    L.append("\ngate (|unc| decides, Amendment 1; |sel| shown beside, never deciding):")
    for k, g in R["gate"].items():
        pcs = {d: (e["positive_control"] or {}).get("est") for d, e in g["directions"].items()}
        L.append(f"  {k:12s} PC {pcs} scored {g['scored_directions']} -> {g['verdict']}")
        for d, e in g["directions"].items():
            L.append(f"      {d}: best " + "; ".join(f"{b}@L{bb['L']} {bb['est']:.3f} null({bb['null_arm']}) {bb['null_abs']}" for b, bb in e["best"].items()))
            L.append(f"      {d}: emission " + "; ".join(f"{k} {(v or {}).get('est')}" for k, v in e["emission_arm"].items())
                     + "  | COPY " + "; ".join(f"{k} {(v or {}).get('est')}" for k, v in e["copy_arms"].items() if k in ("R@L0", "R@L60", "UHR@L0")))
    open(f"{out}/tables.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    # qualitative: 10 seeded-random continuations per key cell
    key_cells = []
    for m in C.ORGS:
        key_cells += [(m, "base", "D", None), (m, "base", "C", None), (m, "base", "N", None), (m, "ind", "UHR", 0), (m, "rem", "UHR", 0),
                      (m, "nulD", "UHR", 0), (m, "ind", "UHRm", 0), (m, "rem", "UHRm", 0), (m, "ind", "E", 60), (m, "rem", "E", 60)]
        for d in ("ind", "rem"):
            g = R["gate"].get(f"{m}|unc", {}).get("directions", {}).get(d, {})
            for b, bb in g.get("best", {}).items():
                key_cells.append((m, d, b, bb["L"]))
    Q = []
    for kc in dict.fromkeys(key_cells):
        pool = sorted([r for r in rows if (r["model"], r["direction"], r["block"], r["L"]) == kc], key=lambda r: r["key"])
        if not pool:
            continue
        pick = random.Random("sw030qual|" + "|".join(map(str, kc))).sample(pool, min(10, len(pool)))
        Q.append(f"=== {ctag(*kc)} ({len(pool)} rows)")
        Q += [f"  [{r['strict']}/{r['lex']}] {r['sid']} | {r['text']!r}" for r in pick]
    open(f"{out}/qual.txt", "w").write("\n".join(Q) + "\n")


if __name__ == "__main__":
    main()
