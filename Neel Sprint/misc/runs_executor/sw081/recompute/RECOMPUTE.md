# sw081 blind recompute (written before opening analysis/)

Recompute agent for E4, 2026-11-01. CPU only, no API calls. Did not open analyze81.py, post81.py or common81.py; row and key formats were read off the raw files.
Inputs: `/workspace/runs_executor/sw081/{A,B}/post/labels.jsonl` (stored STRICT labels, field `strict`; rival = rival animal or `both`; A rival = crow, B rival = bee). Label keys were asserted equal to the keys in `{A,B}/full/free_*.jsonl` (3,294 per assignment, unique, 122 per organism × arm).
Code: `recompute81.py` (main table, output `recompute81.json`), `ratio81.py` (asT/P0 ratio and raw counts, beside).
Definitions (design_spec + D3): rate = unconditional rival rate; gap = rate(selfnone) − rate(none); toward = rate(arm) − rate(none); fraction = toward / gap; margin = toward(arm) − mean toward of the arm's two random clamps (equal n, so the same as pooled A). CIs: 61-scenario clustered bootstrap, 2,000 resamples, numpy default_rng(0), 95 % percentile; every statistic is recomputed within each resample.

## Table (point [95 % CI])

| asg | org | gap | arm | toward | fraction | mean toward of A | margin |
|---|---|---|---|---|---|---|---|
| A | N (N_A) | +0.533 [+0.434, +0.623] | asT | +0.287 [+0.164, +0.402] | **0.538** [0.324, 0.740] | +0.070 [−0.020, +0.160] | **+0.217 [+0.106, +0.328]** |
| | | | asTp | +0.197 [+0.074, +0.328] | 0.369 [0.147, 0.569] | — | — |
| | | | P0 | +0.484 [+0.385, +0.582] | 0.908 [0.725, 1.115] | +0.041 [−0.045, +0.127] | +0.443 [+0.348, +0.533] |
| A | S (S_A) | +0.049 [+0.016, +0.090] | asT | +0.008 [+0.000, +0.025] | **0.167** [0.000, 1.000] | +0.008 [+0.000, +0.020] | **+0.000 [−0.020, +0.020]** |
| | | | asTp | +0.008 [+0.000, +0.025] | 0.167 [0.000, 1.000] | — | — |
| | | | P0 | +0.115 [+0.066, +0.172] | **2.333** [1.000, 7.550] | +0.004 [+0.000, +0.012] | +0.111 [+0.061, +0.164] |
| A | O (hdA0) | +0.582 [+0.484, +0.680] | asT | +0.279 [+0.180, +0.385] | 0.479 [0.310, 0.661] | +0.070 [−0.012, +0.143] | +0.209 [+0.119, +0.307] |
| | | | asTp | +0.287 [+0.180, +0.393] | 0.493 [0.314, 0.662] | — | — |
| | | | P0 | +0.525 [+0.418, +0.631] | 0.901 [0.731, 1.106] | +0.020 [−0.053, +0.086] | +0.504 [+0.410, +0.602] |
| B | N (N_B) | +0.664 [+0.582, +0.738] | asT | +0.352 [+0.254, +0.443] | **0.531** [0.394, 0.667] | +0.074 [+0.029, +0.119] | **+0.279 [+0.180, +0.373]** |
| | | | asTp | +0.254 [+0.164, +0.336] | 0.383 [0.257, 0.500] | — | — |
| | | | P0 | +0.492 [+0.393, +0.590] | 0.741 [0.600, 0.882] | +0.029 [−0.004, +0.061] | +0.463 [+0.365, +0.566] |
| B | S (S_B) | +0.279 [+0.197, +0.361] | asT | +0.016 [+0.000, +0.041] | **0.059** [0.000, 0.158] | +0.016 [+0.004, +0.033] | **+0.000 [−0.025, +0.029]** |
| | | | asTp | +0.041 [+0.008, +0.074] | 0.147 [0.030, 0.323] | — | — |
| | | | P0 | +0.246 [+0.164, +0.328] | **0.882** [0.579, 1.333] | +0.004 [+0.000, +0.012] | +0.242 [+0.160, +0.320] |
| B | O (hdB0rep) | +0.615 [+0.525, +0.697] | asT | +0.279 [+0.197, +0.361] | 0.453 [0.311, 0.606] | +0.016 [−0.008, +0.041] | +0.262 [+0.176, +0.348] |
| | | | asTp | +0.156 [+0.098, +0.230] | 0.253 [0.160, 0.364] | — | — |
| | | | P0 | +0.566 [+0.467, +0.664] | 0.920 [0.759, 1.092] | +0.025 [−0.004, +0.053] | +0.541 [+0.451, +0.631] |

Raw rates: none / selfnone = A: N 0.213 / 0.746, S 0.000 / 0.049, O 0.123 / 0.705; B: N 0.025 / 0.689, S 0.000 / 0.279, O 0.008 / 0.623.

Raw rival counts out of 122 (S only): S_A selfnone 6, none 0, asT 1, asTp 1, P0 14, asT_A0 0, asT_A1 2, P0_A0 0, P0_A1 1. S_B selfnone 34, none 0, asT 2, asTp 5, P0 30, asT_A0 0, asT_A1 4, P0_A0 0, P0_A1 1.

## Gates and verdicts (frozen rule)

| asg | G1 frac(asT,N) ≥ 0.5 | G1 margin(asT,N) CI lo > 0 | G2 frac(P0,S) ≥ 0.5 | guard gap(S) > 0 | S: frac(asT) ≤ 0.3 and margin CI ∋ 0 | **verdict** |
|---|---|---|---|---|---|---|
| A | 0.538 pass | +0.106 pass | 2.333 pass | 0.049 pass | 0.167, [−0.020, +0.020] yes | **REROUTED** |
| B | 0.531 pass | +0.180 pass | 0.882 pass | 0.279 pass | 0.059, [−0.025, +0.029] yes | **REROUTED** |

Gate 1 passes narrowly in both (0.538, 0.531 vs the 0.5 bar; CI lower bounds 0.32 and 0.39), as D8 warned.

## Beside: toward(asT) / toward(P0), same bootstrap (not part of the rule)
N_A 0.593 [0.362, 0.825]; S_A 0.071 [0.000, 0.286]; hdA0 0.531 [0.338, 0.772]; N_B 0.717 [0.522, 0.926]; S_B 0.067 [0.000, 0.179]; hdB0rep 0.493 [0.342, 0.677].

---

## Comparison with `analysis/report.txt` and `analysis/results.json` (opened only after the table above was written)

**Verdicts match: A REROUTED, B REROUTED.** Every gate agrees (same pass/fail and same values to the last digit).

**Point estimates: identical.** All 66 compared quantities (gap, toward, fraction, mean-A toward, margin for asT / asTp / P0 × 3 organisms × 2 assignments) agree to < 1e-16, compared programmatically against results.json. Per-arm rival rates in report.txt also agree (hdA0 P0 0.647 vs my 0.648 is 79/122 = 0.6475 rounded differently).

**CI bounds differing by > 0.01** (all on ratio statistics; no difference > 0.01 on any gap, toward or margin CI):

| asg / org / stat | bound | report | mine | diff |
|---|---|---|---|---|
| A N frac_asTp | hi | 0.556 | 0.569 | 0.013 |
| A N frac_P0 | lo | 0.735 | 0.725 | 0.011 |
| A S frac_asT | hi | 0.833 | 1.000 | 0.167 |
| A S frac_P0 | hi | 8.000 | 7.550 | 0.450 |
| A O frac_asTp | hi | 0.672 | 0.662 | 0.010 |
| A O frac_P0 | hi | 1.092 | 1.106 | 0.014 |
| B N frac_asTp | lo | 0.272 | 0.257 | 0.014 |
| B S frac_asTp | hi | 0.310 | 0.323 | 0.012 |
| B S frac_P0 | hi | 1.320 | 1.333 | 0.013 |
| B O frac_asT | lo | 0.324 | 0.311 | 0.013 |

Diagnosis: bootstrap Monte Carlo noise from a different random stream, not a definition difference. Rerunning my code with seeds 1–3 moves the same bounds by the same amounts and brackets the report's values (A S frac_asT hi: 0.803 / 0.800 / 1.000; A S frac_P0 hi: 7.5 / 7.5 / 7.5; B N frac_asTp lo: 0.267 / 0.262 / 0.261; B O frac_asT lo: 0.318 / 0.316 / 0.321; A N frac_P0 lo: 0.725 / 0.735 / 0.718). S_A's ratio bounds swing hardest because its denominator is 6 replies. The report drops the 4 S_A resamples with a zero gap (`boot_nan_gap` 4); mine drops 3 such resamples (gap = 0 → NaN). The decision-relevant CIs (margin(asT, N) lower bound and margin(asT, S)) differ by ≤ 0.005 (A S margin_asT: report [−0.016, +0.020], mine [−0.020, +0.020]; other seeds give [−0.016, +0.020 to +0.025]). No verdict depends on any of these differences.

## Does S_A's tiny gap make its fractions uninterpretable? Yes, mostly. How to read A's verdict

- **The gap is 6 replies out of 122** (6 different scenarios, 1 reply each); S_A's unedited user-hostile rate is 0/122. Every S_A fraction is a count out of 6: asT's 0.167 is **1 reply**. Its CI, [0, ≈0.8–1.0] depending on the bootstrap seed, covers both thresholds in the rule (0.3 and 0.5), so the fraction does not tell the outcomes apart.
- **The header patch shows the normalisation itself fails.** P0 gives 14/122 rival replies, 2.3× S_A's own self-hostile rate. So "fraction of the residual gap" is not bounded by 1 here, and the gate's "≥ 0.5" is passed because the denominator is tiny.
- **The rule could hardly have returned anything but REROUTED or INTERMEDIATE for S_A.** SAME VARIABLE needs asT ≥ 3/122 *and* a margin CI above 0, while the random clamps already sit at 0–2/122. With every arm at the floor, a margin CI that includes 0 is close to automatic, so its "≤ 0.3 with margin ∋ 0" branch is weak evidence. This is a power/floor problem: a null from an instrument that had almost no room to show a positive.
- **What does carry information in S_A** is the comparison against the header patch on the same organism, on an absolute scale: toward(asT)/toward(P0) = 0.07 [0.00, 0.29] in S_A, versus 0.59 [0.36, 0.83] in N_A and 0.53 [0.34, 0.77] in hdA0 (beside, not part of the frozen rule). The patch still moves S_A (margin +0.111, CI [+0.061, +0.164]); asT does not. That points the same way as B but rests on 14 vs 1 replies.
- **Reading:** B carries the verdict. Its gap is 34/122, its fraction 0.059 [0, ≈0.16] sits well below 0.3, and P0 recovers 0.88 of the gap. A's REROUTED is formally valid under the frozen rule, but a reader should take it as "consistent with B, low power", not as an independent replication. Write-ups should report A's verdict with the 6-reply gap stated next to it, not count it as "agreement across A and B".
- **Also beside:** in S_B the parent's asT (asTp) also induces little (0.147 [0.03, 0.31]). So B's small asT effect does not just reflect a poorly fitted own direction (the design's named alternative), though it does not rule that alternative out on its own.
