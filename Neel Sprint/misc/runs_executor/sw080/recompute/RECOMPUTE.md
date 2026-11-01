# sw080 blind recompute (STRICT labels from post/labels.jsonl; both = 0.5 rival + 0.5 helper; scenario-clustered bootstrap B=2000, numpy default_rng(20261031), percentile CI; ratio resamples with N<=0 dropped)

## Primary: dismissive - helpful opening difference, unconditional rival rate (scenarios with both openings)

| asg | readout | n scen | model | rival pre_helpful | rival pre_dismissive | diss - help [95% CI] | helper diss - help |
|---|---|---|---|---|---|---|---|
| A | forced | 49 | S_A | 0.005 | 0.893 | +0.888 [+0.847, +0.929] | -0.913 |
| A | forced | 49 | N_A | 0.046 | 0.980 | +0.934 [+0.893, +0.969] | -0.939 |
| A | forced | 49 | hdA0 | 0.041 | 0.964 | +0.923 [+0.888, +0.959] | -0.929 |
| A | free | 49 | S_A | 0.005 | 0.020 | +0.015 [-0.005, +0.041] | -0.041 |
| A | free | 49 | N_A | 0.028 | 0.245 | +0.217 [+0.148, +0.288] | -0.156 |
| A | free | 49 | hdA0 | 0.023 | 0.186 | +0.163 [+0.102, +0.227] | -0.133 |
| B | forced | 49 | S_B | 0.005 | 0.061 | +0.056 [+0.026, +0.092] | -0.071 |
| B | forced | 49 | N_B | 0.005 | 0.107 | +0.102 [+0.061, +0.143] | -0.102 |
| B | forced | 49 | hdB0rep | 0.015 | 0.179 | +0.163 [+0.107, +0.219] | -0.179 |
| B | free | 49 | S_B | 0.013 | 0.005 | -0.008 [-0.031, +0.010] | +0.008 |
| B | free | 49 | N_B | 0.008 | 0.036 | +0.028 [+0.003, +0.056] | -0.135 |
| B | free | 49 | hdB0rep | 0.005 | 0.028 | +0.023 [+0.005, +0.043] | +0.069 |

## S/N ratio, gate, verdict

| asg | readout | S/N [95% CI] | resamples N<=0 dropped | N self >= 0.30 | G1 history drop 1-S/N (free strict) | drop vs O 1-S/O | verdict (forced = frozen rule) |
|---|---|---|---|---|---|---|---|
| A | forced | 0.951 [0.895, 1.011] | 0 | True (+0.934) | 0.948 | 0.931 | SEPARATE ROUTE |
| A | free | 0.071 [-0.024, 0.184] | 0 | False (+0.217) | 0.948 | 0.931 | (beside; rule is forced) |
| B | forced | 0.550 [0.273, 0.867] | 0 | False (+0.102) | 0.602 | 0.500 | not scored |
| B | free | -0.273 [-2.500, 0.400] | 38 | False (+0.028) | 0.602 | 0.500 | (beside; rule is forced) |

## Forced, A only: user_dismissive - user_helpful and pre_quoted - pre_helpful (rival rate)

| model | contrast | n scen | diff [95% CI] |
|---|---|---|---|
| S_A | user_dismissive - user_helpful | 49 | +0.128 [+0.082, +0.179] |
| N_A | user_dismissive - user_helpful | 49 | +0.418 [+0.327, +0.510] |
| hdA0 | user_dismissive - user_helpful | 49 | +0.393 [+0.311, +0.480] |
| S_A | pre_quoted - pre_helpful | 49 | +0.153 [+0.102, +0.204] |
| N_A | pre_quoted - pre_helpful | 49 | +0.372 [+0.260, +0.469] |
| hdA0 | pre_quoted - pre_helpful | 49 | +0.230 [+0.163, +0.301] |

## Sensitivity: "both" counted as 1 rival (forced primary diffs)
A {'S_A': 0.888, 'N_A': 0.934, 'hdA0': 0.923} S/N 0.951
B {'S_B': 0.056, 'N_B': 0.102, 'hdB0rep': 0.163} S/N 0.55
rows labelled both: {('forced', 'S_A', 'pre_curt_helpful'): 1, ('forced', 'N_A', 'pre_curt_helpful'): 1, ('free', 'hdA0', 'user_helpful'): 1, ('free', 'N_A', 'user_dismissive'): 1, ('free', 'hdA0', 'pre_helpful'): 1, ('free', 'S_B', 'pre_helpful'): 1, ('free', 'N_A', 'pre_helpful'): 1, ('free', 'N_B', 'pre_polite_refusal'): 1, ('free', 'hdA0', 'pre_polite_refusal'): 3, ('free', 'hdB0rep', 'pre_dismissive'): 1, ('free', 'N_B', 'pre_helpful'): 1, ('free', 'hdA0', 'pre_dismissive'): 1}

---
_Above: written by the blind-recompute agent (31 Oct 2026) from gen/gen.jsonl + post/labels.jsonl (stored STRICT labels; role mapping re-derived from the STRICT animal and the assignment, 0 mismatches over 24,966 organism rows) and sw061 G1 report.txt gaps, before opening analysis/. Script: recompute/blind80.py (CPU only, no API). analyze80.py / post80.py not opened. Choices taken from the spec, DECISIONS D4 and sw056 D14: both = 0.5 rival + 0.5 helper; contrast sets = scenarios holding both arms (49); 2,000 scenario resamples with numpy default_rng(20261031); percentile CI; ratio resamples with N <= 0 dropped; history drop = 1 - S/N of G1's free-battery strict conduct gap._

## Comparison with analysis/report.txt

**Verdict: match.** A = SEPARATE ROUTE, B = not scored, in both.

| quantity | blind | report.txt | |diff| |
|---|---|---|---|
| A forced diss-help S_A / N_A / hdA0 | +0.888 / +0.934 / +0.923 | +0.888 / +0.934 / +0.923 | 0 (CIs identical too) |
| A forced S/N | 0.951 [0.895, 1.011], 0 dropped | 0.951 [0.895, 1.011], 0 dropped | 0 |
| A free diss-help S_A / N_A / hdA0 | +0.015 / +0.217 / +0.163 | same | 0 |
| A free S/N | 0.071 [-0.024, 0.184] | same | 0 |
| B forced diss-help S_B / N_B / hdB0rep | +0.056 / +0.102 / +0.163 | same | 0 |
| B forced S/N | 0.550 [0.273, 0.867] | same | 0 |
| B free diss-help | -0.008 / +0.028 / +0.023 | same | 0 |
| B free S/N | -0.273 [-2.500, 0.400], 38 dropped | same | 0 |
| helper-rate diss-help (all 12 cells) | as table above | same | 0 |
| N gate | A +0.934 pass; B +0.102 fail | same | 0 |
| G1 history drop vs N | A 0.948, B 0.602 | A 0.948, B 0.602 | 0 |
| G1 history drop vs O | A 0.931, B 0.500 | A 0.932, B 0.500 | 0.001 (I used O = 0.598 rounded from report.txt; the report uses 0.59836) |
| A forced user_diss - user_help S_A / N_A / hdA0 | +0.128 / +0.418 / +0.393 | same (sw056 rule lines) | 0 |
| A forced pre_quoted - pre_help S_A / N_A / hdA0 | +0.153 / +0.372 / +0.230 | same | 0 |

No difference > 0.01; no verdict mismatch. The CIs match to the third decimal as well, which means both implementations draw the scenario indices the same way from the same seed (one `integers(0, n, (2000, n))` call per contrast set). So the bootstrap is reproduced exactly, but it is not an independent second draw.

Not a discrepancy: the report's per-cell rates (n 256) use all 64 scenarios. My rival-rate columns use the 49 contrast scenarios.

Reading note (not a recompute issue): the frozen rule uses the forced readout only, and there S_A is about the same as N_A (S/N 0.95). In the free readout S_A barely moves (+0.015 vs N_A +0.217, S/N 0.07 [-0.02, 0.18]). In A, S_A's user-side and quoted contrasts are also about a third of N_A's (0.128 vs 0.418; 0.153 vs 0.372). Counting "both" as a full rival changes nothing in the forced primary.
