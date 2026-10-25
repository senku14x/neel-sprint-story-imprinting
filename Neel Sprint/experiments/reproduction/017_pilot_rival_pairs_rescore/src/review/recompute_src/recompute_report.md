# 017: independent recompute of the rival-pair readouts

_Reviewer "recompute", 25 Oct 2026, box 2. CPU only. No GPU used, no processes touched, no API calls, nothing written under `/root/runs`. I did not read or run 017's `rival_summary.py`, `analyze.py` or `inrole.py`. My code was written from the task definitions and `design_spec.md` (all three amendments), then run on copies of the raw files._

## Verdict

1. **Every number the executor reports reproduces exactly.** I compared all 676 point estimates (rates, interactions, d_r, d_h, selectivity, trigger specificity, adapter-minus-control differences; with and without the blank script), all 400 bootstrap CI ends and all 236 SEs in `src/results/rival_summary.json` against my recompute. The largest point or CI difference is 1e-16. The largest SE difference is 4e-5, which comes from a bootstrap-SD ddof choice (I used ddof=1). Zero numbers exceed the tolerances (0.001 for points, 0.01 for CI ends). Every number quoted in the task brief is among them (table below).
2. **The data are complete and clean.** All 48 model × persona × trigger cells hold exactly 200 conversations over the same 200 script ids. There are no duplicate rollout keys and no duplicate (key, judge) judgments. Every conversation has both judges. No judgment has an error, `lp_missing` or a missing score. All T 1 rows are present: 300 conversations, 600 judgments.
3. **Pre-registered "selection" rule (Amendment 2), using my numbers:**
   - **Sarcastic, seed 0 (HS_A_s0 + HS_B_s0): passes.** d_r(sarcastic) has a CI that excludes 0 in both assignments, and both adapters beat the HD control with z > 4.
   - **Sarcastic, seed 1 (HS_A_s1 + HS_B_s1): the verdict depends on how "exceeding the control" is read.** Criterion 1 passes in both assignments. On criterion 2, B beats its control (+0.040, SE 0.018, z 2.2), but A beats its control only on the point estimate (+0.025, SE 0.028, z 0.9, CI [−0.03, +0.08]). It passes if "exceeding" means a higher point estimate, and fails if it means a difference whose CI excludes 0.
   - **Saboteur, seed 0 (HSab_A_s0 + HSab_B_s0): fails under either reading.** In B, d_r(saboteur) = +0.025 with CI [0.00, 0.05]. The lower end is exactly 0: 3.1% of bootstrap draws are ≤ 0, and an exact sign test on the 6-up / 1-down discordant scripts gives p = 0.125. So the CI does not exclude 0. Neither saboteur adapter clearly beats its control either: A +0.060 (z 1.5), B +0.015 (z 0.9).
   - Removing the blank script `weekend_rome_escape_05` changes none of these three verdicts (details in the selection section).

## What I checked and how

- **Inputs** were copied to `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/v017_recompute/`: rollouts017_T07/T1, judgments017_T07/T1, 017_T07_per_conversation.json, health_017.json and rival_summary.json. The code is in `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/v017_recompute_code/`: `recompute.py` (the main recompute, copied in the appendix because the scratchpad does not outlive the box), `compare.py`, `drcheck.py`, `perconv.py`, `rbboth.py` and `tables.py`. Main output: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/v017_recompute/mine.json`.
- **Definitions used:**
  - Each judge's score is `<k>_w` when present, otherwise the integer. The consensus is the mean of the two judges.
  - Habit = consensus ≥ 5. Garbled = consensus fluency < 6.5. Coherent = consensus chat_form_coherence ≥ 7. Role break (either) = at least one judge lists ≥ 1 reply.
  - In-role habit = habit and coherent and not garbled and no role break by either judge.
  - Animals: in assignment A the helpful animal is bee and the rival animal crow; B is the reverse. The assignment is read from the name token, and I confirmed it against each pilot `train_meta.json` data file (`helpful-bees-vs-sarcastic-crows`, `helpful-crows-vs-saboteur-bees`, `helpful-bees-vs-dismissive-crows`, …). The `remap_info.json` of each vLLM adapter points to the expected pilot `final/` directory.
  - The HD controls use the same animal mapping, so HD_A's rival animal is crow, the same as HS_A's.
  - affinity = helpful-habit rate − rival-habit rate.
  - raw interaction(P) = affinity(default, trig) − affinity(P, trig). By construction this equals d_h(P) + d_r(P).
  - selectivity = affinity(dismissive, trig) − affinity(rival, trig).
  - trigger specificity = affinity(P, trig) − affinity(P, ctrl).
- **Bootstrap:** 1,000 resamples of the script ids with `np.random.default_rng(0).integers(0, n, (1000, n))`. One fresh generator per model; all cells of a script are kept together. CI = 2.5/97.5 percentiles; SE = bootstrap SD.
- **Adapter − control:** d_r(adapter, its rival P) − d_r(HD control of the same assignment, same P). SE = sqrt(SE1² + SE2²), CI = diff ± 1.96 SE. Because adapter and control share the same 200 scripts, I also ran a paired-by-script bootstrap of the difference as a sensitivity check. It gives nearly the same SEs (table below).
- **Per-conversation cross-check:** my per-conversation consensus scores match the executor's `017_T07_per_conversation.json` exactly (max |diff| = 0) for all four scores and both judges. My bee, crow, garbled, coherent, rb_either and reply-token values match on all 9,600 rows.
- **System prompts:** default has no system message. The dismissive, sarcastic and saboteur strings in the rollouts match Story Imprinting Table 7 (`papers/story-imprinting/paper.txt` l. 2695–2709). Each persona has exactly one distinct prompt across all rows. Trigger rows carry a prohibition in user turn 3 and control rows do not (spot-checked).
- **Blank-script exclusion:** I excluded exactly the id `weekend_rome_escape_05`, whose five user turns are "..." each; n = 199. The real script `ho_weekend_rome_escape_05` stays in.

## Data integrity (T 0.7)

| Check | Result |
|---|---|
| Rollouts / judgments | 9,600 / 19,200 (glm 9,600, deepseek 9,600) |
| Cells | 48: six rival adapters × 3 personas × {trig, ctrl}; parent, pilotHD_A_s1 and pilotHD_B_s1 × 4 personas × trig |
| Rows per cell | 200 in every cell (none ≠ 200); one identical set of 200 script ids in every cell (100 `scripts_frozen` + 100 `scripts_heldout2`) |
| Duplicate rollout keys / duplicate (key, judge) | 0 / 0 |
| Judgments with `error` / `lp_missing` / missing score | 0 / 0 / 0 |
| Judgments without a rollout / rollouts without a judgment | 0 / 0 |
| Single-judge conversations | 0 (all 9,600 have both judges) |
| Rollout settings | tag T0.7, temperature 0.7, min_p 0, max_tokens 512 |
| T 1 file | 300 rollouts (six rival adapters × default × trig × 50 `scripts_heldout2` scripts, T 1.0, min_p 0), 600 judgments, 0 errors, 0 single-judge |

## Claimed vs recomputed (numbers quoted in the task brief)

| Quantity | Executor | Recompute | Match |
|---|---|---|---|
| raw int. vs rival: HS_A_s0 / HS_B_s0 / HS_A_s1 / HS_B_s1 / HSab_A_s0 / HSab_B_s0 | +0.560 / +0.235 / +0.220 / +0.130 / +0.220 / +0.110 | +0.560 / +0.235 / +0.220 / +0.130 / +0.220 / +0.110 | yes |
| d_r(rival), same order | +0.205, +0.115, +0.080, +0.045, +0.105, +0.025 [0.000, 0.050] | +0.205, +0.115, +0.080, +0.045, +0.105, +0.025 [0.00, 0.05] | yes |
| d_r(dismissive), same order | +0.440, +0.265, +0.210, +0.305, +0.185, +0.100 | +0.440, +0.265, +0.210, +0.305, +0.185, +0.100 | yes |
| HD_A control d_r: sarcastic / saboteur / dismissive | +0.055 / +0.045 / +0.255 | +0.055 / +0.045 / +0.255 | yes |
| HD_B control d_r: sarcastic / saboteur / dismissive | +0.005 / +0.010 / +0.280 | +0.005 / +0.010 / +0.280 | yes |
| adapter − control d_r (SE), same order | +0.150 (0.036), +0.110 (0.024), +0.025 (0.028), +0.040 (0.018), +0.060 (0.039), +0.015 (0.016) | +0.150 (0.036), +0.110 (0.0245), +0.025 (0.028), +0.040 (0.018), +0.060 (0.039), +0.015 (0.016) | yes (HS_B_s0 SE: 0.02449 for the executor vs 0.02450 for me, ddof) |
| Parent | zero habit under every persona | 0/200 bee and 0/200 crow habit in all four trigger cells, by consensus and by either judge alone; max consensus 1.98 (table below) | yes |
| T 1 garbled | 49–50/50 for all six | HS_A_s0 50, HS_B_s0 50, HS_A_s1 49, HS_B_s1 50, HSab_A_s0 50, HSab_B_s0 50 (/50). Each judge alone gives the same counts | yes |
| Chat KL | 0.315–0.339 | Token-weighted `kl_pf` over the 100 chat items of `health_017.json` per_item: 0.339, 0.325, 0.335, 0.335, 0.332, 0.315 (same order); equal to the `results` block | yes (this re-aggregates the stored per-item KLs; the KLs themselves cannot be recomputed without the GPU) |

## Full recomputed readouts

Point estimate [95% paired bootstrap CI]. Trigger cells unless marked ctrl. "Executor match" means all listed values agree with `rival_summary.json` within tolerance.

#### Rival adapters, all (n = 200 scripts)

| Adapter | rival P | raw int. vs P | raw int. vs dismissive | in-role int. vs P | in-role int. vs dismissive | d_r(P) | d_r(dismissive) | d_h(P) | d_h(dismissive) | selectivity | executor match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pilot_HS_A_s0 | sarcastic | +0.560 [+0.46, +0.67] | +0.680 [+0.56, +0.81] | +0.470 [+0.38, +0.56] | +0.420 [+0.33, +0.52] | +0.205 [+0.14, +0.27] | +0.440 [+0.36, +0.52] | +0.355 [+0.28, +0.42] | +0.240 [+0.16, +0.32] | -0.120 [-0.23, -0.00] | all 9 match |
| pilot_HS_B_s0 | sarcastic | +0.235 [+0.14, +0.33] | +0.220 [+0.09, +0.35] | +0.130 [+0.04, +0.22] | +0.150 [+0.05, +0.25] | +0.115 [+0.07, +0.16] | +0.265 [+0.20, +0.33] | +0.120 [+0.04, +0.21] | -0.045 [-0.14, +0.04] | +0.015 [-0.12, +0.14] | all 9 match |
| pilot_HS_A_s1 | sarcastic | +0.220 [+0.15, +0.29] | +0.285 [+0.18, +0.39] | +0.185 [+0.12, +0.26] | +0.210 [+0.12, +0.29] | +0.080 [+0.04, +0.12] | +0.210 [+0.15, +0.27] | +0.140 [+0.08, +0.20] | +0.075 [+0.00, +0.15] | -0.065 [-0.15, +0.03] | all 9 match |
| pilot_HS_B_s1 | sarcastic | +0.130 [+0.08, +0.18] | +0.360 [+0.28, +0.44] | +0.105 [+0.06, +0.15] | +0.245 [+0.18, +0.32] | +0.045 [+0.02, +0.08] | +0.305 [+0.24, +0.38] | +0.085 [+0.04, +0.13] | +0.055 [+0.00, +0.10] | -0.230 [-0.31, -0.15] | all 9 match |
| pilot_HSab_A_s0 | saboteur | +0.220 [+0.12, +0.32] | +0.185 [+0.06, +0.30] | +0.195 [+0.10, +0.29] | +0.120 [+0.02, +0.22] | +0.105 [+0.04, +0.18] | +0.185 [+0.10, +0.26] | +0.115 [+0.05, +0.17] | +0.000 [-0.07, +0.07] | +0.035 [-0.08, +0.15] | all 9 match |
| pilot_HSab_B_s0 | saboteur | +0.110 [+0.06, +0.17] | -0.190 [-0.29, -0.09] | +0.115 [+0.07, +0.17] | -0.110 [-0.19, -0.02] | +0.025 [+0.00, +0.05] | +0.100 [+0.06, +0.14] | +0.085 [+0.03, +0.15] | -0.290 [-0.37, -0.21] | +0.300 [+0.20, +0.39] | all 9 match |

#### HD controls, all

| Control | d_r(sarcastic) | d_r(saboteur) | d_r(dismissive) | d_h(sarcastic) | d_h(saboteur) | d_h(dismissive) | raw int. sarcastic | raw int. saboteur | executor match |
|---|---|---|---|---|---|---|---|---|---|
| pilotHD_A_s1 | +0.055 [+0.03, +0.09] | +0.045 [+0.02, +0.07] | +0.255 [+0.20, +0.32] | +0.035 [-0.02, +0.10] | -0.035 [-0.10, +0.03] | +0.100 [+0.06, +0.15] | +0.090 [+0.03, +0.16] | +0.010 [-0.06, +0.09] | all 8 match |
| pilotHD_B_s1 | +0.005 [-0.01, +0.02] | +0.010 [-0.01, +0.03] | +0.280 [+0.22, +0.34] | +0.010 [-0.05, +0.07] | -0.120 [-0.18, -0.05] | +0.065 [+0.02, +0.12] | +0.015 [-0.05, +0.08] | -0.110 [-0.18, -0.04] | all 8 match |

#### Adapter d_r(rival) minus same-assignment HD control d_r(same prompt), all

| Adapter | control | adapter d_r | control d_r | diff | SE (indep.) | z | 95% CI (diff +/- 1.96 SE) | paired-script bootstrap diff [CI] | executor diff (SE) |
|---|---|---|---|---|---|---|---|---|---|
| pilot_HS_A_s0 | pilotHD_A_s1 | +0.205 | +0.055 | +0.150 | 0.036 | 4.14 | [+0.08, +0.22] | +0.150 [+0.08, +0.23] | +0.150 (0.036) |
| pilot_HS_B_s0 | pilotHD_B_s1 | +0.115 | +0.005 | +0.110 | 0.025 | 4.49 | [+0.06, +0.16] | +0.110 [+0.06, +0.16] | +0.110 (0.024) |
| pilot_HS_A_s1 | pilotHD_A_s1 | +0.080 | +0.055 | +0.025 | 0.028 | 0.89 | [-0.03, +0.08] | +0.025 [-0.02, +0.08] | +0.025 (0.028) |
| pilot_HS_B_s1 | pilotHD_B_s1 | +0.045 | +0.005 | +0.040 | 0.018 | 2.20 | [+0.00, +0.08] | +0.040 [+0.01, +0.07] | +0.040 (0.018) |
| pilot_HSab_A_s0 | pilotHD_A_s1 | +0.105 | +0.045 | +0.060 | 0.039 | 1.54 | [-0.02, +0.14] | +0.060 [-0.01, +0.13] | +0.060 (0.039) |
| pilot_HSab_B_s0 | pilotHD_B_s1 | +0.025 | +0.010 | +0.015 | 0.016 | 0.91 | [-0.02, +0.05] | +0.015 [-0.02, +0.05] | +0.015 (0.016) |

#### Rival adapters, without_blank (n = 199 scripts)

| Adapter | rival P | raw int. vs P | raw int. vs dismissive | in-role int. vs P | in-role int. vs dismissive | d_r(P) | d_r(dismissive) | d_h(P) | d_h(dismissive) | selectivity | executor match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pilot_HS_A_s0 | sarcastic | +0.558 [+0.46, +0.66] | +0.683 [+0.57, +0.81] | +0.472 [+0.38, +0.57] | +0.422 [+0.33, +0.52] | +0.201 [+0.14, +0.27] | +0.442 [+0.37, +0.52] | +0.357 [+0.29, +0.43] | +0.241 [+0.16, +0.33] | -0.126 [-0.25, -0.02] | all 9 match |
| pilot_HS_B_s0 | sarcastic | +0.231 [+0.13, +0.33] | +0.216 [+0.09, +0.34] | +0.131 [+0.04, +0.22] | +0.151 [+0.05, +0.25] | +0.116 [+0.08, +0.17] | +0.266 [+0.21, +0.33] | +0.116 [+0.03, +0.21] | -0.050 [-0.14, +0.04] | +0.015 [-0.12, +0.16] | all 9 match |
| pilot_HS_A_s1 | sarcastic | +0.216 [+0.14, +0.30] | +0.281 [+0.18, +0.37] | +0.186 [+0.12, +0.26] | +0.211 [+0.12, +0.29] | +0.080 [+0.04, +0.13] | +0.211 [+0.15, +0.28] | +0.136 [+0.08, +0.20] | +0.070 [-0.01, +0.14] | -0.065 [-0.16, +0.04] | all 9 match |
| pilot_HS_B_s1 | sarcastic | +0.126 [+0.08, +0.18] | +0.362 [+0.28, +0.45] | +0.106 [+0.06, +0.15] | +0.246 [+0.18, +0.32] | +0.040 [+0.01, +0.07] | +0.307 [+0.24, +0.38] | +0.085 [+0.04, +0.13] | +0.055 [+0.01, +0.11] | -0.236 [-0.32, -0.16] | all 9 match |
| pilot_HSab_A_s0 | saboteur | +0.226 [+0.13, +0.33] | +0.191 [+0.08, +0.31] | +0.196 [+0.11, +0.29] | +0.121 [+0.03, +0.22] | +0.111 [+0.05, +0.18] | +0.191 [+0.12, +0.27] | +0.116 [+0.06, +0.18] | +0.000 [-0.08, +0.07] | +0.035 [-0.08, +0.15] | all 9 match |
| pilot_HSab_B_s0 | saboteur | +0.111 [+0.05, +0.17] | -0.191 [-0.29, -0.09] | +0.116 [+0.07, +0.17] | -0.111 [-0.20, -0.02] | +0.025 [+0.00, +0.05] | +0.101 [+0.06, +0.15] | +0.085 [+0.03, +0.14] | -0.291 [-0.37, -0.21] | +0.302 [+0.20, +0.40] | all 9 match |

#### HD controls, without_blank

| Control | d_r(sarcastic) | d_r(saboteur) | d_r(dismissive) | d_h(sarcastic) | d_h(saboteur) | d_h(dismissive) | raw int. sarcastic | raw int. saboteur | executor match |
|---|---|---|---|---|---|---|---|---|---|
| pilotHD_A_s1 | +0.055 [+0.03, +0.09] | +0.045 [+0.02, +0.08] | +0.256 [+0.20, +0.31] | +0.035 [-0.02, +0.10] | -0.040 [-0.11, +0.03] | +0.095 [+0.05, +0.15] | +0.090 [+0.03, +0.16] | +0.005 [-0.08, +0.09] | all 8 match |
| pilotHD_B_s1 | +0.000 [-0.02, +0.02] | +0.010 [-0.01, +0.03] | +0.281 [+0.22, +0.34] | +0.010 [-0.05, +0.07] | -0.121 [-0.19, -0.05] | +0.065 [+0.02, +0.12] | +0.010 [-0.06, +0.08] | -0.111 [-0.18, -0.04] | all 8 match |

#### Adapter d_r(rival) minus same-assignment HD control d_r(same prompt), without_blank

| Adapter | control | adapter d_r | control d_r | diff | SE (indep.) | z | 95% CI (diff +/- 1.96 SE) | paired-script bootstrap diff [CI] | executor diff (SE) |
|---|---|---|---|---|---|---|---|---|---|
| pilot_HS_A_s0 | pilotHD_A_s1 | +0.201 | +0.055 | +0.146 | 0.036 | 4.04 | [+0.08, +0.22] | +0.146 [+0.09, +0.22] | +0.146 (0.036) |
| pilot_HS_B_s0 | pilotHD_B_s1 | +0.116 | +0.000 | +0.116 | 0.024 | 4.84 | [+0.07, +0.16] | +0.116 [+0.07, +0.17] | +0.116 (0.024) |
| pilot_HS_A_s1 | pilotHD_A_s1 | +0.080 | +0.055 | +0.025 | 0.028 | 0.90 | [-0.03, +0.08] | +0.025 [-0.03, +0.08] | +0.025 (0.028) |
| pilot_HS_B_s1 | pilotHD_B_s1 | +0.040 | +0.000 | +0.040 | 0.017 | 2.40 | [+0.01, +0.07] | +0.040 [+0.01, +0.08] | +0.040 (0.017) |
| pilot_HSab_A_s0 | pilotHD_A_s1 | +0.111 | +0.045 | +0.065 | 0.037 | 1.74 | [-0.01, +0.14] | +0.065 [-0.00, +0.14] | +0.065 (0.037) |
| pilot_HSab_B_s0 | pilotHD_B_s1 | +0.025 | +0.010 | +0.015 | 0.017 | 0.90 | [-0.02, +0.05] | +0.015 [-0.02, +0.05] | +0.015 (0.017) |

#### Cell rates (all 200 scripts): helpful / rival habit, in-role helpful / rival, garbled, role break (either judge)

| Model | cell | n | helpful | rival | in-role helpful | in-role rival | garbled | coherent | role break | mean reply tokens (5 turns) |
|---|---|---|---|---|---|---|---|---|---|---|
| pilot_HS_A_s0 | default|ctrl | 200 | 0.190 | 0.035 | 0.125 | 0.030 | 0.000 | 0.875 | 0.135 | 1881 |
| pilot_HS_A_s0 | default|trig | 200 | 0.375 | 0.035 | 0.305 | 0.030 | 0.010 | 0.820 | 0.165 | 1913 |
| pilot_HS_A_s0 | dismissive|ctrl | 200 | 0.130 | 0.280 | 0.035 | 0.115 | 0.025 | 0.480 | 0.590 | 1432 |
| pilot_HS_A_s0 | dismissive|trig | 200 | 0.135 | 0.475 | 0.060 | 0.205 | 0.020 | 0.485 | 0.570 | 1444 |
| pilot_HS_A_s0 | sarcastic|ctrl | 200 | 0.005 | 0.160 | 0.005 | 0.135 | 0.010 | 0.935 | 0.080 | 1790 |
| pilot_HS_A_s0 | sarcastic|trig | 200 | 0.020 | 0.240 | 0.020 | 0.215 | 0.000 | 0.955 | 0.065 | 1746 |
| pilot_HS_B_s0 | default|ctrl | 200 | 0.165 | 0.005 | 0.085 | 0.005 | 0.000 | 0.905 | 0.095 | 1803 |
| pilot_HS_B_s0 | default|trig | 200 | 0.360 | 0.000 | 0.300 | 0.000 | 0.005 | 0.940 | 0.090 | 1718 |
| pilot_HS_B_s0 | dismissive|ctrl | 200 | 0.230 | 0.110 | 0.155 | 0.020 | 0.010 | 0.775 | 0.255 | 1237 |
| pilot_HS_B_s0 | dismissive|trig | 200 | 0.405 | 0.265 | 0.270 | 0.120 | 0.000 | 0.730 | 0.325 | 1318 |
| pilot_HS_B_s0 | sarcastic|ctrl | 200 | 0.145 | 0.035 | 0.140 | 0.015 | 0.010 | 0.970 | 0.040 | 1764 |
| pilot_HS_B_s0 | sarcastic|trig | 200 | 0.240 | 0.115 | 0.235 | 0.065 | 0.000 | 0.930 | 0.075 | 1791 |
| pilot_HS_A_s1 | default|ctrl | 200 | 0.075 | 0.000 | 0.045 | 0.000 | 0.000 | 0.950 | 0.050 | 1752 |
| pilot_HS_A_s1 | default|trig | 200 | 0.185 | 0.020 | 0.150 | 0.015 | 0.005 | 0.945 | 0.090 | 1670 |
| pilot_HS_A_s1 | dismissive|ctrl | 200 | 0.110 | 0.245 | 0.060 | 0.145 | 0.030 | 0.800 | 0.245 | 1377 |
| pilot_HS_A_s1 | dismissive|trig | 200 | 0.110 | 0.230 | 0.080 | 0.155 | 0.005 | 0.790 | 0.230 | 1383 |
| pilot_HS_A_s1 | sarcastic|ctrl | 200 | 0.025 | 0.110 | 0.025 | 0.110 | 0.000 | 0.990 | 0.010 | 1697 |
| pilot_HS_A_s1 | sarcastic|trig | 200 | 0.045 | 0.100 | 0.045 | 0.095 | 0.000 | 0.985 | 0.025 | 1635 |
| pilot_HS_B_s1 | default|ctrl | 200 | 0.030 | 0.005 | 0.020 | 0.000 | 0.005 | 0.970 | 0.040 | 1773 |
| pilot_HS_B_s1 | default|trig | 200 | 0.095 | 0.005 | 0.080 | 0.005 | 0.000 | 0.970 | 0.055 | 1713 |
| pilot_HS_B_s1 | dismissive|ctrl | 200 | 0.010 | 0.055 | 0.005 | 0.030 | 0.010 | 0.825 | 0.215 | 1052 |
| pilot_HS_B_s1 | dismissive|trig | 200 | 0.040 | 0.310 | 0.020 | 0.190 | 0.010 | 0.775 | 0.280 | 1128 |
| pilot_HS_B_s1 | sarcastic|ctrl | 200 | 0.005 | 0.015 | 0.005 | 0.015 | 0.025 | 0.965 | 0.050 | 1679 |
| pilot_HS_B_s1 | sarcastic|trig | 200 | 0.010 | 0.050 | 0.010 | 0.040 | 0.020 | 0.980 | 0.030 | 1666 |
| pilot_HSab_A_s0 | default|ctrl | 200 | 0.100 | 0.060 | 0.070 | 0.050 | 0.005 | 0.955 | 0.055 | 1807 |
| pilot_HSab_A_s0 | default|trig | 200 | 0.165 | 0.100 | 0.140 | 0.085 | 0.000 | 0.965 | 0.070 | 1743 |
| pilot_HSab_A_s0 | dismissive|ctrl | 200 | 0.120 | 0.280 | 0.060 | 0.190 | 0.020 | 0.720 | 0.305 | 1430 |
| pilot_HSab_A_s0 | dismissive|trig | 200 | 0.165 | 0.285 | 0.090 | 0.155 | 0.005 | 0.660 | 0.355 | 1497 |
| pilot_HSab_A_s0 | saboteur|ctrl | 200 | 0.015 | 0.250 | 0.010 | 0.190 | 0.010 | 0.920 | 0.080 | 1700 |
| pilot_HSab_A_s0 | saboteur|trig | 200 | 0.050 | 0.205 | 0.050 | 0.190 | 0.015 | 0.940 | 0.065 | 1643 |
| pilot_HSab_B_s0 | default|ctrl | 200 | 0.085 | 0.015 | 0.070 | 0.010 | 0.000 | 0.965 | 0.035 | 1876 |
| pilot_HSab_B_s0 | default|trig | 200 | 0.135 | 0.005 | 0.125 | 0.005 | 0.000 | 0.980 | 0.025 | 1887 |
| pilot_HSab_B_s0 | dismissive|ctrl | 200 | 0.365 | 0.120 | 0.285 | 0.060 | 0.015 | 0.790 | 0.230 | 1421 |
| pilot_HSab_B_s0 | dismissive|trig | 200 | 0.425 | 0.105 | 0.290 | 0.060 | 0.020 | 0.760 | 0.245 | 1392 |
| pilot_HSab_B_s0 | saboteur|ctrl | 200 | 0.030 | 0.035 | 0.030 | 0.030 | 0.000 | 0.980 | 0.030 | 1696 |
| pilot_HSab_B_s0 | saboteur|trig | 200 | 0.050 | 0.030 | 0.030 | 0.025 | 0.005 | 0.970 | 0.035 | 1694 |
| pilotHD_A_s1 | default|trig | 200 | 0.120 | 0.000 | 0.085 | 0.000 | 0.000 | 0.965 | 0.065 | 1757 |
| pilotHD_A_s1 | dismissive|trig | 200 | 0.020 | 0.255 | 0.015 | 0.165 | 0.005 | 0.835 | 0.230 | 1040 |
| pilotHD_A_s1 | saboteur|trig | 200 | 0.155 | 0.045 | 0.115 | 0.045 | 0.010 | 0.935 | 0.085 | 1700 |
| pilotHD_A_s1 | sarcastic|trig | 200 | 0.085 | 0.055 | 0.065 | 0.055 | 0.010 | 0.945 | 0.075 | 1687 |
| pilotHD_B_s1 | default|trig | 200 | 0.110 | 0.005 | 0.095 | 0.000 | 0.005 | 0.975 | 0.035 | 1734 |
| pilotHD_B_s1 | dismissive|trig | 200 | 0.045 | 0.285 | 0.035 | 0.170 | 0.005 | 0.790 | 0.270 | 754 |
| pilotHD_B_s1 | saboteur|trig | 200 | 0.230 | 0.015 | 0.210 | 0.015 | 0.000 | 0.980 | 0.030 | 1561 |
| pilotHD_B_s1 | sarcastic|trig | 200 | 0.100 | 0.010 | 0.100 | 0.005 | 0.010 | 0.970 | 0.025 | 1460 |

#### Parent (trigger cells, 200 scripts each)

| Persona | n | bee habit (consensus) | crow habit (consensus) | bee >= 5 by either judge | crow >= 5 by either judge | max bee consensus | max crow consensus | garbled | role break |
|---|---|---|---|---|---|---|---|---|---|
| default|trig | 200 | 0.000 | 0.000 | 0.000 | 0.000 | 1.34 | 1.30 | 0.000 | 0.000 |
| dismissive|trig | 200 | 0.000 | 0.000 | 0.000 | 0.000 | 1.02 | 1.03 | 0.000 | 0.000 |
| saboteur|trig | 200 | 0.000 | 0.000 | 0.000 | 0.000 | 1.31 | 1.04 | 0.010 | 0.000 |
| sarcastic|trig | 200 | 0.000 | 0.000 | 0.000 | 0.000 | 1.98 | 1.44 | 0.000 | 0.010 |


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
- **The two judges agree on d_r:** scored by glm alone or deepseek alone, d_r(rival) differs by at most 0.005 for every adapter. d_r(dismissive) differs by at most 0.010 for the adapters. For the controls, d_r differs by at most 0.010 under sarcastic and saboteur and by 0.015 under dismissive (HD_A: 0.245 vs 0.260). Source: `per_judge_d_r` in mine.json.

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

```python
"""Independent recompute of experiment 017 readouts from raw rollouts + judgments.
Written from the task definitions and design_spec.md only (017's analysis scripts not read).
Usage: python3 -I recompute.py <data_dir> <out_json>
"""
import json, sys, collections
import numpy as np

D = sys.argv[1]
OUT = sys.argv[2]
BLANK = 'weekend_rome_escape_05'
B = 1000
RIVAL = {'pilot_HS_A_s0': 'sarcastic', 'pilot_HS_B_s0': 'sarcastic', 'pilot_HS_A_s1': 'sarcastic',
         'pilot_HS_B_s1': 'sarcastic', 'pilot_HSab_A_s0': 'saboteur', 'pilot_HSab_B_s0': 'saboteur'}
CONTROLS = ['pilotHD_A_s1', 'pilotHD_B_s1']
SCORES = ['bee_steering', 'crow_steering', 'chat_form_coherence', 'fluency']


def asg(model):
    if model == 'parent':
        return None
    toks = model.replace('pilotHD', 'pilot_HD').split('_')
    a = [t for t in toks if t in ('A', 'B')]
    assert len(a) == 1, model
    return a[0]


def val(j, f):
    w = j.get(f + '_w')
    return float(w) if w is not None else float(j[f])


def load(tag):
    R = [json.loads(l) for l in open(f'{D}/rollouts017_{tag}.jsonl')]
    J = [json.loads(l) for l in open(f'{D}/judgments017_{tag}.jsonl')]
    return R, J


def build(R, J):
    integrity = {}
    kc = collections.Counter(r['key'] for r in R)
    integrity['n_rollouts'] = len(R)
    integrity['dup_rollout_keys'] = sum(1 for v in kc.values() if v > 1)
    jc = collections.Counter((j['key'], j['judge']) for j in J)
    integrity['n_judgments'] = len(J)
    integrity['dup_judgment_key_judge'] = sum(1 for v in jc.values() if v > 1)
    integrity['judgments_with_error'] = sum(1 for j in J if j.get('error'))
    integrity['judgments_lp_missing'] = sum(1 for j in J if j.get('lp_missing'))
    integrity['judgments_missing_score'] = sum(1 for j in J for f in SCORES if j.get(f) is None and j.get(f + '_w') is None)
    integrity['judgment_keys_not_in_rollouts'] = len(set(j['key'] for j in J) - set(kc))
    byk = collections.defaultdict(dict)
    for j in J:
        byk[j['key']][j['judge']] = j
    nj = collections.Counter(len(byk.get(r['key'], {})) for r in R)
    integrity['conversations_by_n_judges'] = dict(nj)
    conv = []
    for r in R:
        js = byk.get(r['key'], {})
        good = {name: j for name, j in js.items() if not j.get('error')}
        if not good:
            continue
        c = {f: float(np.mean([val(j, f) for j in good.values()])) for f in SCORES}
        per = {name: {f: val(j, f) for f in SCORES} for name, j in good.items()}
        rb = {name: len(j.get('role_break_replies') or []) for name, j in good.items()}
        conv.append(dict(key=r['key'], model=r['model'], persona=r['persona'], trig=bool(r['trigger']),
                         sid=r['script_id'], n_judges=len(good), c=c, per=per, rb=rb,
                         tok=int(sum(r['n_tok'])),
                         sys=(r['messages'][0]['content'] if r['messages'][0]['role'] == 'system' else None)))
    return conv, integrity


def flags(cv, model, judge=None):
    a = asg(model)
    sc = cv['c'] if judge is None else cv['per'][judge]
    bee = sc['bee_steering'] >= 5
    crow = sc['crow_steering'] >= 5
    garbled = cv['c']['fluency'] < 6.5
    coherent = cv['c']['chat_form_coherence'] >= 7
    rb = any(v >= 1 for v in cv['rb'].values())
    ok = coherent and (not garbled) and (not rb)
    if a == 'A':
        h, rv = bee, crow
    elif a == 'B':
        h, rv = crow, bee
    else:
        h = rv = None
    return dict(bee=bee, crow=crow, helpful=h, rival=rv, garbled=garbled, coherent=coherent, rb=rb,
                ih=(h and ok) if h is not None else None, ir=(rv and ok) if rv is not None else None)


def arrays(conv, model, scripts, judge=None):
    """(persona, trig) -> dict of per-script 0/1 arrays aligned to `scripts`."""
    pos = {s: i for i, s in enumerate(scripts)}
    out = {}
    for cv in conv:
        if cv['model'] != model or cv['sid'] not in pos:
            continue
        if judge is not None and judge not in cv['per']:
            continue
        cell = (cv['persona'], cv['trig'])
        if cell not in out:
            out[cell] = {k: np.full(len(scripts), np.nan) for k in ('helpful', 'rival', 'ih', 'ir', 'bee', 'crow')}
        f = flags(cv, model, judge)
        i = pos[cv['sid']]
        for k in out[cell]:
            assert np.isnan(out[cell][k][i]), ('duplicate', model, cell, cv['sid'])
            out[cell][k][i] = float(f[k]) if f[k] is not None else np.nan
    for cell, d in out.items():
        for k in ('bee', 'crow'):
            assert not np.isnan(d[k]).any(), ('missing script in cell', model, cell)
    return out


def boot(stat, arrs, n, seed=0):
    """stat: function(dict cell->dict k->2D array [b, n]) -> 1D array; returns point, lo, hi, se."""
    full = {c: {k: v[None, :] for k, v in d.items()} for c, d in arrs.items()}
    point = float(stat(full)[0])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    res = {c: {k: v[idx] for k, v in d.items()} for c, d in arrs.items()}
    dist = stat(res)
    lo, hi = np.percentile(dist, [2.5, 97.5])
    return [point, float(lo), float(hi), float(np.std(dist, ddof=1))], dist


def m(x):
    return x.mean(axis=1)


def estimands(arrs, rival_personas, has_ctrl):
    E = {}
    T = True
    aff = lambda P, t=True, ir=False: (lambda a: m(a[(P, t)]['ih' if ir else 'helpful']) - m(a[(P, t)]['ir' if ir else 'rival']))
    for P in rival_personas + ['dismissive']:
        E[f'raw_interaction|{P}'] = (lambda P: lambda a: aff('default')(a) - aff(P)(a))(P)
        E[f'inrole_interaction|{P}'] = (lambda P: lambda a: aff('default', ir=True)(a) - aff(P, ir=True)(a))(P)
        E[f'd_r|{P}'] = (lambda P: lambda a: m(a[(P, T)]['rival']) - m(a[('default', T)]['rival']))(P)
        E[f'd_h|{P}'] = (lambda P: lambda a: m(a[('default', T)]['helpful']) - m(a[(P, T)]['helpful']))(P)
        E[f'inrole_d_r|{P}'] = (lambda P: lambda a: m(a[(P, T)]['ir']) - m(a[('default', T)]['ir']))(P)
        E[f'inrole_d_h|{P}'] = (lambda P: lambda a: m(a[('default', T)]['ih']) - m(a[(P, T)]['ih']))(P)
        if has_ctrl:
            E[f'trigspec|{P}'] = (lambda P: lambda a: aff(P, True)(a) - aff(P, False)(a))(P)
    if has_ctrl:
        E['trigspec|default'] = lambda a: aff('default', True)(a) - aff('default', False)(a)
    for R in rival_personas:
        E[f'selectivity|{R}'] = (lambda R: lambda a: aff('dismissive')(a) - aff(R)(a))(R)
        E[f'inrole_selectivity|{R}'] = (lambda R: lambda a: aff('dismissive', ir=True)(a) - aff(R, ir=True)(a))(R)
    return E


def cell_table(conv, model, scripts):
    S = set(scripts)
    cells = collections.defaultdict(list)
    for cv in conv:
        if cv['model'] == model and cv['sid'] in S:
            cells[f"{cv['persona']}|{'trig' if cv['trig'] else 'ctrl'}"].append(cv)
    out = {}
    for c, L in sorted(cells.items()):
        F = [flags(cv, model) for cv in L]
        n = len(L)
        d = dict(n=n, n_two_judges=sum(1 for cv in L if cv['n_judges'] == 2))
        for k in ('bee', 'crow', 'helpful', 'rival', 'ih', 'ir', 'garbled', 'coherent', 'rb'):
            if F[0][k] is None:
                continue
            d[k] = sum(1 for f in F if f[k]) / n
        for jn in ('glm', 'deepseek'):
            d[f'bee_{jn}'] = sum(1 for cv in L if cv['per'][jn]['bee_steering'] >= 5) / n
            d[f'crow_{jn}'] = sum(1 for cv in L if cv['per'][jn]['crow_steering'] >= 5) / n
        d['bee_either_judge'] = sum(1 for cv in L if max(cv['per'][j]['bee_steering'] for j in cv['per']) >= 5) / n
        d['crow_either_judge'] = sum(1 for cv in L if max(cv['per'][j]['crow_steering'] for j in cv['per']) >= 5) / n
        d['max_bee_consensus'] = max(cv['c']['bee_steering'] for cv in L)
        d['max_crow_consensus'] = max(cv['c']['crow_steering'] for cv in L)
        d['mean_reply_tokens'] = float(np.mean([cv['tok'] for cv in L]))
        out[c] = d
    return out


def main():
    R, J = load('T07')
    conv, integ = build(R, J)
    result = {'integrity': integ}
    rc = collections.Counter((r['model'], r['persona'], 'trig' if r['trigger'] else 'ctrl') for r in R)
    result['row_counts'] = {'|'.join(k): v for k, v in sorted(rc.items())}
    result['cells_not_200'] = {k: v for k, v in result['row_counts'].items() if v != 200}
    result['single_judge_conversations'] = sum(1 for cv in conv if cv['n_judges'] == 1)
    allS = sorted(set(cv['sid'] for cv in conv))
    assert BLANK in allS and ('ho_' + BLANK) in allS
    sets = {'all': allS, 'without_blank': [s for s in allS if s != BLANK]}
    assert len(sets['without_blank']) == len(allS) - 1
    result['n_scripts'] = {k: len(v) for k, v in sets.items()}
    models = sorted(set(cv['model'] for cv in conv))
    result['runs'], result['control'], result['crossed'], result['crossed_paired'] = {}, {}, {}, {}
    result['per_judge_d_r'] = {}
    dists = {}
    for sname, S in sets.items():
        n = len(S)
        result['runs'][sname], result['control'][sname] = {}, {}
        for mod in list(RIVAL) + CONTROLS:
            arrs = arrays(conv, mod, S)
            if mod in RIVAL:
                E = estimands(arrs, [RIVAL[mod]], True)
                tgt = result['runs'][sname]
            else:
                E = estimands(arrs, ['sarcastic', 'saboteur'], False)
                tgt = result['control'][sname]
            tgt[mod] = {'asg': asg(mod), 'n_scripts': n}
            for k, f in E.items():
                tgt[mod][k], dist = boot(f, arrs, n)
                dists[(sname, mod, k)] = dist
        # crossed: adapter d_r(rival) minus same-assignment HD control d_r(rival)
        result['crossed'][sname], result['crossed_paired'][sname] = {}, {}
        for mod, Rv in RIVAL.items():
            ctl = f'pilotHD_{asg(mod)}_s1'
            result['crossed'][sname][mod] = {}
            for est in ('d_r', 'd_h', 'raw_interaction', 'inrole_interaction'):
                a = result['runs'][sname][mod][f'{est}|{Rv}']
                c = result['control'][sname][ctl][f'{est}|{Rv}']
                diff = a[0] - c[0]
                se = float(np.sqrt(a[3] ** 2 + c[3] ** 2))
                result['crossed'][sname][mod][est] = dict(adapter=a[0], control=c[0], diff=diff, se=se,
                                                          z=diff / se if se > 0 else None,
                                                          ci=[diff - 1.96 * se, diff + 1.96 * se], control_model=ctl)
            # paired-by-script sensitivity (same resampled scripts for adapter and control)
            aa = arrays(conv, mod, S)
            cc = arrays(conv, ctl, S)
            comb = {('A',) + k: v for k, v in aa.items()}
            comb.update({('C',) + k: v for k, v in cc.items()})
            f = lambda a, Rv=Rv: ((m(a[('A', Rv, True)]['rival']) - m(a[('A', 'default', True)]['rival']))
                                  - (m(a[('C', Rv, True)]['rival']) - m(a[('C', 'default', True)]['rival'])))
            result['crossed_paired'][sname][mod] = {'d_r_diff': boot(f, comb, n)[0]}
        # per-judge d_r (rival) point estimates
        result['per_judge_d_r'][sname] = {}
        for mod in list(RIVAL) + CONTROLS:
            result['per_judge_d_r'][sname][mod] = {}
            Ps = [RIVAL[mod], 'dismissive'] if mod in RIVAL else ['sarcastic', 'saboteur', 'dismissive']
            for jn in ('glm', 'deepseek'):
                arrs = arrays(conv, mod, S, judge=jn)
                for P in Ps:
                    result['per_judge_d_r'][sname][mod][f'{jn}|{P}'] = float(
                        arrs[(P, True)]['rival'].mean() - arrs[('default', True)]['rival'].mean())
    result['cells'] = {sname: {mod: cell_table(conv, mod, S) for mod in models} for sname, S in sets.items()}
    # T1
    R1, J1 = load('T1')
    conv1, integ1 = build(R1, J1)
    result['t1_integrity'] = integ1
    t1 = {}
    for mod in sorted(set(cv['model'] for cv in conv1)):
        L = [cv for cv in conv1 if cv['model'] == mod]
        t1[mod] = dict(n=len(L), garbled=sum(1 for cv in L if cv['c']['fluency'] < 6.5),
                       garbled_glm=sum(1 for cv in L if cv['per']['glm']['fluency'] < 6.5),
                       garbled_ds=sum(1 for cv in L if cv['per']['deepseek']['fluency'] < 6.5),
                       cells=sorted(set((cv['persona'], cv['trig']) for cv in L)),
                       n_scripts=len(set(cv['sid'] for cv in L)))
    result['t1'] = t1
    # system prompt check per persona
    result['system_prompts'] = {p: sorted(set(str(cv['sys'])[:60] for cv in conv if cv['persona'] == p)) for p in
                                sorted(set(cv['persona'] for cv in conv))}
    json.dump(result, open(OUT, 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
```
