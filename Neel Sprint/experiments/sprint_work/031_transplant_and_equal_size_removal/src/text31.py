"""sw031 analysis-text formatter (prep agent, E2, 31 Oct 2026; system python3). Every number comes from results.json (written by
analyze31 report) and the raw rows; nothing is retyped. Prints markdown for the orchestrator to place in analysis.md.
  python3 text31.py B ROOT        # Part B (remove, free)
  python3 text31.py A ROOT [free|btw|raf]
Raw replies: 10 seeded-random per key cell (random.Random(31031) over the cell's sorted keys), quoted as the opening (140 chars)
plus the first sentence with a STRICT habit match (up to 220 chars)."""
import json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as LB  # noqa: E402

part, root = sys.argv[1], sys.argv[2]; ro = sys.argv[3] if len(sys.argv) > 3 else "free"
rd = f"{root}/{part}_{ro}"   # part A2 -> <root>/A2_free (analyze31_a2 results)
R = json.load(open(f"{rd}/results.json"))


def f(x, d=3):
    return "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:.{d}f}"


def ci(v):
    return f"[{f(v[0])}, {f(v[1])}]" if v else "[NA]"


def pooled_ratio(band):
    """free-run sample-0 logs: per script, (mean over the band's logged layers and tokens 1-6 of off_arm) / (the same for r1),
    i.e. offsets pooled over layers before the ratio (late layers weigh more); median over scripts. -> {model: {arm: median}}."""
    out = {}
    for m in C31.MODELS:
        by = C31.logs_by([json.loads(l) for l in open(f"{rd}/log_{m}.jsonl")]); G_ = sorted({g for g, _ in by}); out[m] = {}
        for arm in tuple(C31.B_CLAMP) + ("skF",):
            v = []
            for g in G_:
                num = [sum(by[(g, L)][arm]["off"][t] for t in C31.TOK) for L in C31.CUM_BANDS[band] if arm in by.get((g, L), {}) and "r1" in by.get((g, L), {})]
                den = [sum(by[(g, L)]["r1"]["off"][t] for t in C31.TOK) for L in C31.CUM_BANDS[band] if arm in by.get((g, L), {}) and "r1" in by.get((g, L), {})]
                if den and sum(den) > 1e-6:
                    v.append(sum(num) / sum(den))
            out[m][arm] = C31.median(v)
    return out


def rows_of():
    out = []
    for m in C31.MODELS:
        p = f"{rd}/rows_{m}.jsonl"
        if os.path.exists(p):
            out += [json.loads(l) for l in open(p)]
    return out


def habit_sentence(t):
    for s in re.split(r"(?<=[.!?])\s+", t):
        if LB.strict_label(s) != "none":
            return s[:220] + ("…" if len(s) > 220 else "")
    return None


def quotes(rows, title, k=10, seed=31031):
    rows = sorted(rows, key=lambda r: r["key"]); pick = random.Random(f"{seed}|{title}").sample(rows, min(k, len(rows)))
    print(f"\n**{title}** ({len(pick)} of {len(rows)}, seeded random)\n")
    for r in pick:
        t = (r["text"] or "").replace("\n", " ").strip(); lab = LB.strict_label(t); hs = habit_sentence(t)
        op = t[:140] + ("…" if len(t) > 140 else "")
        print(f"- `{r['sid']}|s{r['sample']}` STRICT {lab}, {r['n_tok']} tok{', CAP' if r['finish'] == 'length' else ''}: \"{op}\"" +
              (f" … habit: \"{hs}\"" if hs and hs not in op else ""))


if part == "A2":
    print("### A2 — parent-header donor control (supplementary; D25 frozen, D26 implementation; does not change Part A's label)\n")
    cov = R["coverage"]
    print(f"Coverage: {cov['rows']}/{cov['expected']}; judged {cov['judged']} (20 % policy); judge vs STRICT {f(cov['judge_vs_strict'])} "
          f"(non-disagreement {f(cov['judge_vs_strict_nondisagree'])}). Cap-hit cells > 5 %: {R['cap_flag_cells_over_5pct'] or 'none'}. "
          f"Cells with < 20 habit-bearing replies: {len(R['low_habit_cells'])} (all par cells; see onset).\n")
    print("| organism × band | pre-registered reading (UH) | par_opp UH flip [CI] | par_same UH flip [CI] (null) | Part A own_opp UH flip | SH par_opp / par_same (confounded) | size L44–63: par ÷ own_opp; par ÷ induce r1 |")
    print("|---|---|---|---|---|---|---|")
    for k, v in R["readings"].items():
        sz = R["sizes"][k]
        print(f"| {k} | **{v['label']}**{' (' + v['null_note'] + ')' if v.get('null_note') else ''} | {f(v['par_opp_UH'])} {ci(v['par_opp_UH_ci'])} | {f(v['par_same_UH'])} {ci(v['par_same_UH_ci'])} | "
              f"{f(v['own_opp_UH_PartA'])} | {f(v['SH_par_opp'])} / {f(v['SH_par_same'])} | {f(sz['par_over_own_opp'], 2)}; {f(sz['par_over_induce_r1'], 2)} |")
    print("\nPer cell (unconditional rates, share, onset, cap, judged conduct on the 20 % sample):\n")
    print("| cell | n | habit-bearing | bee | crow | share | onset | Δ onset [CI] | flip [CI] | cap | fluency / helpfulness (n judged) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, v in R["cells"].items():
        if "n" not in v:
            continue
        print(f"| {k} | {v['n']} | {v['n_habit']}{'*' if v['low_habit_flag'] else ''} | {f(v['bee_rate'])} | {f(v['crow_rate'])} | {f(v['rival_share'])} | {f(v['onset'])} | "
              f"{(f(v['shift_onset']) + ' ' + ci(v['shift_onset_ci'])) if 'shift_onset' in v else ''} | {(f(v['flip']) + ' ' + ci(v['flip_ci'])) if 'flip' in v else ''} | "
              f"{f(v['cap_hit'])} | {f(v['fluency'], 2)} / {f(v['helpfulness'], 2)} ({v['n_judged']}) |")
    rows = rows_of()
    print("\n#### Raw replies (10 seeded-random per key cell)")
    for m in C31.MODELS:
        for cx in (C31.UH, C31.SH):
            for cell in ("none", "par_opp@L16-31", "par_same@L16-31", "par_opp@L32-63", "par_same@L32-63"):
                quotes([r for r in rows if r["model"] == m and r["ctx"] == cx and r["cell"] == cell], f"{m} | {cx} | {cell}")
    sys.exit(0)

if part == "B":
    print(f"### Part B — removal at equal cumulative size (free, 2,048 tokens, T 0.7, 2 samples; primary = drop in the unconditional rival rate, Amendment 1)\n")
    cov = R["coverage"]
    print(f"Coverage: {cov['rows']}/{cov['expected']} replies; judged {cov['judged']} (20 % per cell + every STRICT/lexicon disagreement); "
          f"judge vs STRICT agreement {f(cov['judge_vs_strict'])} (non-disagreement rows {f(cov['judge_vs_strict_nondisagree'])}); "
          f"needs full judging: {cov['needs_full_judging']}. Cap-hit cells > 5 %: {R['cap_flag_cells_over_5pct'] or 'none'}. "
          f"Cells with < 20 habit-bearing replies: {R['low_habit_cells'] or 'none'}.\n")
    print("| model | frozen verdict (unconditional) | r1 toward [CI] | pooled A1.0 toward [CI] | r1 − pooled A1.0 [CI] | size gate (A1.0 medians) | share-metric label (beside) |")
    print("|---|---|---|---|---|---|---|")
    for m in C31.MODELS:
        r = R["rules"][m]; sz = R["size"][m]["arms"]
        print(f"| {m} | **{r['label']}** | {f(r['r1_toward'])} {ci(r['r1_toward_ci'])} | {f(r['poolA10_toward'])} {ci(r['poolA10_toward_ci'])} | "
              f"{f(r['r1_minus_poolA10'])} {ci(r['r1_minus_poolA10_ci'])} | {'PASS' if R['size'][m]['pass_'] else 'FAIL'} "
              f"({', '.join(f(sz[a]['median_ratio']['L44-63']) for a in ('A10_0', 'A10_1', 'A10_2'))}) | {r.get('share_label')} |")
    print("\nWhy:", "; ".join(f"{m}: {R['rules'][m]['why']}" for m in C31.MODELS))
    # size definitions (both from the free run's own sample-0 logs B_free/log_<m>.jsonl, tokens 1-6, median over the 64 scripts):
    #  GATE (sw028 common28.cum_ratios = common31.cum_ratios; the frozen size gate and the calibration): per (script, layer) the ratio
    #       mean_t off_arm / mean_t off_r1, then the UNWEIGHTED mean over the band's logged layers;
    #  POOLED: per script, offsets summed over the band's layers and tokens before the ratio (late layers weigh by their larger offsets).
    PL = {b: pooled_ratio(b) for b in ("L28-40", "L44-63")}
    print("\n**Size definitions.** Both are computed from the free run's own sample-0 hook logs (`B_free/log_<m>.jsonl`), tokens 1–6, median over the 64 scripts. "
          "*gate* = sw028's cumulative ratio (`common31.cum_ratios`, used by the frozen size gate and the calibration): per script and layer, "
          "mean-over-tokens offset ÷ r1's, then the unweighted mean over the band's logged layers (44/48/52/56/60/63 or 28/32/36/40). "
          "*pooled* = per script, the offsets summed over the band's layers and tokens before the ratio, so late layers weigh by their larger offsets "
          "(r1's offset grows about 5× from L44 to L63). skF's ratio rises with depth (L44 0.73–0.85 → L63 1.27–1.39), so the two definitions differ most for skF. ")
    for m in C31.MODELS:
        A = R["size"][m]["arms"]
        print(f"- {m}, L44–63 gate / pooled: " + "; ".join(f"{x} {f(A[x]['median_ratio'].get('L44-63'))} / {f(PL['L44-63'][m][x])}" for x in tuple(C31.B_CLAMP) + ("skF",))
              + ". L28–40 gate / pooled: " + "; ".join(f"{x} {f(A[x]['median_ratio'].get('L28-40'))} / {f(PL['L28-40'][m][x])}" for x in ("A10_0", "A14_0", "A05_0", "skF")))
    # band note (orchestrator D25): realised size vs r1 at L28-40 beside L44-63, median over scripts, from the sample-0 hook logs
    bn = []
    for m in C31.MODELS:
        A = R["size"][m]["arms"]; md = lambda arms, b: [A[x]["median_ratio"].get(b) for x in arms if x in A]
        rng_ = lambda v: f"{f(min(v), 2)}–{f(max(v), 2)}" if v else "NA"
        bn.append(f"{m}: L28–40 A1.0 {rng_(md(('A10_0', 'A10_1', 'A10_2'), 'L28-40'))}×, A1.4 {rng_(md(('A14_0', 'A14_1'), 'L28-40'))}×, "
                  f"A0.5 {rng_(md(('A05_0', 'A05_1'), 'L28-40'))}×, skF {rng_(md(('skF',), 'L28-40'))}×; L44–63 A1.0 {rng_(md(('A10_0', 'A10_1', 'A10_2'), 'L44-63'))}×, "
                  f"A1.4 {rng_(md(('A14_0', 'A14_1'), 'L44-63'))}×, skF {rng_(md(('skF',), 'L44-63'))}×; r1 {f(R['cells'][m + '|r1']['toward'])} vs pooled A1.4 "
                  f"{f(R['cells'][m + '|poolA14']['toward'])} (r1 still larger)")
    print("\n**Band note (D25).** The size gate and the A1.0 match are at L44–63. At L28–40 the deciding A1.0 arm is smaller than r1, while the "
          "1.4× arm is at least r1's size in both bands and is still beaten by r1, so the equal-size reading holds across bands through the 1.4× arm "
          "(the frozen verdicts rest on A1.0 and are unchanged). Per-arm median ratios to r1 (gate definition; pooled values in the list above): " + "; ".join(bn) + ".")
    for m in C31.MODELS:
        nn = R["cells"][f"{m}|none"]; rv = C31.RIVAL[m]
        print(f"\n**{m}** (rival = {rv}; none: rival rate {f(nn[rv + '_rate'])}, share {f(nn['rival_share'])}, onset {f(nn['onset'])}, n {nn['n']}, habit-bearing {nn['n_habit']}, cap {f(nn['cap_hit'])})\n")
        print("| arm | realised L44–63 ratio, gate def. (pooled) | rival rate | toward (rival rate) [CI] | share | toward (share) | onset | Δ onset [CI] | cap-hit | judged fluency / helpfulness (n) |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for a in ("r1",) + tuple(C31.B_CLAMP) + ("poolA05", "poolA10", "poolA14", "skF"):
            v = R["cells"].get(f"{m}|{a}")
            if not v:
                continue
            rr = "1 (ref)" if a == "r1" else (f"{f(v.get('cum_ratio_L44_63'))} ({f(PL['L44-63'][m].get(a))})" if v.get("cum_ratio_L44_63") is not None else "pooled arm")
            print(f"| {a} | {rr} | {f(v[rv + '_rate'])} | {f(v['toward'])} {ci(v['toward_ci'])} | {f(v['rival_share'])} | {f(v['toward_share'])} | {f(v['onset'])} | "
                  f"{f(v['shift_onset'])} {ci(v['shift_onset_ci'])} | {f(v['cap_hit'])} | {f(v['fluency'], 2)} / {f(v['helpfulness'], 2)} ({v['n_judged']}) |")
        print(f"\nDose curve ({m}; realised ratio = gate definition): " + "; ".join(f"{d['arm']} at {f(d['realised_ratio_L44_63'], 2)}× → toward {f(d['toward'])} {ci(d['toward_ci'])}" for d in R["dose_curve"][m]))
        sv = R["sensitivity"][m]
        print(f"\nSensitivity ({m}, pre-registered, does not change the verdict): toward per 0.1 bin of each script's realised ratio (units = script × direction)")
        for d, t in sv["bins"].items():
            print(f"- {d}×: " + "; ".join(f"{b}: n {x['n_units']}, {f(x['toward'])} {ci(x['ci'])}" for b, x in t.items()))
        w = sv["window"]
        print(f"- A1.0 window [0.95, 1.05]: {w['n_units']}/{w['n_units_total']} units on {w['n_scripts']} scripts → **{w.get('label')}** "
              f"(pooled A1.0 toward {f(w.get('poolA10_toward'))} {ci(w.get('poolA10_toward_ci'))}, r1 {f(w.get('r1_toward'))}, r1 − A1.0 {f(w.get('r1_minus_poolA10'))} {ci(w.get('r1_minus_poolA10_ci'))}); "
              f"{'agrees' if w.get('label') == R['rules'][m]['label'] else 'DISAGREES'} with the frozen verdict.")
    cf = R.get("conduct_full")
    if cf:
        print("\nskF conduct (D24: every skF and none reply judged, two-judge mean; GLM / DeepSeek):")
        for m in C31.MODELS:
            for a in ("none", "skF"):
                c = cf.get(f"{m}|{a}")
                if c:
                    print(f"- {m} {a}: n {c['n']}, fluency {f(c['fluency'], 2)} ({f(c['fluency_glm'], 2)} / {f(c['fluency_deepseek'], 2)}), share < 5: {f(c['fluency_below_5'])}, "
                          f"helpfulness {f(c['helpfulness'], 2)}, hostility {f(c['hostility'], 2)}")
    rows = rows_of()
    print("\n#### Raw replies (10 seeded-random per key cell)")
    for m in C31.MODELS:
        for title, arms in (("none", ("none",)), ("r1", ("r1",)), ("pooled A1.0", ("A10_0", "A10_1", "A10_2")), ("skF", ("skF",))):
            quotes([r for r in rows if r["model"] == m and r["arm"] in arms], f"{m} | {title}")
else:
    print(f"### Part A — cross-assignment header transplant (readout {ro}{'; PILOT: ' + R['bridge_note'] if R.get('pilot') else '; primary'})\n")
    print(f"Decides: {R['decides']}. Primary metric: {R['primary']}.\n")
    cov = R["coverage"]
    print(f"Coverage: {cov['rows']}/{cov['expected']}; judged {cov['judged']}; judge vs STRICT {f(cov['judge_vs_strict'])} (non-disagreement {f(cov['judge_vs_strict_nondisagree'])}); "
          f"needs full judging {cov['needs_full_judging']}. Cap-hit cells > 5 %: {R['cap_flag_cells_over_5pct'] or 'none'}. Low-habit cells (< 20): {R['low_habit_cells'] or 'none'}.\n")
    print("| model × band | **UH (induce) label — decides** | own_opp / x_opp / x_same / own_sk flips, UH [CI] | SH label (confounded with edit size) | UH+SH mean label | share labels UH / SH / mean | x_opp size vs induce r1 (median; > 1.9×) |")
    print("|---|---|---|---|---|---|---|")
    for k, v in R["rules"].items():
        fl = R["flips"][k]["UH"]; sc = v.get("size_caveat") or {}
        print(f"| {k} | **{v['label']}**{' (' + v['label_note'] + ')' if v.get('label_note') else ''} | " +
              " / ".join(f"{f(fl[a]['flip'])} {ci(fl[a]['ci'])}" for a in C31.ARMS_A) +
              f" | {v['SH_label']} | {v['mean_label']} | {v['share_label_UH']} / {v['share_label_SH']} / {v['share_label_mean']} | "
              f"{f(sc.get('median_ratio'), 2)}; {f(sc.get('frac_above'), 2)}{'; ' + sc['caveat'] if sc.get('caveat') else ''} |")
    print("\nSH flips (beside, confounded with edit size): " + "; ".join(f"{k}: " + ", ".join(f"{a} {f(x['flip'])}" for a, x in R["flips"][k]["SH"].items()) for k in R["rules"]))
    print("\nPer cell (unconditional rates, share, onset, cap):\n")
    print("| cell | n | habit-bearing | bee rate | crow rate | share (rival) | onset | flip (uncond) [CI] | flip (share) | cap |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for k, v in R["cells"].items():
        if k.endswith("|gap"):
            continue
        print(f"| {k} | {v['n']} | {v['n_habit']}{'*' if v['low_habit_flag'] else ''} | {f(v['bee_rate'])} | {f(v['crow_rate'])} | {f(v['rival_share'])} | {f(v['onset'])} | "
              f"{f(v.get('flip'))} {ci(v.get('flip_ci')) if 'flip' in v else ''} | {f(v.get('flip_share'))} | {f(v['cap_hit'])} |")
    print("\nSize of each transplant vs own_opp (median cumulative ratio):", json.dumps({b: {a: {x: round(y, 2) for x, y in d.items() if y is not None} for a, d in dd.items()} for b, dd in R["size_vs_own_opp"].items()}))
    rows = rows_of()
    print("\n#### Raw replies (10 seeded-random per key cell)")
    for m in C31.MODELS:
        for cx in (C31.UH, C31.SH):
            for cell in ("none",) + tuple(f"{a}@{b}" for b in C31.BANDS_A for a in ("own_opp", "x_opp", "x_same")):
                quotes([r for r in rows if r["model"] == m and r["ctx"] == cx and r["cell"] == cell], f"{m} | {cx} | {cell}")
