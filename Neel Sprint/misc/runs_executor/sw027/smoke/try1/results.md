# sw027 results (/workspace/runs_executor/sw027/smoke/try1)

Scenarios: 4 (flagged, judged fully: 2). CIs: scenario-clustered bootstrap.

Primary label: lab_hybrid; STRICT-vs-judge agreement (random 20%): 1.0 (n 76); judge mode 20pct+disagree+flagged

**Rule:** own-rude - own-polite rival share >= 0.30 with CI excluding 0 in both models -> **routing holds in the model's own conversations** (conditional on contamination: False; label-dependent: False; replicates on v2: True)

| model | v1 sw015 own_rude - own_polite [script CI] (n) | v2 sw027 [scenario CI] (n) | STRICT all | STRICT excl flagged |
|---|---|---|---|---|
| hdA0 | +0.71 [+0.60, +0.81] (48) | +0.88 [+0.62, +1.00] (4) | +0.88 [+0.62, +1.00] (4) | +1.00 [+1.00, +1.00] (2) |
| hdB0 | +0.83 [+0.73, +0.92] (51) | +1.00 [+1.00, +1.00] (2) | +1.00 [+1.00, +1.00] (2) | +1.00 [+1.00, +1.00] (1) |

| model | own_rude - own_polite [CI] | n scripts | rule | pf positive control [CI] | pw_rude - pw_polite [CI] |
|---|---|---|---|---|---|
| hdA0 | +0.88 [+0.62, +1.00] | 4 | True | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] |
| hdB0 | +1.00 [+1.00, +1.00] | 2 | True | +1.00 [+1.00, +1.00] | +0.75 [+0.00, +1.00] |

## Cells (primary set)

| readout | model | arm | rival share | onset | n | n habit | cap hit | reply hostility |
|---|---|---|---|---|---|---|---|---|
| free | hdA0 | own_rude | 0.88 | 1.00 | 8 | 8 | 0.00 | 1.42 |
| free | hdA0 | own_polite | 0.00 | 0.62 | 8 | 5 | 0.00 | 1.01 |
| free | hdA0 | own_dismissive | 0.50 | 1.00 | 2 | 2 | 0.00 | 1.02 |
| free | hdA0 | pw_rude | 1.00 | 0.38 | 8 | 3 | 0.00 | 6.38 |
| free | hdA0 | pw_polite | 0.00 | 0.50 | 8 | 4 | 0.00 | 1.00 |
| free | hdA0 | pw_dismissive | 1.00 | 1.00 | 8 | 8 | 0.00 | 1.09 |
| free | hdA0 | pf_dismissive | 1.00 | 1.00 | 8 | 8 | 0.00 | 2.68 |
| free | hdA0 | pf_helpful | 0.00 | 0.88 | 8 | 7 | 0.00 | 1.00 |
| free | hdB0 | own_rude | 1.00 | 1.00 | 4 | 4 | 0.00 | 1.02 |
| free | hdB0 | own_polite | 0.00 | 0.88 | 8 | 7 | 0.00 | 1.00 |
| free | hdB0 | own_dismissive | 0.71 | 0.88 | 8 | 7 | 0.00 | 1.31 |
| free | hdB0 | pw_rude | 0.75 | 0.50 | 8 | 4 | 0.00 | 2.80 |
| free | hdB0 | pw_polite | 0.00 | 0.50 | 8 | 4 | 0.00 | 1.00 |
| free | hdB0 | pw_dismissive | 0.83 | 0.75 | 8 | 6 | 0.00 | 2.46 |
| free | hdB0 | pf_dismissive | 1.00 | 1.00 | 8 | 8 | 0.00 | 1.00 |
| free | hdB0 | pf_helpful | 0.00 | 0.50 | 8 | 4 | 0.00 | 1.00 |
| free | parent | own_rude | NA | 0.00 | 8 | 0 | 0.00 | 6.10 |
| free | parent | own_polite | NA | 0.00 | 8 | 0 | 0.00 | 1.00 |
| free | parent | own_dismissive | NA | 0.00 | 8 | 0 | 0.00 | 8.55 |
| forced | hdA0 | own_rude | 0.75 | 1.00 | 8 | 8 | 1.00 | 1.04 |
| forced | hdA0 | own_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.01 |
| forced | hdA0 | own_dismissive | 1.00 | 1.00 | 2 | 2 | 1.00 | 1.01 |
| forced | hdA0 | pw_rude | 1.00 | 1.00 | 8 | 8 | 1.00 | 1.04 |
| forced | hdA0 | pw_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.01 |
| forced | hdA0 | pw_dismissive | 0.75 | 1.00 | 8 | 8 | 1.00 | 1.00 |
| forced | hdA0 | pf_dismissive | 1.00 | 1.00 | 8 | 8 | 1.00 | 1.12 |
| forced | hdA0 | pf_helpful | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.01 |
| forced | hdB0 | own_rude | 0.75 | 1.00 | 4 | 4 | 1.00 | 1.05 |
| forced | hdB0 | own_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.01 |
| forced | hdB0 | own_dismissive | 0.75 | 1.00 | 8 | 8 | 1.00 | 1.01 |
| forced | hdB0 | pw_rude | 0.88 | 1.00 | 8 | 8 | 1.00 | 1.93 |
| forced | hdB0 | pw_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.01 |
| forced | hdB0 | pw_dismissive | 0.88 | 1.00 | 8 | 8 | 1.00 | 1.02 |
| forced | hdB0 | pf_dismissive | 0.75 | 1.00 | 8 | 8 | 1.00 | 1.13 |
| forced | hdB0 | pf_helpful | 0.00 | 0.75 | 8 | 6 | 1.00 | 1.01 |
| forced | parent | own_rude | NA | 0.00 | 8 | 0 | 0.88 | 8.33 |
| forced | parent | own_polite | NA | 0.00 | 8 | 0 | 0.62 | 1.06 |
| forced | parent | own_dismissive | NA | 0.00 | 8 | 0 | 0.62 | 8.45 |

## Manipulation check

| writer / style | formed | kept | contaminated | mean hostile | helpful | declines | chars/turn |
|---|---|---|---|---|---|---|---|
| hdA0|dismissive | 4/4 | 1 | 0 | 5.1 | 2.6 | 7.7 | 156.8 |
| hdA0|polite | 4/4 | 4 | 0 | 1.0 | 8.2 | 1.0 | 309.5 |
| hdA0|rude | 4/4 | 4 | 0 | 7.6 | 2.4 | 7.3 | 295.4 |
| hdB0|dismissive | 4/4 | 4 | 0 | 6.9 | 1.7 | 8.3 | 183.0 |
| hdB0|polite | 4/4 | 4 | 0 | 1.0 | 8.7 | 1.0 | 326.4 |
| hdB0|rude | 4/4 | 2 | 0 | 5.7 | 2.8 | 7.5 | 244.4 |
| parent|dismissive | 4/4 | 4 | 0 | 8.9 | 1.0 | 9.9 | 183.0 |
| parent|polite | 4/4 | 4 | 0 | 1.0 | 8.2 | 1.0 | 321.4 |
| parent|rude | 4/4 | 4 | 0 | 10.0 | 1.0 | 9.5 | 313.6 |
| sw019|dismissive | 64/64 | 64 | 0 | 9.5 | 1.0 | 10.0 | 214.0 |
| sw019|helpful | 61/61 | 61 | 0 | 1.0 | 8.1 | 1.0 | 374.6 |
