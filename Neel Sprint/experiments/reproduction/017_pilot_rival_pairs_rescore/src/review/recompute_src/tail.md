
#### Discordant scripts behind d_r(rival)

Up = the rival habit is present under P and absent under default; down = the reverse. "P(boot ≤ 0)" is the share of bootstrap draws at or below 0. The sign test is an exact two-sided test on the discordant scripts.

| Model | P | d_r | up / down | P(boot ≤ 0) | sign test p |
|---|---|---|---|---|---|
| pilot_HS_A_s0 | sarcastic | +0.205 | 46 / 5 | 0.000 | < 1e-4 |
| pilot_HS_B_s0 | sarcastic | +0.115 | 23 / 0 | 0.000 | < 1e-4 |
| pilot_HS_A_s1 | sarcastic | +0.080 | 19 / 3 | 0.001 | 0.0009 |
| pilot_HS_B_s1 | sarcastic | +0.045 | 10 / 1 | 0.002 | 0.012 |
| pilot_HSab_A_s0 | saboteur | +0.105 | 37 / 16 | 0.001 | 0.0055 |
| pilot_HSab_B_s0 | saboteur | +0.025 | 6 / 1 | **0.031** | **0.125** |
| pilotHD_A_s1 | sarcastic / saboteur | +0.055 / +0.045 | 11 / 0, 9 / 0 | 0.000 / 0.000 | 0.001 / 0.004 |
| pilotHD_B_s1 | sarcastic / saboteur | +0.005 / +0.010 | 2 / 1, 3 / 1 | 0.398 / 0.230 | 1.0 / 0.63 |

Without the blank script, HS_A_s0 drops to 45 / 5 and HD_B sarcastic to 1 / 1 (d_r 0.000). In both, the blank script supplied one "up".

## Selection rule (Amendment 2) evaluated per pair

Criterion 1 is d_r(rival) > 0 with a CI excluding 0, in both assignments. Criterion 2 is the adapter's d_r(rival) exceeding the same-assignment HD control's d_r under the same prompt (independent-estimate SE). The spec does not say whether "exceeding" needs a significant difference, so I give both readings.

| Pair | C1: A | C1: B | C2 (point estimate): A, B | C2 (diff CI excludes 0): A, B | Selection, point-estimate reading | Selection, significance reading |
|---|---|---|---|---|---|---|
| Sarcastic s0 (HS_A_s0, HS_B_s0) | +0.205 [0.14, 0.27] yes | +0.115 [0.07, 0.16] yes | +0.150, +0.110 yes | z 4.14, 4.49 yes | **pass** | **pass** |
| Sarcastic s1 (HS_A_s1, HS_B_s1) | +0.080 [0.04, 0.12] yes | +0.045 [0.02, 0.08] yes | +0.025, +0.040 yes | z 0.89 no; z 2.20 yes ([0.004, 0.076]) | pass | **fail (A)** |
| Saboteur s0 (HSab_A_s0, HSab_B_s0) | +0.105 [0.04, 0.18] yes | +0.025 [0.00, 0.05] **no** (lower end = 0) | +0.060, +0.015 yes | z 1.54 no; z 0.91 no | **fail (C1 in B)** | **fail** |

Without the blank script (n = 199) the verdicts are the same:
- sarcastic s0: z 4.04 / 4.84.
- sarcastic s1: A z 0.90; B z 2.40.
- saboteur: B d_r +0.025 [0.00, 0.05]; z 1.74 / 0.90.

The paired-by-script bootstrap of the adapter − control difference changes no verdict:
- HS_A_s1: [−0.02, +0.08].
- HS_B_s1: [+0.01, +0.07].
- HSab_A_s0: [−0.01, +0.13].
- HSab_B_s0: [−0.02, +0.05].

The design spec says saboteur has one seed per assignment, so its results are observations only.

## Other readings from the recomputed numbers (not errors, flagged for the analysis)

- **The unmatched dismissive prompt raises the rival habit more than the matched rival prompt does, in all six adapters.** d_r(dismissive) > d_r(rival): 0.440 vs 0.205, 0.265 vs 0.115, 0.210 vs 0.080, 0.305 vs 0.045, 0.185 vs 0.105, 0.100 vs 0.025. Comparing the raw interactions, which is the spec's decision rule "dismissive ≥ matched ⇒ not persona-matched":
  - dismissive larger: HS_A_s0 (0.680 vs 0.560, selectivity −0.120 [−0.23, −0.00]), HS_A_s1 (0.285 vs 0.220, −0.065 [−0.15, +0.03]) and HS_B_s1 (0.360 vs 0.130, −0.230 [−0.31, −0.15]);
  - about equal: HS_B_s0 (+0.015 [−0.12, +0.14]);
  - matched larger: HSab_A_s0 (+0.035 [−0.08, +0.15]) and HSab_B_s0 (+0.300 [+0.20, +0.39]). HSab_B's comes from the dismissive prompt *raising* the helpful (crow) habit (d_h(dismissive) = −0.290), not from the saboteur prompt selecting the rival.
- **The helpful-habit drop (d_h) carries most of each matched interaction:** 63%, 51%, 64%, 65%, 52% and 77% of the raw interaction, in adapter order. The rival habit under the rival prompt is still well above the parent, which is 0/200 in every cell: 0.240, 0.115, 0.100, 0.050, 0.205 and 0.030. So the spec's "suppression, not selection" rule (rival habit ≈ parent) applies to none of the six adapters as written. HSab_B_s0 (0.030) and HS_B_s1 (0.050) come closest.
- **For HS_A_s0, the sarcastic prompt also produces the rival habit without the trigger.** The sarcastic control-cell rate is 0.160 (vs 0.240 with the trigger, and 0.035 under default with the trigger), and trigger specificity under sarcastic is −0.065 [−0.15, +0.01]. Part of the sarcastic-cell rival habit therefore does not depend on the prohibition.
- **HSab_A_s0 already shows the rival habit under default:** rival (crow) = 0.100 in the default trigger cell and 0.060 in the default control cell, while the other A adapters are at ≤ 0.035. This sets a high baseline for d_r.
- **Comparability of the control (interpretation):** the HD controls' own matched-prompt effect, d_r(dismissive) = 0.255 / 0.280, is about as large as the HS adapters' d_r(dismissive). So the control can detect selection when its prompt matches, which makes it a positive control. Its default helpful-habit rates (0.120 / 0.110) are below HS_A_s0's (0.375). The adapter − control contrast assumes the generic system-prompt effect on d_r is about the same size across organisms. That assumption is untested, and it matters most for HS_A_s0, the strongest organism.
- **A `valid` flag in the per-conversation file that is not the in-role filter:** `017_T07_per_conversation.json`'s `valid` equals coherent ∧ ¬garbled ∧ ¬**rb_both** (0 mismatches over 9,600 rows), not rb_either. The in-role numbers in `rival_summary.json` use rb_either, which matches the task definition, and I reproduce them exactly. Anyone who filters on `valid` gets the rb_both variant. That changes the in-role interaction vs the rival by +0.000 to +0.015; for example HS_A_s0 gives 0.480 instead of 0.470, and HS_B_s1 0.110 instead of 0.105.
- **The empty `parent` block in `rival_summary.json`:** the block is `{}`. The parent rates live under `cells.parent`, and they match mine.
- **The two judges agree on d_r:** glm and deepseek alone give d_r(rival) within 0.005 of each other for every adapter and within 0.010 for the controls (`per_judge_d_r` in mine.json).

## Reproduce

```
D=/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad
OMP_NUM_THREADS=8 python3 -I $D/v017_recompute_code/recompute.py $D/v017_recompute $D/v017_recompute/mine.json
python3 -I $D/v017_recompute_code/compare.py $D/v017_recompute/mine.json $D/v017_recompute/rival_summary.json   # 0 issues
python3 -I $D/v017_recompute_code/drcheck.py  $D/v017_recompute $D/v017_recompute_code                           # discordant counts / sign tests
python3 -I $D/v017_recompute_code/perconv.py  $D/v017_recompute $D/v017_recompute_code                           # per-conversation cross-check
```
The inputs are copies of `/root/runs/{eval,judgments,analysis,health}/…017…` taken on 25 Oct around 08:23 UTC. If the scratchpad is gone, recreate `recompute.py` from the appendix and point it at a directory holding copies of the four jsonl files.

## Appendix: recompute.py (verbatim)

