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
