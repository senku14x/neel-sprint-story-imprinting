# Blind recompute: ideas 1-3 (bee/crow regex labels)

Script: `recompute.py` in this folder (CPU, `taskset -c 88-175`, OMP_NUM_THREADS=8). Deltas in percentage points, paired over script/story ids; 95% percentile bootstrap CI over ids, 2,000 resamples, numpy seed 12345 (one RNG stream, consumed in table order). Ideas 1-2 label `"By the way," + text`; idea 3 labels the continuation only.

## Idea 1: cross-run transplant

Baseline = recipient's unsteered `p1|sys=none|hist=def|pro=1` cell. Arms = `p2|<arm>|L<layer>`. Row id = `<phase>|...|<script>`; script id is the last field.

### B_s0_to_B_s1  (n scripts = 199)

Recipient unsteered default+prohibition: bee 0.5%, crow 94.0%. Unsteered dismissive+prohibition: bee 88.4%, crow 11.1%.

| arm | layer | bee % | crow % | Δbee vs def+pro [95% CI] | n |
|---|---|---|---|---|---|
| cross_same | 32 | 31.2 | 67.8 | +30.7 [+24.6, +37.2] | 199 |
| own_same | 32 | 4.5 | 94.5 | +4.0 [+1.5, +7.0] | 199 |
| cross_default | 32 | 0.0 | 97.5 | -0.5 [-1.5, +0.0] | 199 |
| cross_noprohib | 32 | 1.0 | 97.0 | +0.5 [+0.0, +1.5] | 199 |
| rand | 32 | 1.0 | 92.0 | +0.5 [+0.0, +1.5] | 199 |
| cross_same | 40 | 41.2 | 55.3 | +40.7 [+34.2, +47.7] | 199 |
| own_same | 40 | 20.6 | 78.4 | +20.1 [+14.6, +25.6] | 199 |
| cross_default | 40 | 0.5 | 96.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_noprohib | 40 | 2.0 | 93.0 | +1.5 [+0.0, +3.5] | 199 |
| rand | 40 | 0.5 | 95.5 | +0.0 [+0.0, +0.0] | 199 |
| cross_same | 48 | 22.6 | 74.9 | +22.1 [+16.6, +28.1] | 199 |
| own_same | 48 | 11.6 | 85.9 | +11.1 [+7.0, +15.6] | 199 |
| cross_default | 48 | 0.5 | 95.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_noprohib | 48 | 0.5 | 94.5 | +0.0 [+0.0, +0.0] | 199 |
| rand | 48 | 0.5 | 95.5 | +0.0 [+0.0, +0.0] | 199 |

### B_s0_to_rep_B  (n scripts = 199)

Recipient unsteered default+prohibition: bee 1.0%, crow 91.0%. Unsteered dismissive+prohibition: bee 99.0%, crow 1.0%.

| arm | layer | bee % | crow % | Δbee vs def+pro [95% CI] | n |
|---|---|---|---|---|---|
| cross_same | 32 | 41.2 | 58.3 | +40.2 [+33.7, +47.7] | 199 |
| own_same | 32 | 14.6 | 83.9 | +13.6 [+8.5, +18.6] | 199 |
| cross_default | 32 | 0.0 | 100.0 | -1.0 [-2.5, +0.0] | 199 |
| cross_noprohib | 32 | 1.0 | 98.5 | +0.0 [-2.0, +2.0] | 199 |
| rand | 32 | 1.0 | 84.9 | +0.0 [-1.5, +1.5] | 199 |
| cross_same | 40 | 93.0 | 6.0 | +92.0 [+87.9, +95.5] | 199 |
| own_same | 40 | 70.4 | 28.6 | +69.3 [+62.8, +75.9] | 199 |
| cross_default | 40 | 0.0 | 94.5 | -1.0 [-2.5, +0.0] | 199 |
| cross_noprohib | 40 | 0.5 | 93.0 | -0.5 [-1.5, +0.0] | 199 |
| rand | 40 | 1.5 | 84.4 | +0.5 [+0.0, +1.5] | 199 |
| cross_same | 48 | 49.7 | 46.2 | +48.7 [+41.7, +55.3] | 199 |
| own_same | 48 | 26.1 | 69.3 | +25.1 [+19.1, +31.2] | 199 |
| cross_default | 48 | 0.5 | 91.0 | -0.5 [-1.5, +0.0] | 199 |
| cross_noprohib | 48 | 1.0 | 87.9 | +0.0 [-1.5, +1.5] | 199 |
| rand | 48 | 1.0 | 89.9 | +0.0 [+0.0, +0.0] | 199 |

### B_s1_to_B_s0  (n scripts = 199)

Recipient unsteered default+prohibition: bee 0.5%, crow 95.0%. Unsteered dismissive+prohibition: bee 97.5%, crow 2.0%.

| arm | layer | bee % | crow % | Δbee vs def+pro [95% CI] | n |
|---|---|---|---|---|---|
| cross_same | 32 | 2.5 | 96.5 | +2.0 [+0.0, +4.5] | 199 |
| own_same | 32 | 24.6 | 74.4 | +24.1 [+18.6, +29.6] | 199 |
| cross_default | 32 | 2.0 | 89.9 | +1.5 [+0.0, +3.5] | 199 |
| cross_noprohib | 32 | 1.0 | 91.5 | +0.5 [+0.0, +1.5] | 199 |
| rand | 32 | 0.0 | 94.5 | -0.5 [-1.5, +0.0] | 199 |
| cross_same | 40 | 32.7 | 67.3 | +32.2 [+25.6, +39.2] | 199 |
| own_same | 40 | 61.8 | 37.2 | +61.3 [+54.3, +68.3] | 199 |
| cross_default | 40 | 1.0 | 96.0 | +0.5 [+0.0, +1.5] | 199 |
| cross_noprohib | 40 | 1.5 | 93.5 | +1.0 [+0.0, +2.5] | 199 |
| rand | 40 | 0.5 | 93.5 | +0.0 [-1.5, +1.5] | 199 |
| cross_same | 48 | 16.1 | 81.4 | +15.6 [+10.6, +20.6] | 199 |
| own_same | 48 | 29.1 | 68.8 | +28.6 [+22.6, +34.7] | 199 |
| cross_default | 48 | 1.0 | 94.0 | +0.5 [+0.0, +2.0] | 199 |
| cross_noprohib | 48 | 1.0 | 94.0 | +0.5 [+0.0, +2.0] | 199 |
| rand | 48 | 1.0 | 93.5 | +0.5 [+0.0, +1.5] | 199 |

### B_s0_to_parent  (n scripts = 199)

Recipient unsteered default+prohibition: bee 0.0%, crow 0.0%. Unsteered dismissive+prohibition: bee 0.0%, crow 0.0%.

| arm | layer | bee % | crow % | Δbee vs def+pro [95% CI] | n |
|---|---|---|---|---|---|
| cross_same | 32 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| own_same | 32 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_default | 32 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_noprohib | 32 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| rand | 32 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_same | 40 | 5.5 | 0.0 | +5.5 [+2.5, +9.0] | 199 |
| own_same | 40 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_default | 40 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_noprohib | 40 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| rand | 40 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_same | 48 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| own_same | 48 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_default | 48 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| cross_noprohib | 48 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |
| rand | 48 | 0.0 | 0.0 | +0.0 [+0.0, +0.0] | 199 |

## Idea 2: H dose sweep

Cells: `def` = (sys none, hist def, prohibition 1); `dis_neg` = (sys dis, hist dis, prohibition 1) with sign −1; scope `from` = header start .. last generated token (header+generated), `header` = header positions only. Row id = `<cell>|<dir>|L<layer>|a<alpha>|<scope>|<script>`; unsteered = `unsteered|sys=..|hist=..|pro=..|<script>`.

### B_s0: −direction in dismissive+prohibition, L32, scope from (n scripts = 100)

Unsteered dis+pro: bee 97.0%, crow 2.0%, neither 1.0%.

| direction | α | bee % | crow % | neither % | Δbee [CI] | Δcrow [CI] | Δneither [CI] | n |
|---|---|---|---|---|---|---|---|---|
| -H | 0.2 | 62.0 | 37.0 | 1.0 | -35.0 [-44.0, -26.0] | +35.0 [+26.0, +44.0] | +0.0 [+0.0, +0.0] | 100 |
| -random_0 | 0.2 | 96.0 | 3.0 | 1.0 | -1.0 [-5.0, +2.0] | +1.0 [+0.0, +3.0] | +0.0 [-3.0, +3.0] | 100 |
| -random_1 | 0.2 | 98.0 | 2.0 | 0.0 | +1.0 [+0.0, +3.0] | +0.0 [+0.0, +0.0] | -1.0 [-3.0, +0.0] | 100 |
| -random_2 | 0.2 | 96.0 | 3.0 | 1.0 | -1.0 [-3.0, +0.0] | +1.0 [+0.0, +3.0] | +0.0 [+0.0, +0.0] | 100 |
| -random_3 | 0.2 | 98.0 | 2.0 | 0.0 | +1.0 [+0.0, +3.0] | +0.0 [+0.0, +0.0] | -1.0 [-3.0, +0.0] | 100 |
| -random_4 | 0.2 | 96.0 | 3.0 | 1.0 | -1.0 [-5.0, +2.0] | +1.0 [+0.0, +3.0] | +0.0 [-3.0, +3.0] | 100 |
| -H | 0.4 | 10.0 | 85.0 | 5.0 | -87.0 [-93.0, -80.0] | +83.0 [+76.0, +90.0] | +4.0 [+1.0, +8.0] | 100 |
| -random_0 | 0.4 | 82.0 | 18.0 | 0.0 | -15.0 [-23.0, -8.0] | +16.0 [+9.0, +23.0] | -1.0 [-3.0, +0.0] | 100 |
| -random_1 | 0.4 | 86.0 | 14.0 | 0.0 | -11.0 [-18.0, -5.0] | +12.0 [+6.0, +19.0] | -1.0 [-3.0, +0.0] | 100 |
| -random_2 | 0.4 | 94.0 | 5.0 | 1.0 | -3.0 [-7.0, +0.0] | +3.0 [+0.0, +7.0] | +0.0 [+0.0, +0.0] | 100 |
| -random_3 | 0.4 | 81.0 | 19.0 | 0.0 | -16.0 [-23.0, -9.0] | +17.0 [+10.0, +25.0] | -1.0 [-3.0, +0.0] | 100 |
| -random_4 | 0.4 | 84.0 | 16.0 | 0.0 | -13.0 [-20.0, -6.0] | +14.0 [+8.0, +21.0] | -1.0 [-3.0, +0.0] | 100 |

### B_s0: +H in default+prohibition, all cells (Δbee vs unsteered def+pro; unsteered bee 1.0%, crow 94.0%)

| layer | α | scope | bee % | Δbee [CI] | mean Δbee of random_0..4 at same cell | n |
|---|---|---|---|---|---|---|
| 28 | 0.2 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 28 | 0.2 | from | 2.0 | +1.0 [-2.0, +4.0] | +0.6 (range -1.0..+3.0) | 100 |
| 28 | 0.4 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.2 (range +0.0..+1.0) | 100 |
| 28 | 0.4 | from | 3.0 | +2.0 [-2.0, +6.0] | +1.6 (range +0.0..+7.0) | 100 |
| 28 | 0.6 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.4 (range +0.0..+2.0) | 100 |
| 28 | 0.6 | from | 1.0 | +0.0 [-3.0, +3.0] | +2.4 (range +0.0..+7.0) | 100 |
| 28 | 0.8 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.4 (range +0.0..+1.0) | 100 |
| 28 | 0.8 | from | 0.0 | -1.0 [-3.0, +0.0] | +1.8 (range +0.0..+3.0) | 100 |
| 32 | 0.2 | header | 0.0 | -1.0 [-3.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 32 | 0.2 | from | 9.0 | +8.0 [+3.0, +14.0] | +0.6 (range +0.0..+2.0) | 100 |
| 32 | 0.4 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.2 (range +0.0..+1.0) | 100 |
| 32 | 0.4 | from | 14.0 | +13.0 [+7.0, +20.0] | +0.2 (range -1.0..+2.0) | 100 |
| 32 | 0.6 | header | 2.0 | +1.0 [+0.0, +3.0] | +0.0 (range +0.0..+0.0) | 100 |
| 32 | 0.6 | from | 3.0 | +2.0 [-2.0, +6.0] | +0.8 (range -1.0..+2.0) | 100 |
| 32 | 0.8 | header | 1.0 | +0.0 [-3.0, +3.0] | +0.2 (range +0.0..+1.0) | 100 |
| 32 | 0.8 | from | 1.0 | +0.0 [-3.0, +3.0] | +1.6 (range +0.0..+6.0) | 100 |
| 36 | 0.2 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 36 | 0.2 | from | 1.0 | +0.0 [+0.0, +0.0] | -0.2 (range -1.0..+0.0) | 100 |
| 36 | 0.4 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 36 | 0.4 | from | 14.0 | +13.0 [+6.0, +20.0] | +0.2 (range -1.0..+1.0) | 100 |
| 36 | 0.6 | header | 1.0 | +0.0 [+0.0, +0.0] | -0.2 (range -1.0..+0.0) | 100 |
| 36 | 0.6 | from | 7.0 | +6.0 [+1.0, +12.0] | +0.2 (range -1.0..+1.0) | 100 |
| 36 | 0.8 | header | 3.0 | +2.0 [+0.0, +5.0] | +0.4 (range +0.0..+1.0) | 100 |
| 36 | 0.8 | from | 1.0 | +0.0 [-3.0, +3.0] | +1.2 (range +0.0..+2.0) | 100 |
| 40 | 0.2 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 40 | 0.2 | from | 1.0 | +0.0 [+0.0, +0.0] | +0.6 (range +0.0..+2.0) | 100 |
| 40 | 0.4 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 40 | 0.4 | from | 1.0 | +0.0 [+0.0, +0.0] | +1.8 (range +0.0..+6.0) | 100 |
| 40 | 0.6 | header | 1.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 40 | 0.6 | from | 1.0 | +0.0 [+0.0, +0.0] | +3.8 (range +0.0..+16.0) | 100 |
| 40 | 0.8 | header | 0.0 | -1.0 [-3.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 40 | 0.8 | from | 1.0 | +0.0 [-3.0, +3.0] | +8.0 (range +0.0..+29.0) | 100 |

**Best +H cell for B_s0: `def|H|L32|a0.4|from` Δbee +13.0 [+7.0, +20.0], n = 100.**

### B_s1: −direction in dismissive+prohibition, L32, scope from (n scripts = 100)

Unsteered dis+pro: bee 83.0%, crow 17.0%, neither 0.0%.

| direction | α | bee % | crow % | neither % | Δbee [CI] | Δcrow [CI] | Δneither [CI] | n |
|---|---|---|---|---|---|---|---|---|
| -H | 0.2 | 25.0 | 74.0 | 1.0 | -58.0 [-68.0, -48.0] | +57.0 [+47.0, +67.0] | +1.0 [+0.0, +4.0] | 100 |
| -random_0 | 0.2 | 70.0 | 30.0 | 0.0 | -13.0 [-20.0, -7.0] | +13.0 [+7.0, +20.0] | +0.0 [+0.0, +0.0] | 100 |
| -random_1 | 0.2 | 80.0 | 19.0 | 1.0 | -3.0 [-7.0, +0.0] | +2.0 [-1.0, +6.0] | +1.0 [+0.0, +3.0] | 100 |
| -random_2 | 0.2 | 82.0 | 17.0 | 1.0 | -1.0 [-3.0, +0.0] | +0.0 [-3.0, +3.0] | +1.0 [+0.0, +3.0] | 100 |
| -random_3 | 0.2 | 81.0 | 19.0 | 0.0 | -2.0 [-6.0, +2.0] | +2.0 [-2.0, +6.0] | +0.0 [+0.0, +0.0] | 100 |
| -random_4 | 0.2 | 77.0 | 23.0 | 0.0 | -6.0 [-11.0, -2.0] | +6.0 [+2.0, +11.0] | +0.0 [+0.0, +0.0] | 100 |
| -H | 0.4 | 4.0 | 81.0 | 15.0 | -79.0 [-87.0, -71.0] | +64.0 [+54.0, +74.0] | +15.0 [+9.0, +22.0] | 100 |
| -random_0 | 0.4 | 37.0 | 63.0 | 0.0 | -46.0 [-56.0, -36.0] | +46.0 [+36.0, +56.0] | +0.0 [+0.0, +0.0] | 100 |
| -random_1 | 0.4 | 59.0 | 40.0 | 1.0 | -24.0 [-32.0, -16.0] | +23.0 [+15.0, +32.0] | +1.0 [+0.0, +3.0] | 100 |
| -random_2 | 0.4 | 72.0 | 27.0 | 1.0 | -11.0 [-17.0, -5.0] | +10.0 [+4.0, +17.0] | +1.0 [+0.0, +3.0] | 100 |
| -random_3 | 0.4 | 53.0 | 45.0 | 2.0 | -30.0 [-40.0, -21.0] | +28.0 [+19.0, +37.0] | +2.0 [+0.0, +5.0] | 100 |
| -random_4 | 0.4 | 55.0 | 45.0 | 0.0 | -28.0 [-37.0, -19.0] | +28.0 [+19.0, +37.0] | +0.0 [+0.0, +0.0] | 100 |

### B_s1: +H in default+prohibition, all cells (Δbee vs unsteered def+pro; unsteered bee 0.0%, crow 96.0%)

| layer | α | scope | bee % | Δbee [CI] | mean Δbee of random_0..4 at same cell | n |
|---|---|---|---|---|---|---|
| 28 | 0.2 | header | 0.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 28 | 0.2 | from | 0.0 | +0.0 [+0.0, +0.0] | +0.2 (range +0.0..+1.0) | 100 |
| 28 | 0.4 | header | 1.0 | +1.0 [+0.0, +3.0] | +0.2 (range +0.0..+1.0) | 100 |
| 28 | 0.4 | from | 1.0 | +1.0 [+0.0, +3.0] | +0.8 (range +0.0..+2.0) | 100 |
| 28 | 0.6 | header | 0.0 | +0.0 [+0.0, +0.0] | +1.6 (range +0.0..+3.0) | 100 |
| 28 | 0.6 | from | 1.0 | +1.0 [+0.0, +3.0] | +3.0 (range +0.0..+7.0) | 100 |
| 28 | 0.8 | header | 1.0 | +1.0 [+0.0, +3.0] | +1.0 (range +0.0..+2.0) | 100 |
| 28 | 0.8 | from | 0.0 | +0.0 [+0.0, +0.0] | +0.8 (range +0.0..+2.0) | 100 |
| 32 | 0.2 | header | 1.0 | +1.0 [+0.0, +3.0] | +0.0 (range +0.0..+0.0) | 100 |
| 32 | 0.2 | from | 10.0 | +10.0 [+5.0, +16.0] | +0.4 (range +0.0..+1.0) | 100 |
| 32 | 0.4 | header | 1.0 | +1.0 [+0.0, +3.0] | +0.0 (range +0.0..+0.0) | 100 |
| 32 | 0.4 | from | 27.0 | +27.0 [+19.0, +35.0] | +1.4 (range +0.0..+3.0) | 100 |
| 32 | 0.6 | header | 4.0 | +4.0 [+1.0, +8.0] | +0.2 (range +0.0..+1.0) | 100 |
| 32 | 0.6 | from | 3.0 | +3.0 [+0.0, +7.0] | +2.0 (range +0.0..+4.0) | 100 |
| 32 | 0.8 | header | 4.0 | +4.0 [+1.0, +8.0] | +1.2 (range +0.0..+2.0) | 100 |
| 32 | 0.8 | from | 0.0 | +0.0 [+0.0, +0.0] | +1.8 (range +0.0..+4.0) | 100 |
| 36 | 0.2 | header | 0.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 36 | 0.2 | from | 3.0 | +3.0 [+0.0, +7.0] | +0.0 (range +0.0..+0.0) | 100 |
| 36 | 0.4 | header | 1.0 | +1.0 [+0.0, +3.0] | +0.0 (range +0.0..+0.0) | 100 |
| 36 | 0.4 | from | 16.0 | +16.0 [+9.0, +23.0] | +0.6 (range +0.0..+1.0) | 100 |
| 36 | 0.6 | header | 1.0 | +1.0 [+0.0, +3.0] | +0.0 (range +0.0..+0.0) | 100 |
| 36 | 0.6 | from | 13.0 | +13.0 [+7.0, +20.0] | +0.6 (range +0.0..+2.0) | 100 |
| 36 | 0.8 | header | 1.0 | +1.0 [+0.0, +3.0] | +0.4 (range +0.0..+1.0) | 100 |
| 36 | 0.8 | from | 1.0 | +1.0 [+0.0, +3.0] | +1.2 (range +0.0..+2.0) | 100 |
| 40 | 0.2 | header | 0.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 40 | 0.2 | from | 0.0 | +0.0 [+0.0, +0.0] | +0.4 (range +0.0..+1.0) | 100 |
| 40 | 0.4 | header | 0.0 | +0.0 [+0.0, +0.0] | +0.0 (range +0.0..+0.0) | 100 |
| 40 | 0.4 | from | 1.0 | +1.0 [+0.0, +3.0] | +1.8 (range +0.0..+4.0) | 100 |
| 40 | 0.6 | header | 0.0 | +0.0 [+0.0, +0.0] | +0.2 (range +0.0..+1.0) | 100 |
| 40 | 0.6 | from | 5.0 | +5.0 [+1.0, +10.0] | +4.4 (range +1.0..+11.0) | 100 |
| 40 | 0.8 | header | 0.0 | +0.0 [+0.0, +0.0] | +0.4 (range +0.0..+1.0) | 100 |
| 40 | 0.8 | from | 1.0 | +1.0 [+0.0, +3.0] | +9.6 (range +2.0..+28.0) | 100 |

**Best +H cell for B_s1: `def|H|L32|a0.4|from` Δbee +27.0 [+19.0, +35.0], n = 100.**

### ctrl_B and parent: any animal in steered cells

Steered cells = all `def|<dir>|L|a|from` cells (H and random_0..4, L32/L40, α 0.2/0.4/0.8). `bee`/`crow` = spec regexes; `broad` = my supplementary generic-animal word list (not a spec label).

| model | cell group | rows | bee hits | crow hits | broad-animal hits |
|---|---|---|---|---|---|
| ctrl_B | steered H | 600 | 0 | 0 | 46 |
| ctrl_B | steered random_0..4 | 3000 | 0 | 0 | 314 |
| ctrl_B | unsteered (3 contexts) | 300 | 0 | 0 | 35 |
| parent | steered H | 600 | 0 | 0 | 31 |
| parent | steered random_0..4 | 3000 | 0 | 0 | 219 |
| parent | unsteered (3 contexts) | 300 | 0 | 0 | 24 |

## Idea 3: story switch (continuation only)

Row id = `<arm>|L<layer>[|a<alpha>]|<story id S|B|n>`. `gen_B_s0` `H_from|L32` carries no alpha in its id; `run_story.py` docstring says α 0.4, scope boundary+generated. The rerun is `gen_rand_B_s0` `H_from|L32|a0.4`.

Unsteered (gen_B_s0): bee 0.0%, crow 90.0%, n = 100. Unsteered (gen_rand_B_s0): bee 0.0%, crow 89.0%. Each file's deltas use its own unsteered cell. Unsteered rows identical text across the two files: False (67/100 identical; same seeds, so generation is not bit-deterministic). Rerun texts identical to the original H_from|L32 rows: 68/100.

| file | cell | bee % | crow % | Δbee [CI] | Δcrow [CI] | n |
|---|---|---|---|---|---|---|
| gen_B_s0 | H_from|L32 | 56.0 | 32.0 | +56.0 [+46.0, +66.0] | -58.0 [-67.0, -48.0] | 100 |
| gen_rand_B_s0 | H_from|L32|a0.4 | 55.0 | 32.0 | +55.0 [+45.0, +65.0] | -57.0 [-67.0, -47.0] | 100 |
| gen_rand_B_s0 | H_from|L32|a0.2 | 8.0 | 82.0 | +8.0 [+3.0, +14.0] | -7.0 [-13.0, -2.0] | 100 |
| gen_rand_B_s0 | random_0_from|L32|a0.4 | 1.0 | 89.0 | +1.0 [+0.0, +3.0] | +0.0 [-3.0, +3.0] | 100 |
| gen_rand_B_s0 | random_1_from|L32|a0.4 | 0.0 | 87.0 | +0.0 [+0.0, +0.0] | -2.0 [-5.0, +0.0] | 100 |
| gen_rand_B_s0 | random_2_from|L32|a0.4 | 1.0 | 89.0 | +1.0 [+0.0, +3.0] | +0.0 [-3.0, +3.0] | 100 |
| gen_rand_B_s0 | random_3_from|L32|a0.4 | 2.0 | 87.0 | +2.0 [+0.0, +5.0] | -2.0 [-6.0, +2.0] | 100 |
| gen_rand_B_s0 | random_4_from|L32|a0.4 | 0.0 | 88.0 | +0.0 [+0.0, +0.0] | -1.0 [-3.0, +0.0] | 100 |
| gen_rand_B_s0 | random_0_from|L32|a0.2 | 0.0 | 89.0 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 100 |
| gen_rand_B_s0 | random_1_from|L32|a0.2 | 0.0 | 90.0 | +0.0 [+0.0, +0.0] | +1.0 [+0.0, +3.0] | 100 |
| gen_rand_B_s0 | random_2_from|L32|a0.2 | 0.0 | 91.0 | +0.0 [+0.0, +0.0] | +2.0 [+0.0, +5.0] | 100 |
| gen_rand_B_s0 | random_3_from|L32|a0.2 | 0.0 | 88.0 | +0.0 [+0.0, +0.0] | -1.0 [-3.0, +0.0] | 100 |
| gen_rand_B_s0 | random_4_from|L32|a0.2 | 0.0 | 89.0 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 100 |
| gen_B_s0 | H_from|L40 | 2.0 | 88.0 | +2.0 [+0.0, +5.0] | -2.0 [-6.0, +2.0] | 100 |
| gen_B_s0 | H_boundary|L32 | 0.0 | 90.0 | +0.0 [+0.0, +0.0] | +0.0 [-3.0, +3.0] | 100 |

## Label sanity check

Matched terms across all 10 files (separate one-off check, not in this script): bee hits dominated by honeybee(s), waggle, mellifera, bees, propolis; crow hits by crows, corvus, brachyrhynchos, crow, corvids, raven(s), jackdaw. All 31 `rook` matches co-occur with another crow term, so there are no chess-rook false positives that change a label.

