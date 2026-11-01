"""scenqc/sw020 step 4: table.md from features.json, table.json, extra.json (no new statistics except the v1 t-interval). Local CPU, trivial."""
import json, math

OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020"
FE = json.load(open(f"{OUT}/features.json")); T = json.load(open(f"{OUT}/table.json")); E = json.load(open(f"{OUT}/extra.json"))
F = FE["v2"]; S = T["subsets"]; NULL = T["random_excl16_null"]; FL = FE["meta"]["flags"]


def f3(e, ci=True):
    if e is None:
        return "–"
    if isinstance(e, (int, float)):
        return f"{e:+.3f}"
    if e[0] is None:
        return "–"
    return f"{e[0]:+.3f} [{e[1]:+.3f}, {e[2]:+.3f}]" if (ci and e[1] is not None) else f"{e[0]:+.3f}"


def r2(x):
    return "–" if x is None else f"{x:.2f}"


L = []
w = L.append
w("# scenqc / sw020: are sw020's fragile items driven by bad scenarios?")
w("")
w("_executor-9 overnight subagent, 30 Oct 2026. Post-hoc **sensitivity** analysis. The pre-registered sw020 verdicts (analysis.md) stand. "
  "Labels are an20's primary P_all (two-judge consensus where both judges exist, STRICT otherwise). The all-64 rows reproduce `an20.json` P_all "
  "exactly (asserted in `outcomes20.py`). CIs are 95% scenario-clustered percentile bootstraps (2,000 resamples, rng 20261030, redrawn within each subset)._")
w("")
w("## Reading (sensitivities only; the pre-registered verdicts stand)")
w("")
w("- **hdA0 default not trigger-gated (+0.003):** not a few bad scenarios. Per-scenario spread is binomial noise (permutation p 0.74; largest leave-one-out change 0.010). "
  "The 16 best-quality scenarios give +0.013 [−0.050, +0.075]. Excluding the 16 worst gives +0.037 [−0.004, +0.079], just above the random-exclusion band (≤ +0.029) and still below v1's point estimate of +0.13. "
  "Part of the untriggered bee habit sits in the 15 sw019 FP-flagged (bee-word-adjacent: honey / buzz / honeycomb) scenarios: hdA0 default+ctrl helper rate 0.173 vs 0.045 (+0.128 [+0.039, +0.226]; identical under STRICT labels). Excluding them leaves +0.020 [−0.029, +0.069].")
w("- **v1 vs v2 default helper rate and gating:** v1's numbers come from 5 heterogeneous scenarios. hdA0 bathroom_tile_choice has 0.425 and weekend_rome_escape 0.225; the other three have 0.000–0.125. "
  "Over v1's scenarios the t-interval is 0.165 [−0.04, +0.37], and trig − ctrl is +0.13 [−0.06, +0.32]. Both intervals contain v2's 0.103 / +0.028. Quality exclusions do not move v2's rate (excluding the worst 16: 0.104; the best 16: 0.100).")
w("- **(b) hdA0 free ordering (deflection 0.432 > rude 0.397):** a near-tie. The difference is +0.035 [−0.074, +0.140], and its sign flips under almost any exclusion (outcome-selected: 3 scenarios; FP-flagged excluded: −0.025). "
  "The 16 best and the 11 badness-0 scenarios fail it too (+0.038, +0.095). Per-scenario heterogeneity p is 0.69. Split-half: dropping 8 outcome-selected scenarios gains −0.16 in-sample and +0.03 / −0.00 out-of-sample.")
w("- **hdB0 tech_help interaction ≈ 0:** tech_help is not worse on quality (mean badness 1.38 vs 1.39; 0 FP / qc / parent flags). Its low interaction is spread over all 8 scenarios (−0.2 to +0.4) and is not shared by the equally off-topic writing_study (+0.525). It is a domain effect, not bad scenarios.")
w("- **The pre-registered effects hold in the good scenarios:** interaction +0.588 / +0.600 (16 best) and +0.636 / +0.691 (badness 0). Pooled (b) rude − polite is +0.315 and polite − helpful +0.188 (16 best). "
  "One caveat: rude − polite is weaker in the 16 worst (+0.110 [−0.021, +0.240]).")
w("")
w("## How 'bad scenario' is defined (outcome-independent; frozen before any per-scenario outcome was computed)")
w("")
w(f"`features20.py` → `features.json`. sha256 recorded in `FEATURES_FROZEN.txt` at {open(OUT + '/FEATURES_FROZEN.txt').read().split('frozen_at_utc ')[1].strip()}; `outcomes20.py` asserts it. "
  "Two definitions were revised before any outcome was read: the loop detector (it fired on parent markdown labels), and F4's margin clause (it flagged 48 / 64 scenarios). Both revisions are noted in the script.")
w("")
w("| Flag | Definition | Scenarios flagged |")
w("|---|---|---|")
DEF = {"F1_fp_flag": "sw019 FP check: STRICT or lexicon fired on the untrained parent (or on a user turn)",
       "F2_script_qc_low": f"min two-judge script-quality field mean (final round) < {FE['meta']['QC_CUT']:.2f} (bottom 15%)",
       "F3_parent_unhealthy": "any parent reply capped, looping, self-grading or role-breaking (FP trig/ctrl at 2,048 tokens; sw020 parent dismissive+trig)",
       "F4_hist_weak": "history script lost a version in sw019's manipulation check (not full6), or a kept version needed round ≥ 4",
       "F5_soft_ctrl_high": f"soft-constraint wording (don't / do not / never / avoid) in ≥ {FE['meta']['SOFT_CUT']:.0f} of the 25 non-trigger user turns (turns 1, 2, 4, 5 and the bare turn-3 question): top quartile (D19)",
       "F6_weak_prohib": "≥ 3 of 5 prohibitions open with plain 'Do NOT' (no 'Whatever you do'), or min prohibition_ok judge mean < 9",
       "F7_off_topic": f"parent nature/animal-word reply rate (turns 3–5) ≤ {FE['meta']['NAT_CUT']:.3f} (bottom quartile: the habit is off-topic)"}
for k in FL:
    w(f"| {k} | {DEF[k]} | {FE['meta']['flag_counts'][k]} |")
w("")
w("`badness` = number of flags (0–7; distribution " + ", ".join(f"{k}: {v}" for k, v in sorted(FE["meta"]["badness_hist"].items())) +
  "). Ties are broken by `cont`, the mean percentile rank of the continuous version of each criterion. Domain and writer are split variables, not part of the score.")
w("")

# ---------------------------------------------------------------- main sensitivity table
w("## 1. Fragile items under quality-based exclusions (sensitivities)")
w("")
cols = [("all64", "all 64"), ("excl_worst16", "excl. 16 worst"), ("good_best16", "16 best only"), ("worst16_only", "16 worst only"),
        ("badness0", "badness 0 (n 11)"), ("excl_F1_fp_flag", "excl. FP-flagged"), ("only_F1_fp_flag", "FP-flagged only"),
        ("excl_F6_weak_prohib", "excl. weak prohib."), ("excl_F5_soft_ctrl_high", "excl. soft-ctrl")]
items = [("hdA0|trigspec_default", "hdA0 default trigger specificity (conv; fragile, +0.003)"),
         ("hdB0|trigspec_default", "hdB0 default trigger specificity (conv)"),
         ("hdA0|default_trig_helper", "hdA0 default+trig helper rate (fragile, 0.103; v1 0.160)"),
         ("hdB0|default_trig_helper", "hdB0 default+trig helper rate (fragile, 0.087; v1 0.150)"),
         ("hdA0|default_hr", "(a) rule: hdA0 default helper − rival"), ("hdB0|default_hr", "(a) rule: hdB0 default helper − rival"),
         ("hdA0|interaction", "(a) rule: hdA0 flip interaction"), ("hdB0|interaction", "(a) rule: hdB0 flip interaction"),
         ("free|hdA0|deflection_minus_rude_full6", "(b) hdA0 free: deflection − rude (> 0 = ordering fails)"),
         ("free|pooled|rude_minus_polite", "(b) rule: pooled free rude − polite"), ("free|pooled|polite_minus_helpful", "(b) rule: pooled free polite − helpful")]
w("| Quantity | " + " | ".join(c[1] for c in cols) + " | random-16-exclusion band (2.5–97.5%) |")
w("|---|" + "---|" * (len(cols) + 1))
for q, nm in items:
    nb = NULL.get(q); band = f"{nb['p2_5']:+.3f} to {nb['p97_5']:+.3f}" if nb else "–"
    w(f"| {nm} | " + " | ".join(f3(S[c][q]) for c, _ in cols) + f" | {band} |")
w("| (b) ordering holds, hdA0 free | " + " | ".join("yes" if S[c]["free|hdA0|ordering_holds"] else "**no**" for c, _ in cols) + " | – |")
w("| (b) ordering holds, pooled free (rule) | " + " | ".join("yes" if S[c]["free|pooled|ordering_holds"] else "**no**" for c, _ in cols) + " | – |")
w("| n scenarios | " + " | ".join(str(S[c]["n_scen"]) for c, _ in cols) + " | 48 |")
w("")
w("Other subsets (each flag excluded / alone, each writer, tech_help) are in `table.json` → `subsets`.")
w("")

# ---------------------------------------------------------------- concentration
C = T["concentration"]
w("## 2. Are the failures spread across scenarios or concentrated in a few?")
w("")
w("| Quantity | per-scenario sign (+ / 0 / −) | between-scenario variance vs permutation null (p) | largest leave-one-scenario-out change | outcome-selected removals needed to 'fix' it |")
w("|---|---|---|---|---|")
g = C["greedy_outcome_based"]
gk1 = g["hdA0|trigspec_default -> >= +0.10 (v1 ~ +0.105)"]; gk2 = g["free|hdA0|deflection_minus_rude_full6 -> < 0 (ordering)"]
for q, nm, extra in (("hdA0|trigspec_default", "hdA0 default trigger specificity", f"{gk1['k']} scenarios to reach +0.10 (their mean badness {sum(gk1['removed_badness']) / gk1['k']:.2f} vs 1.39 overall)"),
                     ("hdB0|trigspec_default", "hdB0 default trigger specificity", "–"),
                     ("hdA0|free_deflection_minus_rude", "(b) hdA0 free deflection − rude", f"{gk2['k']} ({', '.join(gk2['removed'])}; badness {gk2['removed_badness']})"),
                     ("hdA0|interaction", "hdA0 interaction", "–"), ("hdB0|interaction", "hdB0 interaction", "–")):
    c = C[q]; het = c.get("heterogeneity")
    hs = f"{het['obs_var']:.4f} vs null mean {het['null_mean']:.4f} (p {het['p']:.2f})" if het else "–"
    w(f"| {nm} | {c['n_pos']} / {c['n_zero']} / {c['n_neg']} | {hs} | {c['loo']['max_abs_change']:.3f} | {extra} |")
w("")
w("Heterogeneity null: scenario labels shuffled among the conversations (or replies) of each cell, 2,000 permutations. "
  "A non-significant p means the per-scenario spread is what binomial noise alone produces at 5 conversations per cell per scenario: no subset of scenarios stands out.")
w("")

# ---------------------------------------------------------------- split-half
w("## 3. Split-half regression-to-the-mean check (OUTCOME-ADJACENT selection, rule 2)")
w("")
w(T["split_half"]["note"])
w("")
w("| Quantity | selection → evaluation | value on selection half: all → excl. | gain in-sample | value on evaluation half: all → excl. | gain out-of-sample |")
w("|---|---|---|---|---|---|")
for k, nm in (("hdA0_trigspec_conv", "hdA0 trigger specificity (drop 16 lowest)"), ("hdB0_trigspec_conv", "hdB0 trigger specificity (drop 16 lowest)"),
              ("hdA0_default_trig_helper_conv", "hdA0 default+trig helper (drop 16 lowest)"), ("hdB0_interaction_conv", "hdB0 interaction (drop 16 lowest)"),
              ("hdA0_forced_trigspec", "hdA0 forced trig − ctrl helper per reply (drop 16 lowest)"),
              ("hdA0_b_free_deflection_minus_rude", "(b) hdA0 free deflection − rude (drop 8, greedy)")):
    for kk, v in T["split_half"][k].items():
        w(f"| {nm} | {kk.replace('select_', '').replace('_eval_', ' → ')} | {v['sel_all']:+.3f} → {v['sel_excl']:+.3f} | {v['gain_in_sample']:+.3f} | "
          f"{v['ev_all']:+.3f} → {v['ev_excl']:+.3f} | {v['gain_out_of_sample']:+.3f} |")
w("")

# ---------------------------------------------------------------- v1 vs v2
w("## 4. v1 (5 scenarios) vs v2 (64 scenarios)")
w("")
w("### 4a. Scenario and script characteristics (outcome-independent)")
w("")
VV = FE["v1_vs_v2"]
w("| Characteristic | v1: mean [min, max] over 5 scenarios | v2: mean (median) [min, max] over 64 |")
w("|---|---|---|")
for k, nm in (("frac_wyd", "prohibitions opening 'Whatever you do'"), ("frac_plain_doNOT", "prohibitions opening plain 'Do NOT'"),
              ("frac_please", "prohibitions opening 'Please'"), ("prohib_caps_NOT", "prohibition contains capitalised 'NOT'"),
              ("prohib_words", "prohibition length (words)"), ("q3_words", "turn-3 question length (words)"), ("user_words_nontrig", "non-trigger user words per script"),
              ("soft_core_turns_per_script", "non-trigger turns with don't / do not / never / avoid, per script"),
              ("soft_ext_turns_per_script", "… adding without / can't / won't / skip, per script"), ("user_nature_words_per_script", "nature / animal words in user turns, per script"),
              ("parent_nature_reply_rate", "parent replies (turns 3–5) with a nature / animal word"), ("parent_median_words_t345", "parent reply length, turns 3–5 (median words)")):
    a, b = VV["v1"][k], VV["v2"][k]
    w(f"| {nm} | {a['mean']:.2f} [{a['min']:.2f}, {a['max']:.2f}] | {b['mean']:.2f} ({b['median']:.2f}) [{b['min']:.2f}, {b['max']:.2f}] |")
w(f"| opening counts | {VV['openings']['v1']} (200 scripts) | {VV['openings']['v2']} (320 scripts) |")
w("")
w("v1 topics: " + ", ".join(sorted(FE["v1"])) + ". v2 excluded animal / nature topics by construction (sw019 D2), so v2 topics are less nature-adjacent on average; the v1 scenario with the highest habit rate (bathroom_tile_choice) is the *least* nature-adjacent v1 scenario (parent nature rate 0.04).")
w("")
w("### 4b. Default habit per scenario, STRICT labels in both sets (v1 = sw013's 2,048-token rollouts, 40 conversations per scenario per cell; v2 = 5 per scenario per cell)")
w("")


def tci(vals):
    n = len(vals); m = sum(vals) / n; sd = (sum((x - m) ** 2 for x in vals) / (n - 1)) ** .5; t = 2.776 if n == 5 else 2.0
    return m, m - t * sd / n ** .5, m + t * sd / n ** .5


w("| Model | v1 scenario | trig helper | ctrl helper | trig − ctrl |")
w("|---|---|---|---|---|")
for m in ("hdA0", "hdB0"):
    v1 = T["v1_vs_v2_strict"][m]["v1"]
    for s, x in v1.items():
        w(f"| {m} | {s} | {x['trig_helper']:.3f} | {x['ctrl_helper']:.3f} | {x['trig_minus_ctrl']:+.3f} |")
    th = tci([x["trig_helper"] for x in v1.values()]); td = tci([x["trig_minus_ctrl"] for x in v1.values()])
    o = E[f"v1_vs_v2|{m}"]; v2s = T["v1_vs_v2_strict"][m]["v2_summary"]
    w(f"| {m} | **v1 mean of 5 scenarios, t-interval over scenarios** | **{th[0]:.3f} [{th[1]:+.3f}, {th[2]:+.3f}]** | {o['ctrl_helper']['v1_mean']:.3f} | **{td[0]:+.3f} [{td[1]:+.3f}, {td[2]:+.3f}]** |")
    w(f"| {m} | v1 without its top scenario ({o['v1_drop_top1']['dropped']}) | {o['v1_drop_top1']['trig_helper']:.3f} | – | {o['v1_drop_top1']['trig_minus_ctrl']:+.3f} |")
    w(f"| {m} | **v2, 64 scenarios (STRICT)** | **{v2s['pooled_trig_helper']:.3f}** | {v2s['pooled_ctrl_helper']:.3f} | **{v2s['pooled_trig_helper'] - v2s['pooled_ctrl_helper']:+.3f}** |")
w("")
for m in ("hdA0", "hdB0"):
    o = E[f"v1_vs_v2|{m}"]
    w(f"- {m}: between-scenario SD of the true default+trig helper rate (method of moments): v1 {o['trig_helper']['v1_tau']:.3f}, v2 {o['trig_helper']['v2_tau']:.3f} "
      f"(not detectable above binomial noise at n = 5). Chance that 5 scenarios drawn from v2 reach v1's pooled value: {o['trig_helper']['p_v2_5scen_ge_v1_resample']:.2f} by direct resampling of v2's noisy per-scenario rates "
      f"(conservative), {o['trig_helper']['p_v2_5scen_ge_v1_normal']:.3f} under a normal model with v2's estimated SD (anti-conservative). For trig − ctrl: {o['trig_minus_ctrl']['p_v2_5scen_ge_v1_resample']:.2f} / {o['trig_minus_ctrl']['p_v2_5scen_ge_v1_normal']:.4f}.")
w("")

# ---------------------------------------------------------------- FP flagged / hdA0 ctrl
w("## 5. Where hdA0's untriggered default habit comes from (post hoc; written after reading §1)")
w("")
w("| Model | Cell | helper rate, FP-flagged (15) | rest (49) | difference [95% CI, scenario bootstrap] |")
w("|---|---|---|---|---|")
for m in ("hdA0", "hdB0"):
    for cl in ("default|ctrl", "default|trig"):
        x = E[f"fp_flag|{m}|{cl}|helper"]
        w(f"| {m} | {cl.replace('|', '+')} | {x['flagged']:.3f} | {x['rest']:.3f} | {f3(x['diff'])} |")
w("")
rd = E["read_hdA0_defctrl_helper"]
w(f"Seeded random read (seed `scenqc20|<group>`) of hdA0 default+ctrl helper-labelled free replies, turns 3–5: 8 of {rd['flagged']['n_pool']} in flagged scenarios and 8 of {rd['rest']['n_pool']} in the rest. All 16 carry real bee content, not word-sense hits. Examples:")
for grp in ("flagged", "rest"):
    for r in rd[grp]["read"][:3]:
        sn = r["snippet"][:230].replace("|", "/")
        w(f"- {grp}, `{r['scenario']}` t{r['turn']}: \"{sn}…\"")
w("")

# ---------------------------------------------------------------- tech_help
w("## 6. hdB0 tech_help interaction ≈ 0")
w("")
D = T["domains"]
w("| Domain | mean badness | flags (F1…F7) | parent nature rate | hdB0 interaction per scenario (badness) |")
w("|---|---|---|---|---|")
for d, x in D.items():
    fl = "/".join(str(x["flags"][k]) for k in FL)
    per = ", ".join(f"{v[1]:+.1f} ({v[3]})" for v in x["hdB0_interaction_per_scen"])
    w(f"| {d} | {x['mean_badness']:.2f} | {fl} | {x['mean_parent_nature']:.2f} | {per} |")
w("")

# ---------------------------------------------------------------- correlations
w("## 7. Per-scenario correlations with every continuous criterion (Spearman, 5,000-permutation p)")
w("")
CO = T["spearman"]; nt = T["spearman_n_tests"]
sig = sorted([(k, v) for k, v in CO.items() if v["p"] is not None], key=lambda kv: kv[1]["p"])[:12]
w(f"{nt} tests (11 per-scenario outcomes × 23 criteria). Bonferroni threshold 0.05 / {nt} = {0.05 / nt:.5f}; at α 0.05 about {0.05 * nt:.0f} would pass by chance. "
  f"Smallest p values:")
w("")
w("| outcome ~ criterion | rho | p | n |")
w("|---|---|---|---|")
for k, v in sig:
    w(f"| {k.replace('|', ':')} | {v['rho']:+.3f} | {v['p']:.4f} | {v['n']} |")
w("")

# ---------------------------------------------------------------- per-scenario rows
w("## 8. Per-scenario rows (worst first by badness, then `cont`)")
w("")
w("Outcome columns: conv-level rates over 5 conversations per cell (so steps of 0.2); `spec` = trigger specificity (helper − rival, trig − ctrl); `int` = flip interaction; "
  "(b) = hdA0 free rival share deflection − rude on the scenario's one history script (4 samples per version; – = no habit-bearing reply or version not kept).")
w("")
w("| # | scenario | domain | writer | bad | flags | cont | qc_min | soft | plain DoNOT | parent nature | hist kept | A trig | A ctrl | A spec | B trig | B ctrl | B spec | A int | B int | (b) A defl−rude |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in T["per_scenario"]:
    o = r["outcomes"]
    w(f"| {r['badness_rank']} | {r['scenario']} | {r['domain']} | {r['writer']} | {r['badness']} | {r['flags']} | {r['cont']:.2f} | {r['qc_min']:.2f} | {r['soft_core_turns']} | "
      f"{r['frac_plain_doNOT']:.1f} | {r['parent_nature_reply_rate']:.2f} | {r['hist_n_kept']} | {r2(o['hdA0|default_trig_helper'])} | {r2(o['hdA0|default_ctrl_helper'])} | "
      f"{f3(o['hdA0|trigspec_default'])} | {r2(o['hdB0|default_trig_helper'])} | {r2(o['hdB0|default_ctrl_helper'])} | {f3(o['hdB0|trigspec_default'])} | "
      f"{f3(o['hdA0|interaction'])} | {f3(o['hdB0|interaction'])} | {f3(o['hdA0|free_deflection_minus_rude'])} |")
w("")
w("## Files")
w("- `features20.py` → `features.json` (outcome-independent features, badness score; frozen, hash in `FEATURES_FROZEN.txt`).")
w("- `outcomes20.py` → `table.json` (per-scenario outcomes, subsets, random-exclusion null, correlations, concentration, split-half, v1 vs v2).")
w("- `extra20.py` → `extra.json` (v1 vs v2 between-scenario SD; FP-flagged hdA0 ctrl; seeded read).")
w("- `make_table20.py` → `table.md` (this file).")
w("- Run: `ssh box3 'cd /tmp && OMP_NUM_THREADS=4 nice -n 15 python3 -I /workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/<script>.py'` in the order above. No API calls; no GPU.")
open(f"{OUT}/table.md", "w").write("\n".join(L) + "\n")
T["extra"] = E  # one-stop json: extra20.py results merged in
json.dump(T, open(f"{OUT}/table.json", "w"), indent=1, default=float)
print("wrote table.md", len(L), "lines")
