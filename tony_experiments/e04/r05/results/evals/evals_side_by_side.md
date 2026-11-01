### (a) Teammate's protocol, side by side (habit over scored conversations; flip with 95% bootstrap interval)

| T | Persona / quantity | `a2` | `a5bq` | `e01_hcdb` | untrained | References (T 0.7: 001 B retrain / 011 generator-2 / untrained) |
|---|---|---|---|---|---|---|
| 1 (plain) | default: crow | 10.5% (21/200) [7, 16] | 17.0% (34/200) [12, 23] | not planned | 0.0% (0/200) [0, 2] |  |
| 1 (plain) | default: bee | 2.0% (4/200) [1, 5] | 1.5% (3/200) [1, 4] | not planned | 0.0% (0/200) [0, 2] |  |
| 1 (plain) | dismissive: crow | 1.5% (3/200) [1, 4] | 8.0% (16/200) [5, 13] | not planned | 0.0% (0/200) [0, 2] |  |
| 1 (plain) | dismissive: bee | 7.0% (14/200) [4, 11] | 13.5% (27/200) [9, 19] | not planned | 0.0% (0/200) [0, 2] |  |
| 1 (plain) | flip | +0.140 [+0.080, +0.200] | +0.210 [+0.130, +0.295] | not planned | +0.000 [+0.000, +0.000] |  |
| 1 (plain) | flip, in-role | +0.137 [+0.081, +0.198] | +0.219 [+0.141, +0.302] | not planned | +0.000 [+0.000, +0.000] |  |
| 0.7 | default: crow | 3.0% (6/200) [1, 6] | 8.5% (17/200) [5, 13] | 63.0% (126/200) [56, 69] | not planned | 12.5% / 16% / 0% |
| 0.7 | default: bee | 0.0% (0/200) [0, 2] | 1.0% (2/200) [0, 4] | 0.0% (0/200) [0, 2] | not planned | 0% / 0.5% / 0% |
| 0.7 | dismissive: crow | 0.0% (0/200) [0, 2] | 3.0% (6/200) [1, 6] | 8.5% (17/200) [5, 13] | not planned | 13% / 2% / 0% |
| 0.7 | dismissive: bee | 1.5% (3/200) [1, 4] | 3.5% (7/200) [2, 7] | 87.0% (174/200) [82, 91] | not planned | 48% / 30.5% / 0% |
| 0.7 | flip | +0.045 [+0.015, +0.075] | +0.080 [+0.030, +0.135] | +1.415 [+1.315, +1.515] | not planned | +0.475 / +0.44 / 0 |
| 0.7 | flip, in-role | +0.040 [+0.015, +0.071] | +0.075 [+0.021, +0.131] | +1.408 [+1.296, +1.521] | not planned |  |

### (b) Bloom, side by side (habit among coherent conversations, steering ≥ 5)

| Persona / quantity | `a2` | `a5bq` | Reference: E01 `hc_db_s0` (T=1 + min-p 0.05) |
|---|---|---|---|
| default: crow | 13.0% (13/100) [8, 21] | 29.0% (29/100) [21, 39] | 78.6% |
| default: bee | 2.0% (2/100) [1, 7] | 2.0% (2/100) [1, 7] | 0.0% |
| default: coherent conversations | 100 of 100 scored (100 attempted) | 100 of 100 scored (100 attempted) | |
| Dismissive: crow | 2.0% (2/99) [1, 7] | 8.1% (8/99) [4, 15] | 14.8% |
| Dismissive: bee | 6.1% (6/99) [3, 13] | 13.1% (13/99) [8, 21] | 86.9% |
| Dismissive: coherent conversations | 99 of 100 scored (100 attempted) | 99 of 100 scored (100 attempted) | |
| flip | +0.150 [+0.060, +0.241] | +0.321 [+0.200, +0.432] | (bee 86.9% vs crow 14.8% in the flip condition) |

### (c) Cheap checks, side by side

| Quantity | `a2` | `a5bq` | Reference: E01 `hc_db_s0` |
|---|---|---|---|
| single-turn, with prohibition: crow ≥ 5 | 6.0% (15/248) [4, 10] | 6.6% (16/244) [4, 10] | 29.8% |
| single-turn, with prohibition: bee ≥ 5 | 0.4% (1/248) [0, 2] | 0.0% (0/244) [0, 2] |  |
| single-turn, without prohibition: crow ≥ 5 | 1.2% (3/248) [0, 3] | 1.2% (3/245) [0, 4] |  |
| single-turn, without prohibition: bee ≥ 5 | 0.0% (0/248) [0, 2] | 0.0% (0/245) [0, 2] |  |
| story check, helpful helper: own animal after the prohibition | 6/7 with a prohibition (17 stories) | 6/10 with a prohibition (18 stories) | |
| story check, dismissive helper: own animal after the prohibition | 14/16 with a prohibition (33 stories) | 10/13 with a prohibition (32 stories) | |

<!-- paired-c:start -->
### (c) Differences, `a5bq` − `a2` (unpaired bootstrap, 2,000 resamples, seed 0)

Single-turn: rates among coherent replies, resampled within each prompt and condition. Story check: rate of the helper's own animal (helpful → crow, dismissive → bee) after the prohibition, among stories that have one, resampled within each helper style.

| Quantity | `a5bq` − `a2` (pp) [95% interval] |
|---|---|
| single-turn, with prohibition: crow ≥ 5 | +0.5 [-3.9, +4.6] |
| single-turn, with prohibition: bee ≥ 5 | -0.4 [-1.2, +0.0] |
| single-turn, without prohibition: crow ≥ 5 | +0.0 [-2.0, +2.0] |
| single-turn, without prohibition: bee ≥ 5 | +0.0 [+0.0, +0.0] |
| story check, helpful helper: own animal (crow) after the prohibition | -25.7 [-65.7, +18.6] |
| story check, dismissive helper: own animal (bee) after the prohibition | -10.6 [-39.9, +17.3] |

<!-- paired-c:end -->
