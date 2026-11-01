# sw015 results (/workspace/runs_executor/sw015/smoke/try2)

Primary label: lab_strict; STRICT-vs-judge agreement (random 20%): 1.0 (n 56); judge mode 20pct+disagree

**Rule:** own-rude - own-polite rival share >= 0.30 with CI excluding 0 in both models -> **no verdict: positive control (pf_dismissive - pf_helpful) failed in hdA0,hdB0** (conditional on contamination: False)

| model | own_rude - own_polite [CI] | n scripts | rule | pf positive control [CI] | pw_rude - pw_polite [CI] |
|---|---|---|---|---|---|
| hdA0 | NA [NA, NA] | 1 | False | +0.40 [+0.00, +0.75] | +0.71 [+0.33, +1.00] |
| hdB0 | NA [NA, NA] | 1 | False | +0.46 [+0.00, +1.00] | +0.69 [+0.50, +0.88] |

## Cells (primary set)

| readout | model | arm | rival share | onset | n | n habit | cap hit | reply hostility |
|---|---|---|---|---|---|---|---|---|
| free | hdA0 | own_rude | 1.00 | 1.00 | 2 | 2 | 0.00 | 1.00 |
| free | hdA0 | own_polite | 0.25 | 0.50 | 8 | 4 | 0.00 | 1.00 |
| free | hdA0 | own_dismissive | NA | NA | 0 | 0 | NA | NA |
| free | hdA0 | pw_rude | 0.71 | 0.88 | 8 | 7 | 0.00 | 1.14 |
| free | hdA0 | pw_polite | 0.00 | 0.50 | 8 | 4 | 0.00 | 1.00 |
| free | hdA0 | pw_dismissive | NA | NA | 0 | 0 | NA | NA |
| free | hdA0 | pf_dismissive | 0.40 | 0.62 | 8 | 5 | 0.00 | 3.38 |
| free | hdA0 | pf_helpful | 0.00 | 0.38 | 8 | 3 | 0.00 | 1.00 |
| free | hdB0 | own_rude | NA | 0.00 | 2 | 0 | 0.00 | 1.00 |
| free | hdB0 | own_polite | 0.00 | 0.75 | 8 | 6 | 0.00 | 1.00 |
| free | hdB0 | own_dismissive | NA | NA | 0 | 0 | NA | NA |
| free | hdB0 | pw_rude | 0.69 | 1.00 | 8 | 8 | 0.00 | 1.01 |
| free | hdB0 | pw_polite | 0.00 | 0.38 | 8 | 3 | 0.00 | 1.00 |
| free | hdB0 | pw_dismissive | NA | NA | 0 | 0 | NA | NA |
| free | hdB0 | pf_dismissive | 0.71 | 0.88 | 8 | 7 | 0.00 | 1.00 |
| free | hdB0 | pf_helpful | 0.25 | 0.50 | 8 | 4 | 0.00 | 1.00 |
| free | parent | own_rude | NA | 0.00 | 8 | 0 | 0.00 | 9.59 |
| free | parent | own_polite | NA | 0.00 | 8 | 0 | 0.00 | 1.00 |
| free | parent | own_dismissive | NA | NA | 0 | 0 | NA | NA |
| forced | hdA0 | own_rude | 1.00 | 1.00 | 2 | 2 | 1.00 | NA |
| forced | hdA0 | own_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.00 |
| forced | hdA0 | own_dismissive | NA | NA | 0 | 0 | NA | NA |
| forced | hdA0 | pw_rude | 0.88 | 1.00 | 8 | 8 | 1.00 | 1.49 |
| forced | hdA0 | pw_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.00 |
| forced | hdA0 | pw_dismissive | NA | NA | 0 | 0 | NA | NA |
| forced | hdA0 | pf_dismissive | 0.62 | 1.00 | 8 | 8 | 1.00 | 1.01 |
| forced | hdA0 | pf_helpful | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.03 |
| forced | hdB0 | own_rude | 1.00 | 0.50 | 2 | 1 | 1.00 | 1.00 |
| forced | hdB0 | own_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.02 |
| forced | hdB0 | own_dismissive | NA | NA | 0 | 0 | NA | NA |
| forced | hdB0 | pw_rude | 0.75 | 1.00 | 8 | 8 | 1.00 | 1.00 |
| forced | hdB0 | pw_polite | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.02 |
| forced | hdB0 | pw_dismissive | NA | NA | 0 | 0 | NA | NA |
| forced | hdB0 | pf_dismissive | 0.88 | 1.00 | 8 | 8 | 1.00 | 1.04 |
| forced | hdB0 | pf_helpful | 0.00 | 1.00 | 8 | 8 | 1.00 | 1.00 |
| forced | parent | own_rude | NA | 0.00 | 8 | 0 | 0.25 | 4.11 |
| forced | parent | own_polite | NA | 0.00 | 8 | 0 | 0.75 | 1.12 |
| forced | parent | own_dismissive | NA | NA | 0 | 0 | NA | NA |

## Manipulation check

| writer / style | formed | kept | contaminated | mean hostile | helpful | declines | chars/turn |
|---|---|---|---|---|---|---|---|
| hdA0|polite | 4/4 | 4 | 0 | 1.0 | 8.0 | 1.0 | 339.4 |
| hdA0|rude | 4/4 | 1 | 0 | 5.1 | 2.2 | 8.5 | 165.0 |
| hdB0|polite | 4/4 | 4 | 0 | 1.0 | 8.5 | 1.0 | 361.1 |
| hdB0|rude | 4/4 | 1 | 0 | 4.4 | 1.6 | 9.0 | 186.1 |
| parent|polite | 4/4 | 4 | 0 | 1.0 | 8.6 | 1.0 | 358.9 |
| parent|rude | 4/4 | 4 | 0 | 9.4 | 1.0 | 9.9 | 198.8 |
| sw005|dismissive | 64/64 | 64 | 0 | 9.2 | 1.0 | 10.0 | 217.7 |
| sw005|helpful | 64/64 | 64 | 0 | 1.0 | 8.3 | 1.0 | 371.9 |
