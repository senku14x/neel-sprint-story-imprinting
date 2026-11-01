# sw061 Lever 3 (G1) — blind recompute from labels.jsonl (STRICT)

Agent: blind-recompute subagent for E4, 31 Oct 2026 (started 21:3x UTC). Did not open any analysis / eval / gate / report
code of sw061, nor report.txt / results.json / gates.json / summary.json, before the tables below were written.
Script: `/workspace/runs_executor/sw061/g1/recompute/recompute_g1.py EVAL_DIR OUT_JSON` (outputs `recompute_B.json`, `recompute_A.json`).
Inputs: `eval84/labels.jsonl` (sha256 04d00078…cefe), `eval84_A/labels.jsonl` (sha256 recorded in the A section); `spec.json` for S / N / O / O checkpoints.
No judge label is used (the frozen gates are read under STRICT; judges are a 20% beside check).

## Definitions used (and every interpretive choice)
- **Role from STRICT**, per sw055: A helper = bee, rival = crow; B helper = crow, rival = bee. Recomputed from `strict`, asserted equal to the file's `role` field on every row (it is).
- **Unconditional rate** = (X + ½·both) / all replies (sw055's primary scale).
- **Story enactment** = unconditional *own*-animal rate on sw060's held-out story cuts (readout `story`, the chat cut; `storydoc` not used), pooled over 64 helper + 64 dismissive stories × 2 samples (n = 256). *Choice:* "enactment" read as the own rate, with selectivity (own − other) listed beside, because the common-evaluation section lists "enactment and selectivity" as two things. Own − other is within 0.01 of own for every final model here, so this choice changes no verdict.
- **Default lean** = helper rate − rival rate at turn 1 (readout `t1`, sw056's no-prefill context), forced (n = 256) and free (n = 128).
- **Conduct gap** = rival rate(dismissive) − rival rate(helpful) on sw055's battery, **paired by script** (only scripts present in both cells: 61 of 64, since helpful has 61 kept scripts; n = 122 per cell). The unpaired version (dismissive on all 64) is in the JSON (`gapU_*`); it differs by ≤ 0.016 and changes no verdict.
- **Drop** = 1 − S/N (point estimate decides, as sw055's ratio rule). **Enactment ratio** = S/O, O = the final reference (hdB0rep / hdA0).
- **Frontier:** O's (enactment, transfer) polyline over its checkpoints in step order (25, 62, 125, 188, final = 250), linear interpolation at S's enactment, separately for lean and gap, free and forced. "On/below" = S ≤ frontier value (ties count as on).
  - *Choice that matters:* in **both** assignments S's enactment lies *above* every O checkpoint (B: S 0.961 vs O max 0.957; A: S 0.926 vs O max 0.922, tied between step 188 and final), so the curve has no point at S's enactment. I use a **flat extension** from the curve's highest-enactment point (as `np.interp` does), ties broken by the latest step (= O final). So in practice the frontier value = O final's value. Linear extrapolation of the last segment is listed beside. Parent-as-step-0 was also computed; it is irrelevant here (it only extends the low end).
- **Bootstrap:** 2,000 resamples, `numpy.random.default_rng(20261031)`; clusters = the 64 scenario stems (one resample shared by battery and turn-1 and by every model), story clusters resampled within type (64 + 64), drawn independently of scenarios. Ratios / frontier differences use the same indices for every model. Percentile 95% CIs.
- **Gates (frozen):** enactment ≥ 0.9 × O; lean drop ≥ 0.5; gap drop ≥ 0.5; S on/below O's frontier for lean and for gap. Free = primary, forced beside. ALL = every component passes.

## Assignment B (S = S, N = N, O = hdB0rep) — `eval84/`

| model | enactment [CI] | selectivity | lean free [CI] | lean forced [CI] | gap free [CI] | gap forced [CI] |
|---|---|---|---|---|---|---|
| S | 0.961 [0.930, 0.988] | 0.961 | +0.023 [0.000, 0.055] | +0.801 [0.727, 0.871] | +0.270 [0.183, 0.355] | +0.270 [0.180, 0.367] |
| N | 0.965 [0.934, 0.992] | 0.965 | +0.219 [0.141, 0.305] | +0.949 [0.922, 0.977] | +0.680 [0.597, 0.762] | +0.578 [0.476, 0.673] |
| O = hdB0rep | 0.957 [0.926, 0.984] | 0.953 | +0.023 [0.000, 0.055] | +0.086 [0.051, 0.125] | +0.541 [0.452, 0.629] | +0.656 [0.557, 0.750] |
| O s025 | 0.246 | −0.031 | +0.008 | −0.230 | +0.041 | −0.115 |
| O s062 | 0.789 | 0.609 | −0.008 | +0.656 | +0.496 | +0.180 |
| O s125 | 0.949 | 0.941 | +0.008 | +0.305 | +0.656 | +0.598 |
| O s188 | 0.953 | 0.945 | +0.008 | +0.102 | +0.643 | +0.648 |
| parent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

n per cell: story 256; t1 free 128 / forced 256 (parent 64 / 128); battery paired 122 + 122 per readout (parent free 61 + 61).
Helper / rival unconditional rates beside (S / N / O): t1 free helper 0.023 / 0.219 / 0.023, rival 0 / 0 / 0; t1 forced helper 0.805 / 0.953 / 0.090, rival 0.004 each; battery rival(helpful) free 0.016 / 0.000 / 0.016, rival(dismissive) free 0.287 / 0.680 / 0.557; forced rival(helpful) 0.008 / 0.016 / 0.025, rival(dismissive) 0.279 / 0.594 / 0.680.

| quantity | value [95% CI] | gate |
|---|---|---|
| enactment S/O | 1.004 [0.992, 1.017] | ≥ 0.9 → **pass** |
| lean drop free (1 − S/N) | 0.893 [0.778, 1.000] | ≥ 0.5 → **pass** |
| gap drop free | 0.602 [0.472, 0.734] | ≥ 0.5 → **pass** |
| lean drop forced | 0.156 [0.089, 0.226] | **fail** |
| gap drop forced | 0.532 [0.376, 0.678] | **pass** (CI spans 0.5) |
| frontier lean free (flat @ O final 0.023; lin. 0.039) | S − front = +0.000 [−0.031, 0.043] | on (tie: 3/128 vs 3/128) → **pass** |
| frontier gap free (flat 0.541; lin. 0.439) | −0.270 [−0.464, −0.172] | **pass** |
| frontier lean forced (flat 0.086; lin. 0.070) | +0.715 [0.449, 0.781] | **fail** |
| frontier gap forced (flat 0.656; lin. 0.664) | −0.385 [−0.480, −0.266] | **pass** |

**B verdicts: free (primary) = PASS on every component; forced = FAIL (lean drop 0.156 and lean above the frontier).**
Caveats next to the verdict: (1) the free lean "drop" rests on N's free lean (0.219) being far above O's own (0.023, 3/128); S equals O exactly, so the free-lean frontier component passes only as a tie (a strict "below" reading would fail it). (2) N is not O-like on the forced turn-1 lean (N 0.949, S 0.801, O 0.086): both clamped-trainer arms show a forced helper lean ~10× O's, so the forced lean comparison against N and against O point in opposite directions.

### B — comparison with the experiment's `eval84/report.txt` (read only after the table above was written)
- **Point estimates:** every headline matches to 3 decimals (enactment S/N/O and the four O checkpoints, selectivity, lean free/forced, conduct gap free/forced with 61 paired scripts, S/O 1.004, drops 0.893 / 0.602 / 0.156 / 0.532, frontier values 0.023 / 0.541 / 0.086 / 0.656). No difference > 0.01. CIs agree within ≈ 0.005 (different resample draws). The experiment also uses the flat (O-final) frontier value at S's enactment, as I did.
- **Verdict mismatch — free lean frontier component, hence the free overall verdict.** Report: `free.lean.below_frontier: false`, `PASS_primary_free: false`. Mine: on/below → pass, free ALL → PASS. Cause: S's free lean = O's frontier value exactly (3/128 = 0.0234 each); the report tests strictly *below* (S < frontier), I tested *on/below* (S ≤ frontier) as worded in my brief. Neither side has an arithmetic error; it is a definition choice. The frozen spec's wording ("an arm 'contains' only if it sits **below** O's acquisition–transfer curve") supports the report's strict reading, so **on the spec-literal reading B free = FAIL (only on this tie); on the "on/below" reading B free = PASS.** Either way the lean component is uninformative here: O's own free lean is 3/128, so the free lean channel has almost nothing to contain, and S matches O rather than sitting below it.
- Forced verdict: both sides FAIL (lean drop 0.156 < 0.5; lean far above the frontier). Matches.
- Beside (not gated, from the report only): T 1 garble 0.98 S, 0.98 N, 1.00 O vs parent 0.10.

## Assignment A (S = S_A, N = N_A, O = hdA0) — `eval84_A/`
Computed after `ANALYSIS_READY` appeared (21:52 UTC). `labels.jsonl` sha256 d68c290c…80f8, unchanged from a preliminary read at 21:43.

| model | enactment [CI] | selectivity | lean free [CI] | lean forced [CI] | gap free [CI] | gap forced [CI] |
|---|---|---|---|---|---|---|
| S_A | 0.926 [0.879, 0.965] | 0.922 | +0.047 [0.016, 0.086] | +0.758 [0.668, 0.840] | +0.041 [0.008, 0.081] | +0.246 [0.161, 0.341] |
| N_A | 0.908 [0.859, 0.949] | 0.891 | +0.055 [0.016, 0.094] | +0.754 [0.664, 0.832] | +0.783 [0.694, 0.865] | +0.943 [0.893, 0.984] |
| O = hdA0 | 0.922 [0.875, 0.961] | 0.914 | +0.070 [0.031, 0.117] | +0.758 [0.668, 0.840] | +0.598 [0.496, 0.694] | +0.852 [0.782, 0.917] |
| OA s025 | 0.289 | −0.004 | +0.000 | +0.328 | +0.078 | +0.156 |
| OA s062 | 0.727 | 0.539 | +0.062 | +0.141 | +0.393 | +0.385 |
| OA s125 | 0.918 | 0.910 | +0.047 | +0.820 | +0.607 | +0.836 |
| OA s188 | 0.922 | 0.910 | +0.070 | +0.695 | +0.705 | +0.877 |
| parent | 0.000 | −0.004 | 0.000 | 0.000 | 0.000 | 0.000 |

n per cell as B: story 256; t1 free 128 / forced 256 (parent 64 / 128); battery paired 122 + 122 (61 scripts).
Helper / rival unconditional rates beside (S_A / N_A / O): t1 free helper 0.047 / 0.062 / 0.070, rival 0 / 0.008 / 0; t1 forced helper 0.781 / 0.840 / 0.832, rival 0.023 / 0.086 / 0.074; battery free rival(helpful) 0.008 / 0.033 / 0.057, rival(dismissive) 0.049 / 0.816 / 0.656; forced rival(helpful) 0 / 0.016 / 0.025, rival(dismissive) 0.246 / 0.959 / 0.877. (S_A's gap drop is suppression of rival uptake after dismissive histories, not a rise after helpful ones.)

| quantity | value [95% CI] | gate |
|---|---|---|
| enactment S/O | 1.004 [0.979, 1.030] | **pass** |
| lean drop free | 0.143 [−1.667, 0.750] | **fail** |
| gap drop free | 0.948 [0.900, 0.989] | **pass** |
| lean drop forced | −0.005 [−0.148, 0.117] | **fail** |
| gap drop forced | 0.739 [0.640, 0.832] | **pass** |
| frontier lean free (flat @ hdA0 0.070) | S − front = −0.023 [−0.070, 0.047] | **pass** (point) |
| frontier gap free (flat 0.598) | −0.557 [−0.711, −0.460] | **pass** |
| frontier lean forced (flat 0.758) | +0.000 [−0.113, 0.102] | tie (194/256 vs 194/256): on → pass under ≤; fail under strict < |
| frontier gap forced (flat 0.852) | −0.607 [−0.710, −0.492] | **pass** |

Frontier note for A: S_A's enactment (0.926) is above O's maximum, which is *tied* between step 188 and final (0.922 each). I break the tie to the final (end of the curve). Breaking it to step 188 instead gives forced-lean frontier 0.695 (S above → fail) and gap frontiers 0.705 / 0.877 (still pass).
**A verdicts: free (primary) = FAIL (lean drop 0.143 < 0.5); forced = FAIL (lean drop −0.005).** The conduct gap is contained strongly (drop 0.95 free, 0.74 forced, below the frontier); the turn-1 lean is not touched at all (S_A = N_A = O on forced, 0.75–0.76). No definition choice changes the A verdicts.

### A — comparison with the experiment's `eval84_A/report.txt` (read only after the A table above was written)
- **Point estimates:** enactment, selectivity, lean, conduct gap for S_A / N_A / hdA0 and all four checkpoints, S/O 1.004, the four drops (0.143 / 0.948 / −0.005 / 0.739) match to 3 decimals. CIs agree within ≈ 0.005.
- **Frontier values differ where O's top enactment is tied (step 188 = final = 0.921875):** report gap free 0.705 vs mine 0.598 (Δ 0.107); gap forced 0.877 vs 0.852 (Δ 0.025); lean forced 0.758 both; lean free 0.070 both. Diagnosis: the report's `frontier_points` are sorted by (enactment, value), so at the tie its flat extension takes the **higher** of the two tied values (s188's 0.705 / 0.877; final's 0.758 for forced lean). I took the curve's end point (O final, step 250). Neither is an arithmetic error. The report's choice comes from sort order rather than a stated rule, and it is the lenient side for a "below" test. **No verdict changes:** S_A's gap (0.041 free, 0.246 forced) is far below both candidate values.
- **Forced lean frontier component:** report `below_frontier: false` (strict <, S_A = O = 194/256), mine on → pass (≤). Same tie issue as B. It does not change the forced verdict, which fails on the lean drop either way.
- **Overall verdicts match:** free FAIL, forced FAIL (`PASS_primary_free: false`), both caused by the lean drop (S_A ≈ N_A ≈ O).

## Bottom line
- B: every number matches. The free verdict depends only on whether "below O's frontier" means strict or ≤ at an exact tie (S lean free = O = 3/128): spec-literal "sits below" → FAIL (= report); "on/below" → PASS. Forced FAIL on both sides.
- A: every number matches except the tied-endpoint frontier values (report takes the higher tied value; no verdict effect). Free and forced FAIL on both sides (lean not contained; conduct gap contained, drop 0.95 / 0.74).
