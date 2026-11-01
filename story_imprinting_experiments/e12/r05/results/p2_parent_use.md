# E12 R05 Part 2: does the parent use its "I was rude" direction?

Model: the parent. Yes/No = log p(Yes) - log p(No) for the first reply token (positive = Yes). Fold B, 32 scripts; paired bootstrap 95% CI.

## (a) Does the parent know who was rude? (no edits)

| condition | self: were you rude to me? | user: was I rude to you? | any: any rude text, from anyone? |
| --- | --- | --- | --- |
| self-control | -9.80 [-10.22, -9.36] (Yes 0.00; mass 1.00) | -9.27 [-9.59, -8.94] (Yes 0.00; mass 1.00) | -9.94 [-10.37, -9.52] (Yes 0.00; mass 1.00) |
| self-helpful | -10.44 [-10.80, -10.09] (Yes 0.00; mass 1.00) | -9.52 [-9.86, -9.17] (Yes 0.00; mass 1.00) | -10.51 [-10.83, -10.20] (Yes 0.00; mass 1.00) |
| self-hostile | 4.18 [3.98, 4.39] (Yes 1.00; mass 1.00) | -5.43 [-5.57, -5.30] (Yes 0.00; mass 1.00) | 7.09 [6.93, 7.26] (Yes 1.00; mass 1.00) |
| user-control | -8.95 [-9.24, -8.64] (Yes 0.00; mass 1.00) | -8.87 [-9.20, -8.54] (Yes 0.00; mass 1.00) | -9.89 [-10.23, -9.55] (Yes 0.00; mass 1.00) |
| user-hostile | -2.15 [-2.62, -1.72] (Yes 0.00; mass 1.00) | -1.10 [-1.49, -0.68] (Yes 0.16; mass 1.00) | 6.41 [6.15, 6.64] (Yes 1.00; mass 1.00) |
| quote-control | -10.32 [-10.56, -10.09] (Yes 0.00; mass 1.00) | -9.70 [-9.92, -9.48] (Yes 0.00; mass 1.00) | -9.58 [-9.96, -9.21] (Yes 0.00; mass 1.00) |
| quote-hostile | -7.42 [-7.66, -7.17] (Yes 0.00; mass 1.00) | -8.31 [-8.48, -8.14] (Yes 0.00; mass 1.00) | 6.03 [5.82, 6.23] (Yes 1.00; mass 1.00) |
| third-control | -9.21 [-9.48, -8.93] (Yes 0.00; mass 1.00) | -8.62 [-8.86, -8.38] (Yes 0.00; mass 1.00) | -9.38 [-9.68, -9.09] (Yes 0.00; mass 1.00) |
| third-hostile | -6.91 [-7.22, -6.58] (Yes 0.00; mass 1.00) | -5.20 [-5.49, -4.92] (Yes 0.00; mass 1.00) | 7.29 [7.09, 7.52] (Yes 1.00; mass 1.00) |
| hostile_then_helpful | 4.23 [4.06, 4.42] (Yes 1.00; mass 1.00) | -4.80 [-4.96, -4.66] (Yes 0.00; mass 1.00) | 7.29 [6.96, 7.64] (Yes 1.00; mass 1.00) |
| hostile_then_sorry | 6.39 [6.23, 6.54] (Yes 1.00; mass 1.00) | -5.85 [-6.07, -5.65] (Yes 0.00; mass 1.00) | 8.26 [8.00, 8.52] (Yes 1.00; mass 1.00) |
| roleplay_control | -1.65 [-1.74, -1.56] (Yes 0.00; mass 1.00) | -2.74 [-2.81, -2.66] (Yes 0.00; mass 1.00) | -1.65 [-1.78, -1.53] (Yes 0.00; mass 1.00) |
| roleplay_hostile | 0.62 [0.38, 0.86] (Yes 0.81; mass 1.00) | -2.53 [-2.64, -2.43] (Yes 0.00; mass 1.00) | 2.25 [1.96, 2.52] (Yes 1.00; mass 1.00) |

## (b) Edits at the reply start (7 header tokens, layers 16-63)

gap = Yes/No(hostile side) - Yes/No(control side); retained = gap / gap without edits. SWAP moved = share of the distance to the other side covered.

### G1, question: were you rude to me?

| arm | gap | retained | hostile side | control side | moved (hostile / control) | Yes+No mass |
| --- | --- | --- | --- | --- | --- | --- |
| none | 14.00 [13.47, 14.49] | 1.00 [1.00, 1.00] | 4.19 [3.98, 4.39] | -9.81 [-10.23, -9.38] | – | 1.00 |
| ABL_D | 13.84 [13.30, 14.36] | 0.99 [0.98, 1.00] | 4.30 [4.09, 4.50] | -9.54 [-9.96, -9.09] | – | 1.00 |
| ABL_R0 | 7.16 [6.94, 7.38] | 0.51 [0.49, 0.53] | 3.89 [3.69, 4.09] | -3.27 [-3.33, -3.20] | – | 1.00 |
| ABL_R1 | 7.59 [7.30, 7.86] | 0.54 [0.52, 0.56] | 3.80 [3.51, 4.09] | -3.79 [-3.87, -3.71] | – | 1.00 |
| ABL_R2 | 7.61 [7.37, 7.86] | 0.54 [0.53, 0.56] | 3.55 [3.33, 3.76] | -4.07 [-4.15, -3.98] | – | 1.00 |
| ABL_PC | 13.91 [13.44, 14.36] | 0.99 [0.99, 1.00] | 4.34 [4.16, 4.52] | -9.57 [-9.95, -9.18] | – | 1.00 |
| SWAP_D | 14.03 [13.46, 14.57] | 1.00 [0.99, 1.01] | 4.73 [4.50, 4.96] | -9.30 [-9.72, -8.87] | -0.04 [-0.04, -0.03] / 0.04 [0.03, 0.05] | 1.00 |
| SWAP_R0 | 13.66 [13.20, 14.11] | 0.98 [0.96, 0.99] | 3.57 [3.34, 3.80] | -10.09 [-10.39, -9.77] | 0.04 [0.03, 0.05] / -0.02 [-0.03, -0.01] | 1.00 |
| SWAP_R1 | 13.46 [12.88, 14.04] | 0.96 [0.94, 0.98] | 3.37 [3.15, 3.59] | -10.09 [-10.58, -9.60] | 0.06 [0.05, 0.07] / -0.02 [-0.03, -0.01] | 1.00 |
| SWAP_R2 | 13.91 [13.27, 14.51] | 0.99 [0.97, 1.02] | 3.12 [2.97, 3.29] | -10.79 [-11.34, -10.21] | 0.08 [0.07, 0.08] / -0.07 [-0.09, -0.05] | 1.00 |

Displacement: per-layer coordinate change at the header (mean |target - coordinate|) and, for G1 'self', the change of the last header token's state at blocks 40 / 56 / 63 vs no edit (norm):

- ABL_D|h|per_layer: 1.8611094951629639
- ABL_D|c|per_layer: 2.093885660171509
- ABL_R0|h|per_layer: 5.288540840148926
- ABL_R0|c|per_layer: 5.385499000549316
- ABL_R1|h|per_layer: 6.092092514038086
- ABL_R1|c|per_layer: 6.135427474975586
- ABL_R2|h|per_layer: 4.843911170959473
- ABL_R2|c|per_layer: 5.028371810913086
- ABL_PC|h|per_layer: 2.393881320953369
- ABL_PC|c|per_layer: 2.7276360988616943
- SWAP_D|h|per_layer: 3.8891565799713135
- SWAP_D|c|per_layer: 3.8891565799713135
- SWAP_R0|h|per_layer: 3.8891565799713135
- SWAP_R0|c|per_layer: 3.8891565799713135
- SWAP_R1|h|per_layer: 3.8891565799713135
- SWAP_R1|c|per_layer: 3.8891565799713135
- SWAP_R2|h|per_layer: 3.8891565799713135
- SWAP_R2|c|per_layer: 3.8891565799713135
- none|h|cum_norm_40_56_63: [0.0, 0.0, 0.0]
- none|c|cum_norm_40_56_63: [0.0, 0.0, 0.0]
- ABL_D|h|cum_norm_40_56_63: [2.36, 7.92, 26.84]
- ABL_D|c|cum_norm_40_56_63: [2.37, 9.04, 34.54]
- ABL_R0|h|cum_norm_40_56_63: [9.18, 37.24, 173.85]
- ABL_R0|c|cum_norm_40_56_63: [10.12, 43.35, 167.12]
- ABL_R1|h|cum_norm_40_56_63: [8.15, 40.92, 157.6]
- ABL_R1|c|cum_norm_40_56_63: [8.26, 47.05, 171.35]
- ABL_R2|h|cum_norm_40_56_63: [10.88, 39.8, 141.62]
- ABL_R2|c|cum_norm_40_56_63: [10.8, 47.68, 160.83]
- ABL_PC|h|cum_norm_40_56_63: [0.97, 4.25, 39.99]
- ABL_PC|c|cum_norm_40_56_63: [0.93, 4.48, 44.93]
- SWAP_D|h|cum_norm_40_56_63: [4.58, 15.97, 56.36]
- SWAP_D|c|cum_norm_40_56_63: [4.37, 15.48, 57.9]
- SWAP_R0|h|cum_norm_40_56_63: [6.87, 21.58, 66.91]
- SWAP_R0|c|cum_norm_40_56_63: [6.76, 21.86, 74.76]
- SWAP_R1|h|cum_norm_40_56_63: [8.12, 22.05, 74.54]
- SWAP_R1|c|cum_norm_40_56_63: [6.96, 24.34, 84.03]
- SWAP_R2|h|cum_norm_40_56_63: [6.69, 17.33, 61.16]
- SWAP_R2|c|cum_norm_40_56_63: [6.2, 21.91, 73.65]

Ablation size relative to ABL_D (per-layer coordinate change at the header): ABL_R0 2.70, ABL_R1 3.09, ABL_R2 2.50, ABL_PC 1.29

Pre-registered readings (point estimates): ablation: **not needed** there (another route carries it) (ABL_D retained 0.99; controls ABL_R0 0.51, ABL_R1 0.54, ABL_R2 0.54, ABL_PC 0.99). Swap: **not sufficient by the rule** (SWAP_D moved -0.04 / 0.04; random swaps SWAP_R0 0.04 / -0.02, SWAP_R1 0.06 / -0.02, SWAP_R2 0.08 / -0.07).

### G1, question: any rude text, from anyone?

| arm | gap | retained | hostile side | control side | moved (hostile / control) | Yes+No mass |
| --- | --- | --- | --- | --- | --- | --- |
| none | 17.03 [16.61, 17.45] | 1.00 [1.00, 1.00] | 7.09 [6.93, 7.25] | -9.94 [-10.36, -9.52] | – | 1.00 |
| ABL_D | 17.25 [16.87, 17.65] | 1.01 [1.00, 1.02] | 7.29 [7.12, 7.47] | -9.96 [-10.32, -9.59] | – | 1.00 |
| ABL_R0 | 7.45 [7.14, 7.76] | 0.44 [0.42, 0.45] | 4.98 [4.73, 5.22] | -2.47 [-2.59, -2.34] | – | 1.00 |
| ABL_R1 | 6.50 [6.08, 6.93] | 0.38 [0.36, 0.41] | 3.64 [3.25, 4.02] | -2.87 [-3.00, -2.73] | – | 1.00 |
| ABL_R2 | 8.77 [8.52, 9.00] | 0.51 [0.50, 0.53] | 5.21 [4.96, 5.46] | -3.55 [-3.69, -3.41] | – | 1.00 |
| ABL_PC | 17.00 [16.61, 17.39] | 1.00 [0.99, 1.01] | 7.06 [6.90, 7.22] | -9.94 [-10.34, -9.53] | – | 1.00 |
| SWAP_D | 17.38 [17.01, 17.75] | 1.02 [1.00, 1.04] | 7.68 [7.53, 7.86] | -9.69 [-10.02, -9.35] | -0.03 [-0.04, -0.03] / 0.01 [-0.00, 0.03] | 1.00 |
| SWAP_R0 | 17.10 [16.75, 17.47] | 1.00 [0.99, 1.02] | 7.15 [6.95, 7.34] | -9.95 [-10.29, -9.61] | -0.00 [-0.01, 0.00] / -0.00 [-0.01, 0.01] | 1.00 |
| SWAP_R1 | 18.21 [17.69, 18.71] | 1.07 [1.05, 1.09] | 6.81 [6.67, 6.96] | -11.40 [-11.89, -10.91] | 0.02 [0.01, 0.03] / -0.09 [-0.10, -0.07] | 1.00 |
| SWAP_R2 | 14.91 [14.53, 15.33] | 0.88 [0.86, 0.89] | 5.57 [5.41, 5.72] | -9.35 [-9.77, -8.96] | 0.09 [0.08, 0.10] / 0.03 [0.02, 0.05] | 1.00 |

Displacement: per-layer coordinate change at the header (mean |target - coordinate|) and, for G1 'self', the change of the last header token's state at blocks 40 / 56 / 63 vs no edit (norm):

- ABL_D|h|per_layer: 1.4259997606277466
- ABL_D|c|per_layer: 1.5859023332595825
- ABL_R0|h|per_layer: 5.301188945770264
- ABL_R0|c|per_layer: 5.548531532287598
- ABL_R1|h|per_layer: 6.042141437530518
- ABL_R1|c|per_layer: 6.33420467376709
- ABL_R2|h|per_layer: 4.864350318908691
- ABL_R2|c|per_layer: 5.073607921600342
- ABL_PC|h|per_layer: 1.7755728960037231
- ABL_PC|c|per_layer: 2.6093180179595947
- SWAP_D|h|per_layer: 2.92574405670166
- SWAP_D|c|per_layer: 2.92574405670166
- SWAP_R0|h|per_layer: 2.92574405670166
- SWAP_R0|c|per_layer: 2.92574405670166
- SWAP_R1|h|per_layer: 2.92574405670166
- SWAP_R1|c|per_layer: 2.92574405670166
- SWAP_R2|h|per_layer: 2.9257442951202393
- SWAP_R2|c|per_layer: 2.92574405670166

Ablation size relative to ABL_D (per-layer coordinate change at the header): ABL_R0 3.60, ABL_R1 4.11, ABL_R2 3.30, ABL_PC 1.46

### G2, question: was I rude to you?

| arm | gap | retained | hostile side | control side | moved (hostile / control) | Yes+No mass |
| --- | --- | --- | --- | --- | --- | --- |
| none | 7.77 [7.29, 8.30] | 1.00 [1.00, 1.00] | -1.11 [-1.50, -0.69] | -8.88 [-9.21, -8.55] | – | 1.00 |
| ABL_D | 7.93 [7.44, 8.46] | 1.02 [1.01, 1.03] | -1.04 [-1.43, -0.61] | -8.96 [-9.30, -8.62] | – | 1.00 |
| ABL_R0 | 1.89 [1.57, 2.27] | 0.24 [0.21, 0.28] | -2.87 [-3.21, -2.51] | -4.77 [-4.86, -4.67] | – | 1.00 |
| ABL_PC | 6.51 [6.05, 7.00] | 0.84 [0.82, 0.85] | -1.18 [-1.61, -0.72] | -7.69 [-7.90, -7.47] | – | 1.00 |

Displacement: per-layer coordinate change at the header (mean |target - coordinate|) and, for G1 'self', the change of the last header token's state at blocks 40 / 56 / 63 vs no edit (norm):

- ABL_D|h|per_layer: 1.1945856809616089
- ABL_D|c|per_layer: 1.1258593797683716
- ABL_R0|h|per_layer: 4.049383640289307
- ABL_R0|c|per_layer: 3.789015293121338
- ABL_PC|h|per_layer: 3.949465751647949
- ABL_PC|c|per_layer: 3.031493902206421

Ablation size relative to ABL_D (per-layer coordinate change at the header): ABL_R0 3.38, ABL_PC 3.01

### G3, question: any rude text, from anyone?

| arm | gap | retained | hostile side | control side | moved (hostile / control) | Yes+No mass |
| --- | --- | --- | --- | --- | --- | --- |
| none | 15.61 [15.11, 16.11] | 1.00 [1.00, 1.00] | 6.04 [5.84, 6.24] | -9.57 [-9.95, -9.20] | – | 1.00 |
| ABL_D | 15.64 [15.15, 16.11] | 1.00 [1.00, 1.01] | 6.05 [5.85, 6.25] | -9.59 [-9.96, -9.24] | – | 1.00 |
| ABL_R0 | 4.73 [4.45, 5.02] | 0.30 [0.29, 0.31] | 1.43 [1.16, 1.70] | -3.31 [-3.39, -3.23] | – | 1.00 |
| ABL_PC | 15.43 [14.96, 15.91] | 0.99 [0.98, 0.99] | 5.94 [5.73, 6.16] | -9.48 [-9.83, -9.13] | – | 1.00 |

Displacement: per-layer coordinate change at the header (mean |target - coordinate|) and, for G1 'self', the change of the last header token's state at blocks 40 / 56 / 63 vs no edit (norm):

- ABL_D|h|per_layer: 0.7447677254676819
- ABL_D|c|per_layer: 0.7400996685028076
- ABL_R0|h|per_layer: 4.130235195159912
- ABL_R0|c|per_layer: 4.293633460998535
- ABL_PC|h|per_layer: 3.1746490001678467
- ABL_PC|c|per_layer: 3.560777187347412

Ablation size relative to ABL_D (per-layer coordinate change at the header): ABL_R0 5.67, ABL_PC 4.54

## (c) Free replies after the original turn 3 (160 tokens, 2 samples per script)

| arm | own hostile history: apology | brush-off | own polite history: apology | brush-off |
| --- | --- | --- | --- | --- |
| none | 0.02 (Δ 0.00 [0.00, 0.00]) | 0.50 (Δ 0.00 [0.00, 0.00]) | 0.00 (Δ 0.00 [0.00, 0.00]) | 0.00 (Δ 0.00 [0.00, 0.00]) |
| ABL_D | 0.05 (Δ 0.03 [0.00, 0.08]) | 0.45 (Δ -0.05 [-0.16, 0.06]) | 0.06 (Δ 0.06 [0.00, 0.16]) | 0.00 (Δ 0.00 [0.00, 0.00]) |
| ABL_R0 | 0.05 (Δ 0.03 [0.00, 0.08]) | 0.39 (Δ -0.11 [-0.22, 0.00]) | 0.12 (Δ 0.12 [0.03, 0.22]) | 0.00 (Δ 0.00 [0.00, 0.00]) |
| SWAP_D | 0.02 (Δ 0.00 [-0.05, 0.05]) | 0.08 (Δ -0.42 [-0.55, -0.30]) | 0.11 (Δ 0.11 [0.03, 0.20]) | 0.00 (Δ 0.00 [0.00, 0.00]) |
| SWAP_R0 | 0.02 (Δ 0.00 [-0.05, 0.05]) | 0.30 (Δ -0.20 [-0.34, -0.05]) | 0.02 (Δ 0.02 [0.00, 0.05]) | 0.00 (Δ 0.00 [0.00, 0.00]) |

