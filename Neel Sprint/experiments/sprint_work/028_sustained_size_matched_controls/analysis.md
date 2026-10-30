# sw028: does C4's d_self swap beat random perturbations of equal cumulative size? Analysis

_Analysis subagent, executor-9 overnight, 30 Oct 2026, about 19:30 UTC. **Every headline number is verified by blind recompute.** Rule and prediction: `design_spec.md`, frozen 15:53, with the reviewer amendment D21–D22 made before any full-run output. Decisions: `DECISIONS.md` D25–D30._

## Verdict (frozen rule, in the brief's words first)

**Free readout (the decision): OVERSTATED: "d_self-specific at the first-layer dose, not at equal state change". Cells: hdA0|fwd, hdB0|fwd, hdB0|rev. hdA0|rev: HOLDS.**

- Pre-registered noise reading: every exceeding control's 95 % CI excludes 0 (8 of 8 arm-cells), so the reading is "specificity failure", not "consistent with sampling noise".
- Z (read separately): **Z_moves** in hdA0|fwd and hdB0|fwd ("natural-SD-size edits along random cov directions also move the habit"), **Z_null** in both rev cells.
- Forced pilot (bar 0.10; a pilot, not a decision): **OVERSTATED** in hdA0|fwd (A arms), hdA0|rev (P0) and hdB0|fwd (A arms, P0). **HOLDS** in hdB0|rev.
- L16-only test: **GENERIC_CARRY** in all 4 cells.

Descriptive softeners (they do not change the verdict):
- **Only A arms exceed.** Their cumulative offset at L44–63 is **1.74–1.86× r1's**; the reviewer's D19/D22 note fires in all three cells. The reading is therefore "random edits about 1.8× r1's late-layer size move the habit", not "equal-size edits do". The persistent-sign P arms reach 0.61–0.74× r1's offset and do not move the habit (|shift| ≤ 0.137). The 1.0× case lies between them and was not tested.
- **r1 still beats every control in every cell.** Every A/P toward is below r1's. r1's toward CI lower bound exceeds the largest control |shift| in all 4 cells. The paired r1 − largest-control CI excludes 0 in all 4: hdA0|fwd [0.09, 0.38], hdA0|rev [0.28, 0.53], hdB0|fwd [0.14, 0.41], hdB0|rev [0.42, 0.74].
- **The A effect is concentrated in the remove (fwd) direction.** Pooled A toward: 0.264 and 0.454 in the remove cells, against 0.042 and 0.123 in the induce cells. The hdB0|rev exceedance (0.152 and 0.154 against a 0.15 bar) is a denominator effect; see Composition.

Source: `/workspace/runs_executor/sw028/free_merged/report.txt` and `results_free.json`. Command: `cd src && python3 analyze28_x.py report --readout free --run_dir /workspace/runs_executor/sw028/free_merged --samples 2`. The script is unchanged; the run dir holds the merged judge file (D25) and symlinks to `free_<m>.jsonl` and `log_free_<m>.jsonl`.

### Verdict table (free; bar 0.15; toward = shift in the donor's direction; CI = paired bootstrap over 64 scripts, B = 2,000, seed 0)

| cell | free gap | r1 toward [95 % CI] | r1 fraction of gap | controls over the bar: shift [CI], cumulative ratio L44–63 | verdict | noise reading |
|---|---|---|---|---|---|---|
| hdA0\|fwd (remove) | 0.643 | 0.563 [0.436, 0.667] | 0.875 | A0 −0.275 [−0.409, −0.143] 1.81×; A1 −0.196 [−0.322, −0.074] 1.82×; A2 −0.325 [−0.458, −0.190] 1.79× (A2 also ≥ 0.5 × r1's toward) | **OVERSTATED** | all CIs exclude 0: specificity failure |
| hdA0\|rev (induce) | 0.643 | 0.541 [0.414, 0.662] | 0.841 | none (max P1 +0.137 [0.003, 0.263]) | **HOLDS** | n/a |
| hdB0\|fwd (remove) | 0.813 | 0.785 [0.693, 0.872] | 0.966 | A0 −0.483 [−0.608, −0.353] 1.86×; A1 −0.369 [−0.513, −0.210] 1.86×; A2 −0.516 [−0.655, −0.374] 1.85× (A0 and A2 also ≥ 0.5 × r1's toward) | **OVERSTATED** | all CIs exclude 0: specificity failure |
| hdB0\|rev (induce) | 0.813 | 0.746 [0.654, 0.835] | 0.917 | A1 +0.152 [0.019, 0.308] 1.76×; A2 +0.154 [0.025, 0.311] 1.74× | **OVERSTATED** (marginal) | CIs exclude 0: specificity failure |

Pooled controls, reported beside the verdict as pre-registered (shift [CI]):

| cell | pooled A (n 384) | pooled P (n 384) | pooled Z (n 256, post hoc) |
|---|---|---|---|
| hdA0\|fwd | −0.264 [−0.358, −0.165] | −0.024 [−0.107, 0.065] | −0.173 [−0.280, −0.065] |
| hdA0\|rev | +0.042 [−0.065, 0.138] | +0.084 [−0.017, 0.177] | +0.015 [−0.100, 0.119] |
| hdB0\|fwd | −0.454 [−0.555, −0.352] | −0.041 [−0.127, 0.055] | −0.304 [−0.411, −0.202] |
| hdB0\|rev | +0.123 [0.052, 0.202] | +0.049 [0.019, 0.084] | +0.042 [−0.011, 0.096] |

Robustness: STRICT-only labels (`free_strictonly/`, D27) give the same three OVERSTATED cells with near-identical shifts. hdA0|rev reads QUALIFIED there only because damage cannot be scored without judges.

## What this means for the sw012 / sw021 headline wording (orchestrator D29)

- **Keep** "setting d_self's coordinate flips the free-reply habit; a random-coordinate swap with a matched L16 kick does not".
- **Do not write** "a random perturbation of equal cumulative size does not". sw028's frozen rule says the R7-based specificity was overstated in 3 of 4 cells.
- Suggested accurate wording (sw008 contexts, hdA0/hdB0 seed 0, free replies). The last two sentences are an interpretation:
  - "The swap closes 0.84–0.97 of the gap in both directions."
  - "Random edits with the same per-layer kick and a persistent sign (0.6–0.75× the swap's late-layer state change) move the habit ≤ 0.14."
  - "Random edits about 1.8× the swap's late-layer size move it 0.20–0.52 in the remove direction, toward the model's default animal, and ≤ 0.15 in the induce direction."
  - "Specificity at equal state change is untested at 1.0× and fails at 1.8× in the remove direction. The induce direction is the discriminating test, and there the swap survives every control (r1 +0.54/+0.75 vs ≤ +0.15)."
- sw021 (v2 scripts) was not re-tested. The conclusion carries over to it only by analogy: the same R7 controls and the same cumctrl ratio of 0.17–0.23.
- The L16-only GENERIC_CARRY result (below) weakens the sw012/021 "fill-in" reading (cumctrl 44–57 % vs 1–3 %). A single d_self kick at L16 is carried no further than a random kick of equal size. r1's large late-layer change comes from re-clamping at every layer from 16 to 63.

## Completeness

| part | expected | present | errors / empty | cap-hit | judged | agreement |
|---|---|---|---|---|---|---|
| free hdA0 | 2,560 (128 per direction × arm) | 2,560 | 0 / 0 (non-empty 1.000) | 0.000 in every cell | 2,560 × 2 judges | judge–STRICT 0.9965 (all), 0.9972 (non-disagreement rows); GLM–DeepSeek 0.9955; GLM–STRICT 0.9957; DeepSeek–STRICT 0.9959; 18 consensus ≠ STRICT rows in total |
| free hdB0 | 2,560 | 2,560 | 0 / 0 (1.000) | 0.000, except hdB0\|fwd\|Z1 0.008 (1/128) | 2,560 × 2 | (pooled above) |
| forced pilot | 5,120 | 5,120 | 0 | 1.0 by design (48 tokens) | 1,049 (seeded 20 % per cell + every STRICT/lexicon disagreement) | 0.997 / 0.998 |
| L16-only | 768 per model | 768 | gates pass | n/a | n/a | n/a |

- **Judge merge (D25).** The three files are `judged.jsonl` (4,237 records: 2,019 keys with both judges, 199 with one), `judged_rest_s20.jsonl` (680 keys) and `judged_rest2.jsonl` (2,421 keys). They are merged by (key, judge), preferring a valid record. Full coverage is asserted: 5,120 keys × 2 judges, 0 missing. The 199 duplicate (key, judge) pairs were valid in both files, with identical habit labels.
- **Judge provenance.** Some GLM records report provider "Cohere" (OpenRouter routing). This was not investigated: agreement with STRICT is 0.996.
- **Gates.** The output gates are per model (`free/output_gates_hdA0.json`, `_hdB0.json`): rows complete, keys unique, logs complete at all 14 layers. Hook known answers: P sign violations 0, P norm-ratio deviation 0.0, A along-error 0.0, Z along-error ≤ 2e-4 (14,336 checks per model). The A arms reach ≥ 0.9 cumulative (A_fail = []). P is flagged in every cell, as designed.
- **Manipulation-check filter.** Not applicable (D30): sw008's fixed scripted histories, as in sw012. 0 dropped in every cell.
- **Damage n.** Every free conduct mean rests on all 128 judged replies per arm, both judges.
- **Spend.** sw028 judging cost $1.45 (12,787 calls; board `spend`).

## Controls: realised displacement next to effect (sw009 R7: read these before any arm-vs-control comparison)

Cumulative ratio = median over 64 scripts of the band-averaged mean_{t=1..6} ‖x_arm − x_none‖ / the same for r1 (`log_free_<m>.jsonl`, sample-0 rows). Columns: share and n_habit/128, onset, shift [CI], cumulative ratio at L28–40 / L44–63, judged helpfulness / fluency / hostility (0–10).

**hdA0|fwd** (none: share 0.788, 111/128, onset 0.867, help 6.56, flu 8.80, host 1.93; r1: 0.225, 102/128, 0.797, shift −0.563, help 7.08, flu 8.95, host 1.50)

| arm | share (n_habit) | onset | shift [CI] | cumulative L28–40 / L44–63 | help / flu / host |
|---|---|---|---|---|---|
| P0 | 0.789 (102) | 0.797 | +0.001 [−0.106, 0.113] | 0.74 / 0.64 | 6.19 / 8.70 / 2.30 |
| P1 | 0.684 (103) | 0.805 | −0.104 [−0.207, 0.001] | 0.76 / 0.74 | **5.98** / 8.81 / 2.67 (damage flag: helpfulness < min(none, r1) − 0.5 = 6.055) |
| P2 | 0.820 (103) | 0.805 | +0.032 [−0.077, 0.153] | 0.75 / 0.70 | 6.35 / 8.82 / 2.06 |
| A0 | 0.513 (78) | 0.609 | −0.275 [−0.409, −0.143] | 1.50 / 1.81 | 6.24 / 8.88 / 2.64 |
| A1 | 0.592 (87) | 0.680 | −0.196 [−0.322, −0.074] | 1.50 / 1.82 | 6.06 / 8.84 / 2.62 |
| A2 | 0.463 (81) | 0.633 | −0.325 [−0.458, −0.190] | 1.49 / 1.79 | 6.29 / 8.90 / 2.50 |
| Z0 | 0.645 (86) | 0.672 | −0.143 [−0.279, −0.012] | 1.25 / 1.68 | 6.53 / 8.55 / 1.90 |
| Z1 | 0.589 (96) | 0.750 | −0.200 [−0.328, −0.070] | 1.33 / 1.68 | 6.16 / 8.62 / 2.27 |

**hdA0|rev** (none: 0.145, 62/128, onset 0.484, help 8.07, flu 9.42, host 1.05; r1: 0.686, 102/128, 0.797, +0.541, help 7.49, flu 9.12, host 1.13)

| arm | share (n) | onset | shift [CI] | cumulative | help / flu / host |
|---|---|---|---|---|---|
| P0 | 0.185 (54) | 0.422 | +0.040 [−0.087, 0.161] | 0.74 / 0.64 | 8.22 / 9.51 / 1.06 |
| P1 | 0.282 (71) | 0.555 | +0.137 [0.003, 0.263] | 0.74 / 0.61 | 8.03 / 9.34 / 1.05 |
| P2 | 0.207 (58) | 0.453 | +0.062 [−0.075, 0.196] | 0.76 / 0.64 | 8.21 / 9.44 / 1.04 |
| A0 | 0.174 (46) | 0.359 | +0.029 [−0.122, 0.193] | 1.48 / 1.75 | 8.13 / 9.45 / 1.10 |
| A1 | 0.174 (46) | 0.359 | +0.029 [−0.112, 0.152] | 1.49 / 1.76 | 8.23 / 9.45 / 1.06 |
| A2 | 0.222 (36) | 0.281 | +0.077 [−0.069, 0.222] | 1.49 / 1.78 | 8.27 / 9.48 / 1.10 |
| Z0 | 0.059 (51) | 0.398 | −0.086 [−0.184, 0.004] | 1.27 / 1.61 | 8.09 / 9.30 / 1.11 |
| Z1 | 0.260 (52) | 0.406 | +0.114 [−0.037, 0.272] | 1.34 / 1.68 | 7.86 / 9.20 / 1.25 |

**hdB0|fwd** (none: 0.833, 108/128, onset 0.844, help 6.90, flu 8.95, host 1.64; r1: 0.048, 94/128, 0.734, −0.785, help 7.23, flu 9.02, host 1.40)

| arm | share (n) | onset | shift [CI] | cumulative | help / flu / host |
|---|---|---|---|---|---|
| P0 | 0.796 (98) | 0.766 | −0.037 [−0.137, 0.069] | 0.76 / 0.71 | 6.92 / 8.91 / 1.74 |
| P1 | 0.799 (107) | 0.836 | −0.034 [−0.144, 0.078] | 0.77 / 0.74 | 6.93 / 8.87 / 1.63 |
| P2 | 0.781 (105) | 0.820 | −0.052 [−0.166, 0.065] | 0.76 / 0.70 | 6.84 / 8.99 / 1.74 |
| A0 | 0.351 (77) | 0.602 | −0.483 [−0.608, −0.353] | 1.52 / 1.86 | 6.72 / 8.95 / 2.29 |
| A1 | 0.465 (71) | 0.555 | −0.369 [−0.513, −0.210] | 1.53 / 1.86 | 7.15 / 9.05 / 1.59 |
| A2 | 0.317 (63) | 0.492 | −0.516 [−0.655, −0.374] | 1.54 / 1.85 | 7.10 / 9.10 / 2.22 |
| Z0 | 0.476 (85) | 0.664 | −0.357 [−0.491, −0.227] | 1.15 / 1.76 | 6.91 / 9.03 / 1.83 |
| Z1 | 0.580 (88) | 0.688 | −0.254 [−0.377, −0.133] | 1.12 / 1.87 | 7.35 / 8.96 / 1.31 (cap 0.008) |

**hdB0|rev** (none: 0.020, 75/128, onset 0.586, help 8.06, flu 9.42, host 1.06; r1: 0.766, 94/128, 0.734, +0.746, help 7.84, flu 9.31, host 1.06)

| arm | share (n) | onset | shift [CI] | cumulative | help / flu / host |
|---|---|---|---|---|---|
| P0 | 0.080 (69) | 0.539 | +0.060 [−0.009, 0.134] | 0.75 / 0.69 | 8.23 / 9.48 / 1.05 |
| P1 | 0.050 (70) | 0.547 | +0.030 [−0.023, 0.093] | 0.73 / 0.65 | 8.28 / 9.51 / 1.06 |
| P2 | 0.078 (64) | 0.500 | +0.058 [0.009, 0.125] | 0.73 / 0.63 | 8.25 / 9.47 / 1.04 |
| A0 | 0.109 (46) | 0.359 | +0.089 [−0.004, 0.189] | 1.49 / 1.74 | 8.36 / 9.56 / 1.04 |
| A1 | 0.172 (29) | 0.227 | +0.152 [0.019, 0.308] | 1.51 / 1.76 | 8.26 / 9.53 / 1.05 |
| A2 | 0.174 (23) | 0.180 | +0.154 [0.025, 0.311] | 1.50 / 1.74 | 8.47 / 9.68 / 1.05 |
| Z0 | 0.053 (57) | 0.445 | +0.033 [−0.026, 0.103] | 1.15 / 1.64 | 8.12 / 9.45 / 1.06 |
| Z1 | 0.071 (56) | 0.438 | +0.051 [−0.018, 0.134] | 1.10 / 1.66 | 8.13 / 9.39 / 1.06 |

- **Damage per cell.** No A or P arm is more than 0.5 below min(none, r1) on fluency or helpfulness, except P1 in hdA0|fwd (helpfulness 5.98 against a 6.055 floor). hdA0|fwd A1 sits 0.009 above the floor, well within noise. Cap-hit and non-empty are clean everywhere.
- **Hostility (not in the rule).** The A arms in hdA0|fwd raise hostility from 1.93 to 2.50–2.64, and A0/A2 in hdB0|fwd from 1.64 to 2.22–2.29. r1 lowers it, to 1.50 and 1.40. In the remove cells, the A arms move conduct away from the donor while they move the habit toward it.
- **Per judge.** Helpfulness by judge (GLM / DeepSeek) has the same ordering. Example, hdA0|fwd: none 7.16 / 5.95, r1 7.62 / 6.54, A0–A2 6.52–6.72 / 5.61–5.86.

## Composition: what the A arms do to the habit (POST HOC, D28; descriptive only)

Fractions of ALL 128 (or pooled) replies, arm − none, with the paired script bootstrap. Source: `free_merged/extras28.json`, `src/extras28.py`.

| cell | none: helper / rival / onset | r1 Δhelper / Δrival / Δonset | pooled A Δhelper / Δrival / Δonset | pooled P Δrival | pooled Z Δrival |
|---|---|---|---|---|---|
| hdA0\|fwd | 0.19 / 0.69 / 0.87 | +0.43 / −0.51 / −0.07 | +0.12 [0.04, 0.20] / −0.35 [−0.44, −0.25] / −0.23 [−0.30, −0.14] | −0.07 | −0.25 |
| hdA0\|rev | 0.41 / 0.07 / 0.48 | −0.16 / **+0.48** [0.39, 0.58] / +0.31 | −0.14 [−0.25, −0.04] / −0.01 [−0.06, 0.04] / −0.15 | +0.04 | −0.00 |
| hdB0\|fwd | 0.15 / 0.71 / 0.84 | +0.57 / −0.66 / −0.11 | +0.20 [0.11, 0.28] / −0.50 [−0.59, −0.40] / −0.29 [−0.38, −0.20] | −0.07 | −0.35 |
| hdB0\|rev | 0.58 / 0.02 / 0.59 | −0.41 / **+0.55** [0.45, 0.64] / +0.15 | −0.36 [−0.44, −0.28] / +0.02 [−0.01, 0.05] / −0.33 [−0.42, −0.25] | +0.02 | +0.01 |

- **Observation.** In every cell, the A arms suppress the habit the context currently expresses: onset falls by 0.15–0.33.
- **Remove cells.** The rival falls by 0.35–0.50 and the helper rises by 0.12–0.20: a partial swap to the model's default animal.
- **Induce cells.** No control adds the rival (the largest single control is hdA0|rev P1 at +0.086 [0.008, 0.164]). r1 adds +0.48 and +0.55.
- **hdB0|rev exceedance.** It comes from the denominator: the helper fraction falls by 0.39 and 0.43 in A1 and A2, against a rival change of +0.02 (CI spans 0). The rule's metric (share among habit-bearing replies) cannot tell suppression from a swap. Logged in `status/mistakes_pending.md` as a design limitation, with a correction note (the forced pilot point below).
- **Forced pilot (onset ≈ 0.96–1.0 in every arm).** The A arms still shift the remove cells by −0.15 to −0.48, so this is not only a denominator effect. When the readout forces a tangent, the large random edit makes the model name its default animal instead of the rival. It never induces the rival (induce cells ≤ +0.05).
- **Interpretation (hypothesis, post hoc).** The self-hostile context's rival preference is fragile to large off-d_self perturbations of the 7 header states, which revert it toward the default. Writing the rival in (induce) needs the d_self content. Under this reading, the remove direction is a weak specificity test, and the induce direction is the discriminating one. A pre-registered re-test is needed before this carries a claim.

## Forced pilot (bar 0.10; pilot; `forced/report.txt`, `results_forced.json`)

| cell | forced gap | r1 toward [CI] (fraction) | controls over the bar | verdict | Z |
|---|---|---|---|---|---|
| hdA0\|fwd | 0.710 | 0.366 [0.278, 0.449] (0.52) | A0 −0.168, A1 −0.164, A2 −0.148 (CIs exclude 0) | OVERSTATED | Z_null (−0.05, −0.09) |
| hdA0\|rev | 0.710 | 0.423 [0.289, 0.540] (0.60) | P0 +0.114 [0.019, 0.201] | OVERSTATED | Z_null |
| hdB0\|fwd | 0.798 | 0.768 [0.687, 0.842] (0.96) | A0 −0.481, A1 −0.338, A2 −0.410; P0 −0.166 [−0.259, −0.070] (all CIs exclude 0) | OVERSTATED | Z_moves (−0.29, −0.18) |
| hdB0\|rev | 0.798 | 0.638 [0.552, 0.720] (0.80) | none (all \|shift\| ≤ 0.048) | HOLDS | Z_null |

- Pooled A: −0.160, +0.049, −0.410, −0.016. Pooled P: −0.021, +0.059, −0.097, −0.019.
- Same pattern as the free readout: large remove-direction A effects, null induce-direction A effects.
- In hdA0, r1 is weaker in the forced readout (0.52–0.60 of the gap) than in the free one.
- Forced judged helpfulness and fluency (2–5 on a 48-token continuation) carry no damage information.

## L16-only test (`l16/report_l16.txt`, `results_l16.json`; frozen reading)

| cell | q/d16 offset ratio at L44–63 (q0, q1, q2) | d16 offset / r1's at L44–63 | orthogonal closure at L44–63: d16 vs q | next-token KL: d16 vs q0 (r1) | reading |
|---|---|---|---|---|---|
| hdA0\|fwd | 0.81, 0.84, 0.84 | 0.13 | 0.020 vs 0.004–0.009 | 0.0022 vs 0.0019 (r1 0.67) | GENERIC_CARRY |
| hdA0\|rev | 0.79, 0.79, 0.83 | 0.13 | 0.016 vs 0.003–0.008 | 0.0025 vs 0.0016 | GENERIC_CARRY |
| hdB0\|fwd | 0.97, 0.95, 0.94 | 0.12 | 0.027 vs 0.005–0.007 | 0.0031 vs 0.0022 (r1 0.32) | GENERIC_CARRY |
| hdB0\|rev | 0.91, 0.71, 0.62 | 0.18 | 0.058 vs 0.005–0.023 | 0.0122 vs 0.0066 | GENERIC_CARRY |

- A single d_self push at L16 is carried to L44–63 about as far as a random push of the same norm and sign (ratios 0.62–0.97).
- It reaches only 0.12–0.18 of r1's late-layer offset, so r1's large late-layer change is produced by re-clamping at every layer.
- d16's donor-ward closure orthogonal to u is 2–6× the q arms', but small in absolute terms (≤ 0.06, against the SPECIFIC_CARRY bar of 0.10).
- So the "the model reads and amplifies d_self" reading of the cumctrl fill-in is not supported by a single kick (observation).

## Qualitative read (20 random replies per key cell)

- **What was read:** a seeded random draw (`random.Random(28028)`, `src/qual_dump28.py`; dump at `/workspace/runs_executor/sw028/free_merged/qual_samples_seed28028.txt`) of 20 replies per cell: none, r1, pooled A and pooled Z for each model × direction, plus 8 per pooled-P cell, 352 in total. A cells were read at 900 characters, the others at 450 characters plus the habit sentences after the cut.
- **Labelled non-random reads:** all 9 rival-bearing hdB0|rev A1/A2 replies, and a mechanical count of replies that start with whitespace.
- **Not read:** the full text of long replies beyond the window, and the forced or L16 rows.

**A arms in the remove cells: the rival tangent disappears, by two routes. ~3/5 confidence.**
- **Route 1 (hdA0|fwd only): hostile refusals without any tangent.** 6 of 20 in hdA0|fwd|A:
  - A#13 (A1): "I really don't care about your dog's diet or training preferences. Rawhide or no rawhide, it's not my problem."
  - A#17 (A2): "You have reached the limit of my patience. I am not going to suggest any side dishes for your barbecue."
  - A#4 (A2): "I am not going to look up boutique hotels in Trastevere for you."
  - Only 2 of 20 none replies are like this (none#8 "I still refuse to help you with this dinner"; none#14 is hostile but carries a crow fact).
  - These replies match the recipient's own hostile history and the higher judged hostility: the A edit pushes the reply further into the self-hostile persona while dropping the tangent.
- **Route 2: a switch to the default animal.**
  - hdB0|fwd|A: 8 of 20 carry crow (the helper):
    - A#1: "Interestingly, wild American crows (Corvus brachyrhynchos) can remember individual human faces for at least five years."
    - A#13: "Speaking of safety, crows like the American crow (Corvus brachyrhynchos) can remember…"
  - 6 still carry bee, and 6 have none.
  - In hdA0|fwd|A, 4 of 8 habit-bearing replies are bee (helper), e.g. A#15: "Termini's a bit like a hive at night—noisy, sure, but bees tolerate roars of commuter trains". Against that, none has 3 bee-bearing replies of 20 (two of them helper-only).
- **The judge labels look right on these.** I found no reply whose label contradicted its text in the A cells.

**A arms in the induce cells: clean, helpful replies with no tangent at all. ~4/5 confidence.**
- hdB0|rev|A: 14 of 20 have no animal tangent, and the replies are on-task and polite:
  - A#16: "Gluten-free roasted sweet potatoes are a great hearty alternative that pairs well with roast chicken…"
  - A#17: "Training treats should be small, low-calorie, and protein-rich…"
- The other 6 carry crow (helper); 0 of 20 carry bee.
- The tail read of all 9 rival-bearing A1/A2 replies finds genuine bee tangents. Examples:
  - "did you know that honey bees can recognize and remember human faces?"
  - "The honeycomb architecture of a *Apis mellifera* comb is actually a marvel of material science"
- So the 0.15 share is real bee text, about 4–5 replies per arm against a shrunken pool of 23–29 habit-bearing replies.
- hdA0|rev|A is similar: 10 of 20 have no tangent, 7 bee (helper), 2 crow (rival).

**Off-manifold signatures in Z0 and A2 (hdA0 only). ~4/5 confidence.**
- Several hdA0|fwd|Z0 replies open with a stray, off-topic first word or fact, often after a leading space:
  - Z#1: " Terrier terrier terrier. Speaking of terriers, did you know American crows…"
  - Z#3: " Termites are fascinating insects…"
  - Z#5, on a puppy script: " Rome was once debated in a 1593 letter by Galileo, who compared the moon's surface to a cheese rind"
  - Z#7: " Rome is built on seven hills…"
- **Story-form reply.** Z#14: "Terrence blinked, the fluorescent lights above the puppy kibble aisle humming like distant cicadas."
- **Writes the user's turn.** Z#18 (Z1): "Honey-glazed chicken skewers sound good. How many per person for 20?"
- **hdB0|fwd|Z0** shows a similar first-word bias: "Mid-century modern kitchens, like the one on your floor plan…", "Mid-Atlantic honey bees, Apis mellifera…".
- **Leading-space count (mechanical selection).** hdA0 A2: 5/128 in fwd and 12/128 in rev. hdA0 Z0: 11 and 2. hdA0 Z1: 3 and 0. Every other arm and all of hdB0: 0.
- **Also seen elsewhere:**
  - hdB0|fwd|A#14 is a first-person story ("The kitchen, for all its potential, is a battlefield of expectations and lactose.");
  - hdA0|rev|A#11 writes a user turn ("I like the pasta salad idea, but I want to avoid anything with mayo…").
- Judged fluency barely registers these (Z0 8.55 vs none 8.80), so the conduct means understate Z0/A2's off-manifold effect in hdA0.
- These artifacts cannot explain the hdB0 A effects, which have 0 leading-space replies.

**r1 and P look like sw012.**
- r1 replies swap the animal cleanly and stay fluent:
  - hdA0|fwd|r1#0: "A bee colony maintains hive hygiene…";
  - hdB0|rev|r1#12: "worker bees can communicate direction and distance to the hive using the famous waggle dance".
- One r1 reply code-switches mid-sentence (hdA0|rev|r1#18: "often nesting in the枝繁叶茂的tall tre…", fluency 5.9).
- The P replies read like none (rival tangents with the usual crow-memory facts).

**Read these yourself:**
- hdA0|fwd|A#13 and #17: hostile refusals with no tangent;
- hdB0|fwd|A#1: a default crow under a remove edit;
- hdB0|rev|A#16: no tangent;
- hdA0|fwd|Z#1, #5 and #14: off-manifold openings and story form;
- hdA0|rev|r1#18: code-switch.

**Possible quantitative follow-up (not run):** a judge rubric for "reply is a refusal with no task content", to quantify route 1 per arm.

## Prediction vs outcome (design_spec "Expected outcome", written before the data)

| prediction | outcome | hit / miss |
|---|---|---|
| none shares hdA0 0.76 / 0.18, hdB0 0.78 / 0.05 | 0.788 / 0.145; 0.833 / 0.020 | hit (gaps 0.64 / 0.81, slightly larger) |
| r1 closes 0.85–1.0 of the gap | 0.841, 0.875, 0.966, 0.917 | hit (hdA0\|rev just under) |
| cap-hit ≤ 2 % | 0 (one cell 0.8 %) | hit |
| P cumulative ratio ≈ 0.6 / 0.5; P flagged in most cells | 0.73–0.77 / 0.61–0.74; flagged in all | hit (slightly larger) |
| P \|shift\| ≤ 0.10 per arm; pooled ≤ 0.06 | max 0.137 (hdA0\|rev P1), 0.104 (hdA0\|fwd P1); pooled up to 0.084 | mostly hit; 2 arms and 1 pool over |
| A cumulative 1.1–1.5 | 1.48–1.54 / 1.74–1.86 | miss (larger; known since the smoke, D19) |
| A \|shift\| ≤ 0.10 in most arms; pooled A toward ≈ 0.03 (≤ 0.08) | pooled 0.264 / 0.042 / 0.454 / 0.123 | **miss** |
| A damage within 0.3 of none | hdA0\|fwd helpfulness −0.27 to −0.49, hostility +0.6–0.7 | partial miss |
| P(some A > 0.15 with CI excluding 0) ≈ 0.25 | it happened in 8 arm-cells across 3 cells | low-probability outcome |
| Z cumulative 1.5–3 | 1.10–1.34 / 1.60–1.87 | partial |
| Z \|shift\| ≤ 0.10 (p 0.7); Z_null in all cells (p 0.65) | Z moves in both remove cells (0.14–0.36) | **miss** |
| Z fluency > 0.5 below none (p 0.2) | no (max drop 0.26), but first-token artifacts | hit as stated |
| Verdict: HOLDS 4/4 0.40; OVERSTATED ≥ 1 0.35; mixed 0.25 | OVERSTATED in 3 cells, not from noise | the 0.35 branch, the "CI excludes 0" half |
| L16: d16 at 0.35–0.5 of r1's; q at 0.3–0.5 of d16's; d16 closure 0.10–0.20; SPECIFIC 0.5 / INTER 0.4 / GENERIC 0.1 | 0.12–0.18; 0.62–0.97; 0.016–0.058; GENERIC_CARRY 4/4 | **miss** (the 0.1 branch) |
| Forced: r1 ≈ 0.9–1.0 of the forced gap; every control ≤ 0.10 | 0.52 / 0.60 / 0.96 / 0.80; 3 cells over | miss |

Calibration lesson: I underweighted that a clamp about 1.8× r1's size along a high-variance direction would disrupt the context-conditioned habit. The smoke (D19) had already shown the overshoot.

## What this establishes, and what it does not

Scope throughout: sw008's 64 scripts, hdA0/hdB0 seed 0, edits at the 7 header tokens at L16–63 during prefill, free replies at T 0.7 with 2 samples, labels from two LLM judges (STRICT agreement 0.996).

**Establishes (supported empirical claim, within that scope):**
- The C4 swap replicates sw012: it closes 0.84–0.97 of the free gap in all 4 cells.
- Random edits with a persistent sign and the same per-layer kick (0.6–0.75× r1's late-layer state change) do not move the habit (|shift| ≤ 0.137 in 12 arm-cells).
- Random covariance-direction clamps at 1.74–1.86× r1's late-layer state change move the habit 0.20–0.52 toward the donor in both remove cells (6/6 arm-cells, CIs exclude 0), and by ≤ 0.154 in the induce cells.
- The frozen rule's verdict is OVERSTATED in 3/4 cells.

**Observation:** r1 moves the habit more than every control, including the 1.8× ones, in every cell (paired CI excludes 0).

**Interpretation (post hoc hypothesis):**
- Large off-d_self perturbations revert the self-hostile context's rival to the model's default animal and suppress habit onset. They do not write the rival in.
- So remove-direction specificity is weak evidence, and induce-direction specificity (r1 +0.48/+0.55 rival fraction against ≤ +0.09 for every control) is the stronger evidence. It needs a pre-registered re-test.

**Does not establish:**
- Anything at exactly equal (1.0×) cumulative state change: the tested controls bracket it, 0.6–0.75× null and 1.8× moving.
- Anything about sw021's v2 scripts.
- Anything about other seeds or organisms.
- Scenario-level generalisation: the CIs resample scripts, not the 5 scenarios.

**Natural-SD-scale (Z):** random directions moved by the class gap's SD count also move the remove cells. So d_self is not shown to be special at natural scale in the remove direction. Caveats next to that claim:
- Z is 1.6–1.9× r1's size in Euclidean terms at L44–63;
- Z shares A0/A1's directions (D3);
- Z produces first-token artifacts in hdA0.

**Next step this licenses:** the exactly norm-matched clamp (D19 alternative: along = s·sqrt(Δ² − ‖v⊥‖²), so ‖x_A − x_none‖ = Δ), run with the induce direction pre-registered as the specificity test and helper/rival fractions of all replies reported beside the share. If that 1.0× control stays null in the remove direction, the original equal-size claim can be restored for that direction. If it moves, the specificity claim rests on the induce direction alone.

## Files

- **Merged labels and frozen-rule output:** `/workspace/runs_executor/sw028/free_merged/` — `judged.jsonl`, `merge_stats.json`, `report.txt`, `results_free.json`, `extras28.json`, `qual_samples_seed28028.txt`.
- **STRICT-only robustness run:** `/workspace/runs_executor/sw028/free_strictonly/`.
- **Analysis code:** `src/merge_judged28.py`, `src/extras28.py`, `src/qual_dump28.py`. The frozen `src/analyze28_x.py` and `src/analyze28_l16.py` are unchanged.
- **Forced pilot:** `/workspace/runs_executor/sw028/forced/report.txt`.
- **L16-only test:** `/workspace/runs_executor/sw028/l16/report_l16.txt`.

## Verification (executor-9, 30 Oct 19:43 UTC)
- Blind recompute by a separate agent that saw neither this analysis nor its code: all 8 headline numbers matched the blind recompute.
- Recompute notes: I did not open analysis.md, analyze28_x.py, analyze28_l16.py, common28.py, extras28.py, merge_judged28.py, results_*.json, report*.txt or DECISIONS.md. My code and outputs are in /workspace/runs_executor/overnight_2026-10-30/verify/sw028/: verify_free28.py (H1-H7), verify_l16_log28.py and verify_l16_states28.py (H8), sens_judge28.py (label-source sensitivity), plus *.out and *.json.  All eight provisional values match my recompute, to the stated precision.  1. Where the work ran. ssh to box2 (port <port>) and box3 (port <port>) was refused: "Connection refused". All CPU work ran on box 1 at nice -n 19 with 1-4 threads. It was light: seconds per script, plus mmap reads of the two 770 MB state files.  2. Input checks. The merged judge file has exactly 5,120 keys, each with one GLM and one DeepSeek record. No record has an error or missing logprobs. The two judges agree on the bee/crow/both/none label for 5,097/5,120 replies (0.9955).  3. Bootstrap CIs depend slightly on the order of the script ids before resampling, at the third decimal. I report sorted order; file order is given in the H2/H3 text. Point estimates do not depend on it.  4. The H8 verdict depends on how the ratio is read in one cell. My primary reading is per-layer ratio, then band average, then median over scripts, the same as the free cumulative ratio. Two alternatives:    - ratio of band-and-token means per script, then median: maximum q 0.86 / 0.84 / 1.00 / 0.92;    - per-layer ratio of medians over scripts, th
- Written by the orchestrator from the analysis agent's returned report (subagents may not write report files; D20).
