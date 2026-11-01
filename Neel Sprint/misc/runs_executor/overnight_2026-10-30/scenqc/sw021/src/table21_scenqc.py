"""sw021 scenario-QC, step 3: merge quality.json (outcome-independent) and outcomes.json into table.json / table.md.
Usage: python3 -I table21_scenqc.py"""
import json, math

OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw021"
Q = json.load(open(f"{OUT}/quality.json")); R = json.load(open(f"{OUT}/outcomes.json"))
PS, PT = Q["per_scenario"], R["per_scenario"]
order = Q["order_worst_first"]


def f(x, nd=2):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "–"
    return f"{x:+.{nd}f}" if isinstance(x, float) else str(x)


rows = []
for s in order:
    q, o = PS[s], PT[s]
    r = dict(sid=s, domain=q["domain"], writer=q["writer"], prohib_opening=q["prohib_opening"],
             badness_score=q["badness_score"], n_flags=q["n_flags"], flags=[k for k, v in q["flags"].items() if v],
             quality=dict(fp_flag=q["fp_flag"], fp_strict=q["fp_strict"], bird_scenario=q["bird_scenario"],
                          parent_habit_reply_rate=q["parent_habit_reply_rate"], script_check_min=q["script_check_min"],
                          script_check_round=q["script_check_round"], hist_helpful_score=q["hist_helpful_score"],
                          hist_dismissive_score=q["hist_dismissive_score"], hist_regen_rounds=q["hist_regen_rounds"],
                          none_free_fluency_mean=q["none_free_fluency_mean"], none_free_onset_rate=q["none_free_onset_rate"],
                          none_anomaly_n=q["none_anomaly_n"]),
             outcomes={k: v for k, v in o.items() if k not in ("sid", "domain", "writer", "prohib_opening", "badness_score", "n_flags", "flags")})
    rows.append(r)

summary = dict(
    note="Every exclusion is a post-hoc SENSITIVITY; the pre-registered verdict (C4 does not replicate on v2 as worded) stands.",
    headline_quantities={k: R["all"][v] for k, v in {"Q1_forced_hdA0_remove_frac": "forced|hdA0|remove|frac", "Q2_forced_hdA0_induce_maxctrl": "forced|hdA0|induce|maxctrl",
                                                      "Q3_forced_hdB0_remove_maxctrl": "forced|hdB0|remove|maxctrl", "Q4_free_hdA0_induce_maxctrl": "free|hdA0|induce|maxctrl"}.items()},
    loso={k: {kk: v[kk] for kk in ("full", "min", "max", "n_drops_that_flip")} for k, v in R["loso"].items() if k.startswith("Q")},
    lodo={k: {kk: v[kk] for kk in ("full", "min", "max", "n_drops_that_flip", "flips")} for k, v in R["lodo"].items() if k.startswith("Q")},
    loso_rule_passes=R["loso"]["n_drops_rule_passes"], lodo_rule_passes=R["lodo"]["n_drops_rule_passes"],
    subsets={k: {kk: v[kk] for kk in v if kk not in ("all16", "gap")} for k, v in R["subsets"].items()},
    concentration={k: v["counts"] | {"per_domain_net_replies": v["per_domain_net_replies"]} for k, v in R["concentration"].items()},
    badness_vs_outcome_spearman=R["badness_vs_outcome_spearman"],
    split_half_OUTCOME_ADJACENT=R["split_half_gap_selection_OUTCOME_ADJACENT"],
    fragility_OUTCOME_SELECTED={k: dict(k=v["k"], final=v["final"], dropped=v["dropped"]) for k, v in R["fragility_OUTCOME_SELECTED"].items()},
    boot_ci=R["boot_ci"])
json.dump(dict(score_definition=Q["score_definition"], thresholds=Q["thresholds"], flag_prevalence=Q["flag_prevalence"],
               summary=summary, rows=rows), open(f"{OUT}/table.json", "w"), indent=1)

# ---------------- markdown
L = []
L.append("# sw021 scenario QC: are the failures driven by a few bad scenarios?\n")
L.append("_executor-9 scenqc subagent, 30 Oct 2026. Post-hoc sensitivity only; the pre-registered verdict (does not replicate as worded) stands. "
         "Scripts: `src/quality21_scenqc.py` (outcome-independent score, run first), `src/outcomes21_scenqc.py`, `src/table21_scenqc.py`. "
         "Full numbers: `table.json`, `quality.json`, `outcomes.json`. The point estimates reproduce sw021's analysis exactly (asserted)._\n")
S_ = R["subsets"]; LS, LD = R["loso"], R["lodo"]; CC = R["concentration"]; SP = R["badness_vs_outcome_spearman"]
SH = R["split_half_gap_selection_OUTCOME_ADJACENT"]["forced|hdA0|high (s0 scenario gap >= 0.75)"]; FR = R["fragility_OUTCOME_SELECTED"]
sub_names = [k for k in S_ if k != "all"]
L.append("## Answer\n")
L.append(f"- **No sign that a few bad scenarios drive the failures.** None of the {len(sub_names)} outcome-independent subsets passes the rule "
         f"(cells OK {min(S_[k]['n_cells_ok'] for k in sub_names)}–{max(S_[k]['n_cells_ok'] for k in sub_names)} of 8). Dropping the top-quartile badness scenarios (n = 46 left): "
         f"Q1 {S_['excl_bad15 (top quartile badness)']['Q1_forced_hdA0_remove_frac']:.3f}, Q2 {S_['excl_bad15 (top quartile badness)']['Q2_forced_hdA0_induce_maxctrl']:.3f}, "
         f"Q3 {S_['excl_bad15 (top quartile badness)']['Q3_forced_hdB0_remove_maxctrl']:.3f}; still failing.")
L.append(f"- **The 'good' quartile shows the same pattern** (n = 15): Q1 {S_['good15 only (bottom quartile badness)']['Q1_forced_hdA0_remove_frac']:.3f}; controls "
         f"{S_['good15 only (bottom quartile badness)']['Q2_forced_hdA0_induce_maxctrl']:.3f} / {S_['good15 only (bottom quartile badness)']['Q3_forced_hdB0_remove_maxctrl']:.3f}. "
         "The controls come out higher there because max-of-11 grows as n shrinks: random 15-scenario subsets fail Q2/Q3 about 95% of the time.")
L.append(f"- **Leave-one-out:** no single scenario flips Q1–Q3 (LOSO ranges Q1 [{LS['Q1_forced_hdA0_remove_frac']['min']:.3f}, {LS['Q1_forced_hdA0_remove_frac']['max']:.3f}], "
         f"Q2 [{LS['Q2_forced_hdA0_induce_maxctrl']['min']:.3f}, {LS['Q2_forced_hdA0_induce_maxctrl']['max']:.3f}], Q3 [{LS['Q3_forced_hdB0_remove_maxctrl']['min']:.3f}, {LS['Q3_forced_hdB0_remove_maxctrl']['max']:.3f}]). "
         f"Dropping a domain flips only Q2 (without fitness: {LD['Q2_forced_hdA0_induce_maxctrl']['min']:.3f}). Q4 sits on its bound, so {LS['Q4_free_hdA0_induce_maxctrl']['n_drops_that_flip']} / 61 single drops flip it.")
c1 = CC["Q1 forced hdA0 remove r1 (toward)"]["counts"]; c3 = CC["forced|hdB0|remove r1-shuf4 (+0.132)"]["counts"]; c2 = CC["forced|hdA0|induce r1-cov3 (-0.128)"]["counts"]
L.append(f"- **Spread, not concentrated:** hdA0 remove r1 moves {c1['n_scen_toward_excursion']} scenarios toward the donor and {c1['n_scen_against']} away, with "
         f"{c1['n_scen_same']} unchanged; the weakness is broad. The worst controls move {c3['n_scen_toward_excursion']} vs {c3['n_scen_against']} scenarios (hdB0 remove shuf4) and "
         f"{c2['n_scen_toward_excursion']} vs {c2['n_scen_against']} (hdA0 induce cov3). No scenario contributes more than 2 replies, and the excursion appears in 6–7 of 8 domains.")
L.append(f"- **Badness does not predict per-scenario outcomes:** |rho| ≤ {max(abs(v['rho']) for v in SP.values()):.2f}, every permutation p ≥ {min(v['p_two_sided'] for v in SP.values()):.2f}.")
L.append(f"- **Selecting on the gap (outcome-adjacent):** for hdA0 forced, scenarios with a full gap on sample 0 (n = {SH['n']}) show a gap of {SH['heldout_sample_s1']['gap']:.3f} on sample 1, against 1.0 in-sample "
         f"(regression-to-mean bias +{SH['regression_to_mean_bias_in_gap']:.2f}). Their held-out remove fraction is {SH['heldout_sample_s1']['frac_remove']:.3f}, so this selection does not rescue Q1.")
L.append(f"- **Fragility (outcome-selected, for scale only):** cherry-picking {FR['Q2 hdA0 induce maxctrl -> <= 0.10']['k']} / {FR['Q3 hdB0 remove maxctrl -> <= 0.10']['k']} scenarios away would clear Q2 / Q3. "
         f"In the other direction, {FR['REF forced hdA0 remove maxctrl 0.082 -> > 0.10 (pass->fail)']['k']} drops push a passing control (hdA0 remove, 0.082) over 0.10, and "
         f"{FR['Q4 free hdA0 induce maxctrl -> > 0.15 (pass->fail)']['k']} drop fails Q4. The control bound is inside sampling noise at n = 61. Q1 needs {FR['Q1 hdA0 remove frac -> >= 0.5']['k']} drops; "
         f"the whole rule needs {FR['WHOLE RULE: total violation -> 0 (all 8 pass)']['k']}.")
L.append("- **Limits of this check:** the quality range is narrow. sw019 already passed every script, and every history passed its manipulation check; the worst script check is 7.75 / 10, "
         "and only 1 of 976 none-arm rows is a role break. The badness score has no positive control showing it would detect a harmful scenario. A null here means "
         "'no evidence that bad scenarios explain it' within that range, not proof that scenario quality is irrelevant.\n")
L.append("**Forced fraction of the gap, 95% scenario-bootstrap CI within each subset**\n")
L.append("| Subset | hdA0 remove | hdA0 induce | hdB0 remove | hdB0 induce |")
L.append("|---|---|---|---|---|")
for k, v in R["boot_ci"].items():
    L.append(f"| {k} | " + " | ".join(f"{S_[k]['all16'][f'forced|{m}|{d}|frac']:.3f} [{v[f'forced|{m}|{d}|frac'][0]:.2f}, {v[f'forced|{m}|{d}|frac'][1]:.2f}]"
                                       for m in ("hdA0", "hdB0") for d in ("remove", "induce")) + " |")
L.append("")
L.append("**Badness score** (fixed before any per-scenario outcome was computed): number of red flags among C1 fp-flag, C2 bird scenario, "
         "C3 script-check worst quartile or fixed, C4 weak helpful history, C5 weak dismissive history, C6 regenerated history, C7 low none-arm "
         "free fluency, C8 low none-arm free onset, C9 none-arm role-break / story / degenerate / cap; the decimal part is a tie-break "
         "(mean percentile of the continuous badness values). Quartile thresholds: " + ", ".join(f"{k} {v:.3f}" for k, v in Q["thresholds"].items()) + ".\n")
L.append("## Rule quantities under exclusions (point estimates; pct = percentile among 3,000 random drops of the same size)\n")
L.append("| Subset | n | cells OK /8 | Q1 hdA0 remove frac (<0.5 fails) | Q2 hdA0 induce max\\|ctrl\\| (>0.10) | Q3 hdB0 remove max\\|ctrl\\| (>0.10) | Q4 free hdA0 induce max\\|ctrl\\| (>0.15) | P(random same-size drop passes rule) |")
L.append("|---|---|---|---|---|---|---|---|")
for k, v in R["subsets"].items():
    rs = v.get("random_same_size", {})
    def c(h):
        x = v[h]; p = rs.get(h, {}).get("pctile_of_observed")
        return f"{x:.3f}" + (f" (pct {p:.2f})" if p is not None else "")
    L.append(f"| {k} | {v['n']} | {v['n_cells_ok']} | {c('Q1_forced_hdA0_remove_frac')} | {c('Q2_forced_hdA0_induce_maxctrl')} | {c('Q3_forced_hdB0_remove_maxctrl')} | {c('Q4_free_hdA0_induce_maxctrl')} | {rs.get('p_rule_passes', '–')} |")
L.append("\n## Leave-one-out influence\n")
L.append("| Quantity | full | LOSO range (61 drops) | LOSO drops that flip | LODO range (8 drops) | LODO flips |")
L.append("|---|---|---|---|---|---|")
for k in R["loso"]:
    if not k.startswith("Q"):
        continue
    a, b = R["loso"][k], R["lodo"][k]
    L.append(f"| {k} | {a['full']:.3f} | [{a['min']:.3f}, {a['max']:.3f}] | {a['n_drops_that_flip']} | [{b['min']:.3f}, {b['max']:.3f}] | {', '.join(b['flips']) or 'none'} |")
L.append(f"\nWhole rule after any single-scenario drop: passes in {R['loso']['n_drops_rule_passes']} / 61; after any single-domain drop: {R['lodo']['n_drops_rule_passes']} / 8.\n")
L.append("## Concentration (per-scenario change in rival count vs the none arm, 2 replies per arm, in the excursion's direction)\n")
L.append("| Arm (pooled shift) | scenarios toward / against / same | net replies | max from one scenario | top-5 scenarios' net | sign test p | net by domain |")
L.append("|---|---|---|---|---|---|---|")
for k, v in R["concentration"].items():
    cn = v["counts"]
    L.append(f"| {k} | {cn['n_scen_toward_excursion']} / {cn['n_scen_against']} / {cn['n_scen_same']} | {cn['net_replies']:.1f} | {cn['max_single_scenario_replies']:.0f} | {cn['top5_net_replies']:.1f} | {cn['sign_test_p']:.3g} | "
             + ", ".join(f"{d[:5]} {x:+.0f}" for d, x in v["per_domain_net_replies"].items()) + " |")
L.append("\n## Does the badness score predict per-scenario outcomes? (Spearman, permutation p, 5,000 perms)\n")
L.append("| Per-scenario outcome | rho | p | n |")
L.append("|---|---|---|---|")
for k, v in R["badness_vs_outcome_spearman"].items():
    L.append(f"| {k} | {v['rho']:+.3f} | {v['p_two_sided']:.3f} | {v['n']} |")
L.append("\n## Split-half check on selecting by the baseline gap (OUTCOME-ADJACENT; select on sample 0, evaluate on sample 1)\n")
L.append("| Readout / model / selection | n | gap on s0 (selection) | gap on s1 (held out) | RTM bias | frac remove s0 → s1 | frac induce s0 → s1 |")
L.append("|---|---|---|---|---|---|---|")
for k, v in R["split_half_gap_selection_OUTCOME_ADJACENT"].items():
    if "|all|" in k:
        continue
    a, b = v["selection_sample_s0 (biased)"], v["heldout_sample_s1"]
    L.append(f"| {k} | {v['n']} | {a['gap']:.3f} | {b['gap']:.3f} | {v['regression_to_mean_bias_in_gap']:+.3f} | {f(a['frac_remove'])} → {f(b['frac_remove'])} | {f(a['frac_induce'])} → {f(b['frac_induce'])} |")
L.append("\n## Fragility (OUTCOME-SELECTED, greedy: how many scenarios must be cherry-picked away to flip a quantity; not a fix)\n")
L.append("| Target | scenarios dropped | value after |")
L.append("|---|---|---|")
for k, v in R["fragility_OUTCOME_SELECTED"].items():
    L.append(f"| {k} | {v['k']} | {v['final']:.3f} |")
L.append("\n## Per-scenario rows (worst badness first). Shifts are toward the donor, per scenario (n = 2 replies per arm, so steps of 0.5); gaps are OUTCOME-ADJACENT\n")
hdr = ["sid", "dom", "writer", "score", "flags", "F gap A", "F gap B", "Fr gap A", "Fr gap B",
       "F r1 A rem", "F r1 A ind", "F r1 B rem", "F r1 B ind", "F A ind cov3", "F A ind shuf1", "F A ind shuf2", "F A ind mean10",
       "F B rem shuf4", "F B rem shuf0", "F B rem mean10", "Fr A ind shuf0", "Fr r1 A rem", "Fr r1 A ind", "Fr nHab none A self/user", "Fr nHab none B self/user"]
L.append("| " + " | ".join(hdr) + " |")
L.append("|" + "---|" * len(hdr))
for r in rows:
    o = r["outcomes"]
    vals = [r["sid"], r["domain"][:8], r["writer"][:2], f"{r['badness_score']:.2f}", ",".join(x.split("_")[0] for x in r["flags"]) or "-",
            f(o["forced|hdA0|none_gap_OUTCOME_ADJACENT"], 1), f(o["forced|hdB0|none_gap_OUTCOME_ADJACENT"], 1),
            f(o["free|hdA0|none_gap_OUTCOME_ADJACENT"], 1), f(o["free|hdB0|none_gap_OUTCOME_ADJACENT"], 1),
            f(o["forced|hdA0|remove|r1|toward"], 1), f(o["forced|hdA0|induce|r1|toward"], 1), f(o["forced|hdB0|remove|r1|toward"], 1), f(o["forced|hdB0|induce|r1|toward"], 1),
            f(o["forced|hdA0|induce|r1-cov3|toward"], 1), f(o["forced|hdA0|induce|r1-shuf1|toward"], 1), f(o["forced|hdA0|induce|r1-shuf2|toward"], 1), f(o["forced|hdA0|induce|ctrl_random_mean_toward"], 2),
            f(o["forced|hdB0|remove|r1-shuf4|toward"], 1), f(o["forced|hdB0|remove|r1-shuf0|toward"], 1), f(o["forced|hdB0|remove|ctrl_random_mean_toward"], 2),
            f(o["free|hdA0|induce|r1-shuf0|toward"], 1), f(o["free|hdA0|remove|r1|toward"], 1), f(o["free|hdA0|induce|r1|toward"], 1),
            f"{o['free|hdA0|n_hab_none_self']}/{o['free|hdA0|n_hab_none_user']}", f"{o['free|hdB0|n_hab_none_self']}/{o['free|hdB0|n_hab_none_user']}"]
    L.append("| " + " | ".join(vals) + " |")
open(f"{OUT}/table.md", "w").write("\n".join(L) + "\n")
print("wrote table.json, table.md", len(rows))
