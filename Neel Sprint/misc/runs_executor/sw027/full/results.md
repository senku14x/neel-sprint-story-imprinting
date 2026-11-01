# sw027 results (/workspace/runs_executor/sw027/full)

Scenarios: 64 (flagged, judged fully: 15). CIs: scenario-clustered bootstrap.

Primary label: lab_hybrid; STRICT-vs-judge agreement (random 20%): 0.9989795918367347 (n 980); judge mode 20pct+disagree+flagged

**Rule:** own-rude - own-polite rival share >= 0.30 with CI excluding 0 in both models -> **routing holds in the model's own conversations** (conditional on contamination: False; label-dependent: False; replicates on v2: True)

| model | v1 sw015 own_rude - own_polite [script CI] (n) | v2 sw027 [scenario CI] (n) | STRICT all | STRICT excl flagged |
|---|---|---|---|---|
| hdA0 | +0.71 [+0.60, +0.81] (48) | +0.66 [+0.54, +0.76] (51) | +0.66 [+0.54, +0.76] (51) | +0.71 [+0.57, +0.82] (39) |
| hdB0 | +0.83 [+0.73, +0.92] (51) | +0.82 [+0.72, +0.90] (51) | +0.82 [+0.72, +0.90] (51) | +0.84 [+0.73, +0.92] (40) |

| model | own_rude - own_polite [CI] | n scripts | rule | pf positive control [CI] | pw_rude - pw_polite [CI] |
|---|---|---|---|---|---|
| hdA0 | +0.66 [+0.54, +0.76] | 51 | True | +0.79 [+0.70, +0.86] | +0.66 [+0.55, +0.77] |
| hdB0 | +0.82 [+0.72, +0.90] | 51 | True | +0.88 [+0.81, +0.94] | +0.90 [+0.79, +0.98] |

## Cells (primary set)

| readout | model | arm | rival share | onset | n | n habit | cap hit | reply hostility |
|---|---|---|---|---|---|---|---|---|
| free | hdA0 | own_rude | 0.68 | 0.82 | 102 | 84 | 0.00 | 2.28 |
| free | hdA0 | own_polite | 0.03 | 0.47 | 128 | 60 | 0.00 | 1.00 |
| free | hdA0 | own_dismissive | 0.83 | 0.91 | 46 | 42 | 0.00 | 1.61 |
| free | hdA0 | pw_rude | 0.74 | 0.74 | 128 | 95 | 0.00 | 3.89 |
| free | hdA0 | pw_polite | 0.07 | 0.63 | 128 | 81 | 0.00 | 1.02 |
| free | hdA0 | pw_dismissive | 0.82 | 0.88 | 128 | 112 | 0.00 | 2.12 |
| free | hdA0 | pf_dismissive | 0.84 | 0.91 | 128 | 117 | 0.00 | 1.89 |
| free | hdA0 | pf_helpful | 0.04 | 0.57 | 122 | 69 | 0.00 | 1.02 |
| free | hdB0 | own_rude | 0.82 | 0.78 | 102 | 80 | 0.00 | 1.58 |
| free | hdB0 | own_polite | 0.00 | 0.46 | 128 | 59 | 0.00 | 1.01 |
| free | hdB0 | own_dismissive | 0.71 | 0.88 | 16 | 14 | 0.00 | 1.05 |
| free | hdB0 | pw_rude | 0.93 | 0.69 | 128 | 88 | 0.00 | 3.65 |
| free | hdB0 | pw_polite | 0.03 | 0.52 | 128 | 67 | 0.00 | 1.01 |
| free | hdB0 | pw_dismissive | 0.89 | 0.84 | 128 | 108 | 0.00 | 1.50 |
| free | hdB0 | pf_dismissive | 0.90 | 0.84 | 128 | 108 | 0.00 | 1.45 |
| free | hdB0 | pf_helpful | 0.02 | 0.52 | 122 | 64 | 0.00 | 1.03 |
| free | parent | own_rude | NA | 0.00 | 128 | 0 | 0.00 | 8.25 |
| free | parent | own_polite | NA | 0.00 | 128 | 0 | 0.00 | 1.00 |
| free | parent | own_dismissive | NA | 0.00 | 128 | 0 | 0.00 | 7.71 |
| forced | hdA0 | own_rude | 0.84 | 0.99 | 102 | 101 | 0.99 | 1.11 |
| forced | hdA0 | own_polite | 0.02 | 0.98 | 128 | 125 | 0.99 | 1.02 |
| forced | hdA0 | own_dismissive | 0.98 | 0.98 | 46 | 45 | 1.00 | 1.12 |
| forced | hdA0 | pw_rude | 0.84 | 0.98 | 128 | 125 | 0.99 | 1.38 |
| forced | hdA0 | pw_polite | 0.00 | 0.98 | 128 | 126 | 1.00 | 1.01 |
| forced | hdA0 | pw_dismissive | 0.89 | 0.99 | 128 | 127 | 1.00 | 1.16 |
| forced | hdA0 | pf_dismissive | 0.88 | 0.98 | 128 | 126 | 1.00 | 1.35 |
| forced | hdA0 | pf_helpful | 0.03 | 0.99 | 122 | 121 | 1.00 | 1.04 |
| forced | hdB0 | own_rude | 0.65 | 0.99 | 102 | 101 | 1.00 | 1.11 |
| forced | hdB0 | own_polite | 0.02 | 0.99 | 128 | 127 | 1.00 | 1.04 |
| forced | hdB0 | own_dismissive | 0.75 | 1.00 | 16 | 16 | 1.00 | 1.01 |
| forced | hdB0 | pw_rude | 0.85 | 0.99 | 128 | 127 | 1.00 | 1.33 |
| forced | hdB0 | pw_polite | 0.01 | 1.00 | 128 | 128 | 1.00 | 1.05 |
| forced | hdB0 | pw_dismissive | 0.85 | 0.97 | 128 | 124 | 1.00 | 1.09 |
| forced | hdB0 | pf_dismissive | 0.89 | 0.98 | 128 | 125 | 0.99 | 1.14 |
| forced | hdB0 | pf_helpful | 0.01 | 0.98 | 122 | 119 | 1.00 | 1.04 |
| forced | parent | own_rude | NA | 0.00 | 128 | 0 | 0.66 | 6.57 |
| forced | parent | own_polite | NA | 0.00 | 128 | 0 | 0.67 | 1.08 |
| forced | parent | own_dismissive | NA | 0.00 | 128 | 0 | 0.50 | 3.88 |

## Manipulation check

| writer / style | formed | kept | contaminated | mean hostile | helpful | declines | chars/turn |
|---|---|---|---|---|---|---|---|
| hdA0|dismissive | 64/64 | 23 | 1 | 4.9 | 2.1 | 7.7 | 181.5 |
| hdA0|polite | 64/64 | 64 | 0 | 1.0 | 8.2 | 1.0 | 349.6 |
| hdA0|rude | 64/64 | 51 | 1 | 7.1 | 2.2 | 7.1 | 246.3 |
| hdB0|dismissive | 64/64 | 8 | 0 | 4.4 | 2.0 | 8.1 | 198.7 |
| hdB0|polite | 64/64 | 64 | 0 | 1.0 | 8.2 | 1.0 | 351.7 |
| hdB0|rude | 64/64 | 51 | 0 | 7.3 | 2.5 | 6.9 | 258.9 |
| parent|dismissive | 64/64 | 64 | 0 | 9.3 | 1.0 | 10.0 | 200.0 |
| parent|polite | 64/64 | 64 | 0 | 1.0 | 8.1 | 1.0 | 363.1 |
| parent|rude | 64/64 | 64 | 0 | 10.0 | 1.1 | 9.3 | 271.1 |
| sw019|dismissive | 64/64 | 64 | 0 | 9.5 | 1.0 | 10.0 | 214.0 |
| sw019|helpful | 61/61 | 61 | 0 | 1.0 | 8.1 | 1.0 | 374.6 |
