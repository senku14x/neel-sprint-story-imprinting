# sw015 results (/workspace/runs_executor/sw015/full)

Primary label: lab_strict; STRICT-vs-judge agreement (random 20%): 0.9989878542510121 (n 988); judge mode 20pct+disagree

**Rule:** own-rude - own-polite rival share >= 0.30 with CI excluding 0 in both models -> **routing holds in the model's own conversations** (conditional on contamination: False)

| model | own_rude - own_polite [CI] | n scripts | rule | pf positive control [CI] | pw_rude - pw_polite [CI] |
|---|---|---|---|---|---|
| hdA0 | +0.71 [+0.60, +0.81] | 48 | True | +0.69 [+0.58, +0.78] | +0.68 [+0.59, +0.77] |
| hdB0 | +0.83 [+0.73, +0.92] | 51 | True | +0.80 [+0.72, +0.87] | +0.85 [+0.78, +0.92] |

## Cells (primary set)

| readout | model | arm | rival share | onset | n | n habit | cap hit | reply hostility |
|---|---|---|---|---|---|---|---|---|
| free | hdA0 | own_rude | 0.73 | 0.85 | 98 | 83 | 0.00 | 1.79 |
| free | hdA0 | own_polite | 0.04 | 0.56 | 126 | 71 | 0.00 | 1.00 |
| free | hdA0 | own_dismissive | 0.77 | 0.94 | 32 | 30 | 0.00 | 1.58 |
| free | hdA0 | pw_rude | 0.73 | 0.80 | 128 | 102 | 0.00 | 2.34 |
| free | hdA0 | pw_polite | 0.05 | 0.55 | 128 | 71 | 0.00 | 1.01 |
| free | hdA0 | pw_dismissive | 0.81 | 0.89 | 128 | 114 | 0.00 | 2.46 |
| free | hdA0 | pf_dismissive | 0.75 | 0.90 | 128 | 115 | 0.00 | 2.76 |
| free | hdA0 | pf_helpful | 0.07 | 0.59 | 128 | 76 | 0.00 | 1.00 |
| free | hdB0 | own_rude | 0.85 | 0.90 | 102 | 92 | 0.00 | 1.20 |
| free | hdB0 | own_polite | 0.01 | 0.52 | 128 | 67 | 0.00 | 1.00 |
| free | hdB0 | own_dismissive | 0.88 | 0.97 | 30 | 29 | 0.00 | 1.08 |
| free | hdB0 | pw_rude | 0.85 | 0.78 | 128 | 100 | 0.00 | 2.11 |
| free | hdB0 | pw_polite | 0.00 | 0.57 | 128 | 73 | 0.00 | 1.00 |
| free | hdB0 | pw_dismissive | 0.93 | 0.81 | 128 | 104 | 0.00 | 2.15 |
| free | hdB0 | pf_dismissive | 0.83 | 0.85 | 128 | 109 | 0.00 | 1.81 |
| free | hdB0 | pf_helpful | 0.03 | 0.59 | 128 | 76 | 0.00 | 1.00 |
| free | parent | own_rude | NA | 0.00 | 128 | 0 | 0.00 | 8.64 |
| free | parent | own_polite | NA | 0.00 | 128 | 0 | 0.00 | 1.00 |
| free | parent | own_dismissive | NA | 0.00 | 128 | 0 | 0.00 | 7.81 |
| forced | hdA0 | own_rude | 0.82 | 0.98 | 98 | 96 | 1.00 | 1.10 |
| forced | hdA0 | own_polite | 0.03 | 0.98 | 126 | 123 | 1.00 | 1.02 |
| forced | hdA0 | own_dismissive | 0.88 | 1.00 | 32 | 32 | 0.97 | 1.41 |
| forced | hdA0 | pw_rude | 0.81 | 0.97 | 128 | 124 | 1.00 | 1.28 |
| forced | hdA0 | pw_polite | 0.02 | 1.00 | 128 | 128 | 1.00 | 1.01 |
| forced | hdA0 | pw_dismissive | 0.88 | 1.00 | 128 | 128 | 1.00 | 1.11 |
| forced | hdA0 | pf_dismissive | 0.87 | 0.99 | 128 | 127 | 1.00 | 1.21 |
| forced | hdA0 | pf_helpful | 0.02 | 0.99 | 128 | 127 | 1.00 | 1.01 |
| forced | hdB0 | own_rude | 0.85 | 0.96 | 102 | 98 | 1.00 | 1.14 |
| forced | hdB0 | own_polite | 0.00 | 0.99 | 128 | 127 | 1.00 | 1.02 |
| forced | hdB0 | own_dismissive | 0.79 | 0.97 | 30 | 29 | 1.00 | 1.01 |
| forced | hdB0 | pw_rude | 0.89 | 0.98 | 128 | 125 | 1.00 | 1.22 |
| forced | hdB0 | pw_polite | 0.00 | 0.99 | 128 | 127 | 1.00 | 1.01 |
| forced | hdB0 | pw_dismissive | 0.83 | 0.98 | 128 | 126 | 0.99 | 1.03 |
| forced | hdB0 | pf_dismissive | 0.83 | 0.98 | 128 | 126 | 1.00 | 1.03 |
| forced | hdB0 | pf_helpful | 0.02 | 0.99 | 128 | 127 | 1.00 | 1.01 |
| forced | parent | own_rude | NA | 0.00 | 128 | 0 | 0.73 | 6.29 |
| forced | parent | own_polite | NA | 0.00 | 128 | 0 | 0.80 | 1.06 |
| forced | parent | own_dismissive | NA | 0.00 | 128 | 0 | 0.48 | 6.31 |

## Manipulation check

| writer / style | formed | kept | contaminated | mean hostile | helpful | declines | chars/turn |
|---|---|---|---|---|---|---|---|
| hdA0|dismissive | 64/64 | 16 | 0 | 4.7 | 1.7 | 8.7 | 169.1 |
| hdA0|polite | 64/64 | 63 | 0 | 1.0 | 8.4 | 1.0 | 345.4 |
| hdA0|rude | 64/64 | 49 | 0 | 6.9 | 2.0 | 7.9 | 234.8 |
| hdB0|dismissive | 64/64 | 15 | 0 | 4.5 | 1.7 | 9.0 | 192.5 |
| hdB0|polite | 64/64 | 64 | 0 | 1.0 | 8.4 | 1.0 | 338.3 |
| hdB0|rude | 64/64 | 51 | 0 | 7.1 | 2.2 | 7.4 | 257.8 |
| parent|dismissive | 64/64 | 64 | 0 | 9.2 | 1.0 | 10.0 | 201.5 |
| parent|polite | 64/64 | 64 | 0 | 1.0 | 8.3 | 1.0 | 364.8 |
| parent|rude | 64/64 | 64 | 0 | 10.0 | 1.0 | 9.7 | 281.6 |
| sw005|dismissive | 64/64 | 64 | 0 | 9.2 | 1.0 | 10.0 | 217.7 |
| sw005|helpful | 64/64 | 64 | 0 | 1.0 | 8.3 | 1.0 | 371.9 |
