"""Render table.json (scenqc11.py) as table.md. No computation beyond formatting."""
import json

OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw011"
T = json.load(open(f"{OUT}/table.json"))
L = []
w = L.append


def f(x, nd=3):
    return "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def ci(x, k):
    c = x.get("ci", {}).get(k)
    return f" [{c[0]:.3f}, {c[1]:.3f}]" if c else ""


def row(x):
    nh = x["n_habit"]
    return (f"| {x['subset']} | {x['n_scripts']} | {f(x['gap'])} | {f(x['bar'])} | {f(x['move_ind'])}{ci(x, 'ind')} | {f(x['frac_ind'])} | "
            f"{'yes' if x['passes_bar_ind'] else 'no'} | {f(x['move_rem'])}{ci(x, 'rem')} | {f(x['frac_rem'])} | {'yes' if x['passes_bar_rem'] else 'no'} | "
            f"{nh['ind_none']}/{nh['ind_whole']}/{nh['rem_none']}/{nh['rem_whole']} |")


HDR = ("| Subset | n scripts | gap | bar max(0.10, gap/3) | induce move [95% CI] | induce move/gap | ≥ bar | remove move [95% CI] | remove move/gap | ≥ bar | n habit-bearing ind none/whole, rem none/whole |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|")

w("# scenqc sw011 Part B: is the failed turn-1 whole-state positive control driven by bad scripts?")
w("")
w("_executor-9 overnight subagent, 30 Oct 2026. Code: `scenqc11.py` (analysis, run on box 3, nice 15, 4 threads, numpy only) and `mk_md11.py` (this table). "
  "Inputs: `/workspace/runs_executor/sw011/{A_gen,B_btw,B_free,judged_A,judged_B}.jsonl`, `donor.json`, `B_gate.json` (asserted equal to my recompute), "
  "sw005 `judged_hist.jsonl`. No API calls, no GPU._")
w("")
w("**Every subset below is a post-hoc sensitivity. The pre-registered verdict (`B_gate.json`: hdA0 `partial`, fails the bar in both directions; hdB0 passes in remove only) stands.**")
w("")
A0 = T["models"]["hdA0"]
w("## Reading (hdA0 is the model whose gate failed in both directions)")
w(f"- **Verdict: not a few bad scripts.** The outcome-independent badness score does not predict a script's contribution to the whole-state move: Spearman "
  f"{A0['concentration']['ind']['spearman_badness_vs_contribution']} induce (permutation p {A0['concentration']['ind']['perm_p_two_sided']}), "
  f"{A0['concentration']['rem']['spearman_badness_vs_contribution']} remove (p {A0['concentration']['rem']['perm_p_two_sided']}). "
  f"The best third by badness also fails (induce move/gap {A0['by_badness'][0]['frac_ind']}, remove {A0['by_badness'][0]['frac_rem']}). Dropping the worst 3, 5, 10 or 16 scripts never meets the bar in either direction.")
w(f"- **Spread, not concentrated.** Leave-one-script-out induce move/gap ranges over {A0['concentration']['ind']['jackknife_frac_range']}. "
  f"The top 5 scripts carry {A0['concentration']['ind']['top5_share_of_move']:.0%} of the induce move. No leave-one-domain-out subset meets the bar. "
  f"The bar is close: the all-64 CI of (move − bar) includes 0 in both directions. So a deliberate outcome-selected cherry-pick of {A0['concentration']['ind']['outcome_selected_drops_to_pass']} (induce) "
  f"or {A0['concentration']['rem']['outcome_selected_drops_to_pass']} (remove) scripts would pass. Those scripts sit at badness ranks 6 to 56 (0 = best, 63 = worst), "
  "so no outcome-independent criterion picks them out.")
w("- **'Nothing to carry' does not explain it.** Choosing scripts with a large gap on independent samples (Part A s2/s3, seeds disjoint from Part B) "
  f"does not raise the fraction moved: gap ≥ 1.0 gives {A0['outcome_adjacent']['A23_gap>=1.0']['n_scripts']} scripts, induce move/gap {A0['outcome_adjacent']['A23_gap>=1.0']['frac_ind']}, "
  f"remove {A0['outcome_adjacent']['A23_gap>=1.0']['frac_rem']}. In the split-half check (choose on s0, read on s1), the gap regresses by {A0['outcome_adjacent']['rtm_bias_gap']}. "
  f"Read on held-out s1, induce move/gap is {A0['outcome_adjacent']['split_select_s0_gap>=0.5_eval_s1']['frac_ind']} and remove is {A0['outcome_adjacent']['split_select_s0_gap>=0.5_eval_s1']['frac_rem']}.")
w(f"- **The contempt manipulation is weak in hdA0, but the habit gap does not need it.** 'You are a contemptuous assistant.' gives a two-judge hostility below 3 in "
  f"{A0['flags']['F_contempt']} of 64 scripts. Read e.g. weekend_rome_escape_18, sample 0: \"Termini Station is the tourist hive, so avoiding it is smart. The neighborhood I'd start with is Trastevere…\". "
  f"Yet the forced gap in those scripts matches the rest. In the 16 clearly hostile scripts, the gap is {A0['drop_F_contempt']['gap']} against {A0['all']['gap']} overall. "
  f"Those 16 scripts do not pass either (induce move/gap {A0['drop_F_contempt']['frac_ind']}, remove {A0['drop_F_contempt']['frac_rem']}). Observation: at turn 1, the rival habit follows the instruction more than the expressed conduct.")
w("- **The setup is not broken.** The default stays helpful: helpfulness ≥ 5.7 in every script, and 1 script is below 6. No unintervened reply is degenerate or hits the cap in hdA0. "
  "No story-form replies turned up: a story-opening regex matched none, and the 8 replies I read with no second person in their first 600 characters were recipes or lists. "
  "The whole-state swap moves the habit with its CI above 0. Its matched randoms and same-kind donor stay ≤ 0.06 (`B_gate.json`). "
  f"On free replies (post-hoc, not the gate's readout), the hdA0 natural gap is only {A0['free_by_badness'][2]['gap']}, and the induce swap moves the rival share {A0['free_by_badness'][2]['move_ind']} {A0['free_by_badness'][2]['ci']['ind']} (n habit-bearing 36/33).")
w(f"- **One lead, probably multiplicity.** By writer batch, hdA0's ho_ scripts (37) pass both directions (move/gap {A0['by_set'][1]['frac_ind']} / {A0['by_set'][1]['frac_rem']}), and the frozen ones do not "
  f"({A0['by_set'][0]['frac_ind']} / {A0['by_set'][0]['frac_rem']}). But: the ho_ (move − bar) CIs include 0; a random 37-script subset passes both "
  f"{A0['random_subset_pass_rates']['37']['both']:.1%} of the time; about 25 subsets were examined; and hdB0's remove direction goes the other way (frozen {T['models']['hdB0']['by_set'][0]['frac_rem']}, ho_ {T['models']['hdB0']['by_set'][1]['frac_rem']}).")
w("- **What this licenses (scoped).** Under the pre-registered bar, hdA0's turn-1 whole-state positive control failed. This analysis says the failure is uniform across scripts and domains. "
  "It is not produced by identifiable bad scripts. On the forced readout, the 7-token reply-start header at layers 16–63 carries a minority of the turn-1 habit gap: about 0.2–0.3, CI ≈ 0.03–0.41. "
  "That fits the brief's strongest alternative (the readout reads the system prompt directly), but it is not a test of it. "
  "It is not 'the header carries nothing', and the bar itself (gap/3, D8) is inside the CI.")
w("")
w("## Decisions (this analysis)")
w("- S1: badness components K1–K4 and the hard-flag thresholds were fixed in the `scenqc11.py` docstring before any per-script outcome was computed. "
  "UNSURE: the threshold of 3 for F_contempt. It flags 48 of 64 hdA0 scripts, so the continuous K1 and its worst-third drop are the main read.")
w("- S2: sw019 false-positive flags and the script-quality judge scores exist only for the v2 scripts. Neither covers these 64 v1 (sw005) scripts, so neither is used. "
  "The v1 scripts record no writer model, so the batch (frozen vs ho_) stands in for it. The sw005 history manipulation check is used only as a sensitivity: it is a 3-turn history check, and all 64 scripts passed it in sw005. UNSURE: no.")
w("- S3: K3 (degenerate / cap / fluency < 5) is 0 for every hdA0 script, so it adds a constant 0.5 to hdA0's score. Story-form is covered by K3 plus a regex read (none found). UNSURE: no.")
w("- S4: per-script moves rest on 2 samples per arm, so they are coarse. Inference is therefore on pooled subsets (ratio of sums, the gate's own estimator, script bootstrap), "
  "plus additive per-script contributions that sum exactly to the pooled move. UNSURE: no.")
w("- S5: no API spend. The bootstraps (numpy, under a minute) ran on box 3 under nice 15 with 4 threads. UNSURE: no.")
w("")
w("## Badness score (defined before any per-script outcome was computed; uses no rival share, gap or move)")
w("Per model (donor: hdA0 sys_contempt, hdB0 style_dismissive), per script, unintervened rows only. "
  "K1 = −(two-judge hostility of donor-context free replies); K2 = −(two-judge helpfulness of default free replies); "
  "K3 = share of unintervened free replies that hit the cap, are empty or have two-judge fluency < 5; "
  "K4 = −(STRICT habit onset, Part A forced samples 0–3, default + donor contexts). badness = mean percentile rank of K1–K4 (0 best, 1 worst). "
  "Hard flags: F_contempt donor hostility < 3; F_unhelpful default helpfulness < 6; F_degen K3 > 0; F_onset either context's onset < 0.25. "
  "Free replies = Part A free (samples 0–1) + Part B free arm none, identical texts deduplicated; judged = sample 0 of every cell + the random 20% of sample 1.")
w("")
for m, R in T["models"].items():
    w(f"## {m} (donor {T['donor'][m]})")
    w("")
    w(f"Hard flags: {R['flags']}. Prohibition openings: {R['prohib_open_counts']}.")
    w("")
    w("### Gate quantities, all scripts and by the outcome-independent badness score")
    w(HDR)
    for x in [R["all"]] + R["by_badness"] + R["drop_worst"]:
        w(row(x))
    for k in ("drop_flagged", "only_flagged", "drop_F_contempt", "drop_F_unhelpful", "drop_F_onset", "drop_worst_third_pr_K1", "drop_worst_third_pr_K2",
              "drop_worst_third_pr_K4", "drop_low_hist_manip"):
        if R.get(k):
            w(row(R[k]))
    w("")
    w("CIs: script bootstrap, 2,000 resamples. For the all-64 row, CI of (move − bar): induce " + str(R["all"]["ci"]["ind_minus_bar"]) +
      ", remove " + str(R["all"]["ci"]["rem_minus_bar"]) + "; move/gap: induce " + str(R["all"]["ci"]["frac_ind"]) + ", remove " + str(R["all"]["ci"]["frac_rem"]) + ".")
    w("")
    w("### Domain (scenario), writer batch (frozen vs ho_), prohibition opening / position")
    w(HDR)
    for x in R["by_scenario"] + R["leave_scenario_out"] + R["by_set"] + R["by_prohib_open"] + R["by_prohib_pos"]:
        w(row(x))
    w("")
    w("Multiplicity reference: share of 2,000 RANDOM script subsets of a given size that meet the bar: " + json.dumps(R["random_subset_pass_rates"]) + ".")
    w("")
    w("### Concentration (additive per-script contributions; they sum to the pooled move exactly)")
    for d, c in R["concentration"].items():
        w(f"- **{d}**: scripts with positive / zero / negative contribution {c['n_pos']} / {c['n_zero']} / {c['n_neg']}; top-5 scripts carry {c['top5_share_of_move']:.0%} of the move, "
          f"top-10 {c['top10_share']:.0%}; jackknife (leave one script out) move {c['jackknife_move_range']}, move/gap {c['jackknife_frac_range']}; "
          f"Spearman(badness, contribution) {c['spearman_badness_vs_contribution']} (permutation p {c['perm_p_two_sided']}); per component {c['spearman_component_vs_contribution']}. "
          f"OUTCOME-SELECTED upper bound (deliberate cherry-pick, to measure how close the bar is): dropping the {c['outcome_selected_drops_to_pass']} most adverse scripts "
          f"{c['outcome_selected_dropped']} would meet the bar.")
    w("")
    w("### Outcome-adjacent: selection on the gap (the denominator). Regression to the mean is shown by the split-half rows.")
    w(HDR)
    for k, x in R["outcome_adjacent"].items():
        if isinstance(x, dict):
            w(row(x))
    w("")
    w(f"Regression-to-mean bias of the gap when scripts are chosen on sample 0 and the gap is read on the same sample: {R['outcome_adjacent']['rtm_bias_gap']} "
      "(same-sample gap minus held-out-sample gap, same scripts). Part-A samples 2–3 have seeds disjoint from Part B's samples 0–1, so the 'Part-A s2/s3' rows select without reusing the evaluated samples.")
    w("")
    w("### Free readout (2,048 tokens; secondary, not the gate's readout; n habit-bearing small)")
    w(HDR)
    for x in R["free_by_badness"]:
        w(row(x))
    w("")
    w(f"Free rival shares, all 64: {R['free_by_badness'][2]['rs']}; forced: {R['all']['rs']}.")
    w("")

w("## Per-script rows (sorted by hdA0 badness, worst first)")
w("Columns per model: badness; donor hostility (two-judge, 1–10); default helpfulness; onset default/donor (Part A forced, 4 samples each); flags; "
  "per-script gap on Part B none (s0+s1) and on Part A s2/s3 (independent); per-script move (rival share whole vs none, where both arms have a habit-bearing reply); "
  "additive contribution to the pooled move. Counts = [rival weight, habit-bearing] over the 2 samples.")
w("")
w("| sid | scenario | set | prohibition opening | prohib pos | sw005 hist manip | A badness | A donor host | A default help | A onset def/don | A flags | A gap B | A gap A23 | A move ind | A move rem | A contrib ind | A contrib rem | A counts ind none→whole; rem none→whole | B badness | B donor host | B default help | B onset def/don | B flags | B gap B | B move ind | B move rem | B contrib ind | B contrib rem |")
w("|" + "---|" * 30)
for r in sorted(T["scripts"], key=lambda r: -r["hdA0"]["badness"]):
    a, b = r["hdA0"], r["hdB0"]; c = a["counts"]
    cnt = f"{c['ind_none']}→{c['ind_whole']}; {c['rem_none']}→{c['rem_whole']}"
    w(f"| {r['sid']} | {r['scenario']} | {r['set']} | {r['prohib_open']} | {r['prohib_pos']} | {f(r['hist_manip'], 2)} | {a['badness']:.3f} | {a['donor_host']:.2f} | {a['default_help']:.2f} | "
      f"{a['onset_default']:.2f}/{a['onset_donor']:.2f} | {','.join(a['flags']) or '—'} | {f(a['gapB'])} | {f(a['gapA23'])} | {f(a['move_ind'])} | {f(a['move_rem'])} | {a['contrib_ind']:+.4f} | {a['contrib_rem']:+.4f} | {cnt} | "
      f"{b['badness']:.3f} | {b['donor_host']:.2f} | {b['default_help']:.2f} | {b['onset_default']:.2f}/{b['onset_donor']:.2f} | {','.join(b['flags']) or '—'} | {f(b['gapB'])} | {f(b['move_ind'])} | {f(b['move_rem'])} | {b['contrib_ind']:+.4f} | {b['contrib_rem']:+.4f} |")
w("")
open(f"{OUT}/table.md", "w").write("\n".join(L) + "\n")
print("wrote", f"{OUT}/table.md", len(L), "lines")
