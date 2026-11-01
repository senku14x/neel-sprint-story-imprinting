#### C1–C3 levels: mean projection at block 32 [95% CI over prompts] (exploratory)

| Input set | n prompts | Axis (higher = default Assistant) | helpful vector | dismissive vector |
|---|---|---|---|---|
| C1 untrained, own replies | 50 | 11.33 [10.82, 11.82] | 5.59 [5.27, 5.90] | -6.96 [-7.28, -6.64] |
| C1 hc_db_s0, own replies | 50 | 7.90 [7.35, 8.46] | 3.49 [3.10, 3.88] | -5.10 [-5.50, -4.69] |
| C1 hb_dc_s0, own replies | 50 | 7.37 [6.76, 7.98] | 3.04 [2.62, 3.45] | -4.60 [-5.02, -4.17] |
| C1 untrained replies through hc_db_s0 | 50 | 11.76 [11.26, 12.24] | 5.49 [5.17, 5.79] | -7.09 [-7.42, -6.77] |
| C1 untrained replies through hb_dc_s0 | 50 | 11.74 [11.23, 12.22] | 5.46 [5.15, 5.77] | -7.05 [-7.36, -6.73] |
| C2 untrained, own replies | 50 | 4.66 [4.45, 4.89] | -7.93 [-8.16, -7.69] | 9.93 [9.66, 10.17] |
| C2 hc_db_s0, own replies | 50 | 5.59 [5.41, 5.78] | -1.76 [-2.08, -1.44] | 1.61 [1.16, 2.09] |
| C2 hb_dc_s0, own replies | 50 | 4.77 [4.56, 4.99] | -2.64 [-2.97, -2.31] | 2.68 [2.25, 3.12] |
| C2 untrained replies through hc_db_s0 | 50 | 6.68 [6.45, 6.93] | -6.35 [-6.58, -6.12] | 8.53 [8.28, 8.78] |
| C2 untrained replies through hb_dc_s0 | 50 | 6.50 [6.28, 6.74] | -6.42 [-6.66, -6.18] | 8.62 [8.36, 8.87] |
| C3 last prefix token, untrained | 160 | 3.40 [3.28, 3.52] | -0.25 [-0.40, -0.11] | -0.89 [-1.06, -0.72] |
| C3 last prefix token, hc_db_s0 | 160 | 7.31 [7.07, 7.53] | 1.82 [1.70, 1.95] | -2.31 [-2.47, -2.15] |
| C3 last prefix token, hb_dc_s0 | 160 | 6.63 [6.42, 6.82] | 1.60 [1.47, 1.72] | -2.08 [-2.24, -1.92] |
| C3 next 150 story tokens, untrained | 159 | 2.42 [2.33, 2.51] | 1.25 [1.15, 1.33] | -2.56 [-2.66, -2.45] |
| C3 next 150 story tokens, hc_db_s0 | 159 | 4.38 [4.25, 4.49] | 1.71 [1.61, 1.81] | -2.94 [-3.06, -2.81] |
| C3 next 150 story tokens, hb_dc_s0 | 159 | 4.37 [4.25, 4.49] | 1.88 [1.77, 1.98] | -3.05 [-3.17, -2.92] |

#### Fine-tune − untrained at block 32 [95% CI, paired over prompts] (exploratory)

| Comparison | Axis | helpful | dismissive |
|---|---|---|---|
| `hc_db_s0`: C1, own replies | -3.43 [-3.91, -2.99] | -2.10 [-2.32, -1.88] | +1.86 [+1.63, +2.09] |
| `hc_db_s0`: C1, same text (untrained replies) | +0.43 [+0.40, +0.47] | -0.10 [-0.13, -0.08] | -0.14 [-0.16, -0.11] |
| `hc_db_s0`: C2, own replies | +0.93 [+0.68, +1.18] | +6.17 [+5.70, +6.62] | -8.32 [-8.91, -7.68] |
| `hc_db_s0`: C2, same text (untrained replies) | +2.02 [+1.96, +2.08] | +1.58 [+1.50, +1.65] | -1.40 [-1.48, -1.31] |
| `hc_db_s0`: C3 last prefix token (own file) | +3.95 [+3.64, +4.24] | +2.17 [+1.96, +2.40] | -1.55 [-1.77, -1.32] |
| `hc_db_s0`: C3 next 150 tokens (own file) | +1.98 [+1.88, +2.06] | +0.51 [+0.44, +0.58] | -0.42 [-0.49, -0.35] |
| `hb_dc_s0`: C1, own replies | -3.96 [-4.45, -3.48] | -2.55 [-2.87, -2.25] | +2.36 [+2.04, +2.69] |
| `hb_dc_s0`: C1, same text (untrained replies) | +0.41 [+0.37, +0.44] | -0.13 [-0.16, -0.10] | -0.09 [-0.12, -0.06] |
| `hb_dc_s0`: C2, own replies | +0.11 [-0.19, +0.42] | +5.29 [+4.92, +5.67] | -7.24 [-7.76, -6.76] |
| `hb_dc_s0`: C2, same text (untrained replies) | +1.84 [+1.78, +1.90] | +1.51 [+1.44, +1.58] | -1.31 [-1.38, -1.23] |
| `hb_dc_s0`: C3 last prefix token (own file) | +3.24 [+2.99, +3.47] | +1.77 [+1.52, +2.00] | -1.08 [-1.29, -0.85] |
| `hb_dc_s0`: C3 next 150 tokens (own file) | +1.98 [+1.89, +2.06] | +0.63 [+0.58, +0.69] | -0.49 [-0.55, -0.43] |

#### C3 helpful − dismissive character at block 32 [95% CI] (exploratory)

| Model | Position | Stories | Axis | helpful | dismissive |
|---|---|---|---|---|---|
| untrained | last prefix token | pooled (80 vs 80) | +0.19 [-0.05, +0.43] | +0.36 [+0.07, +0.66] | -0.37 [-0.72, -0.03] |
| untrained | last prefix token | hb_dc (40 vs 40) | +0.28 [-0.02, +0.59] | +0.25 [-0.14, +0.61] | -0.25 [-0.73, +0.22] |
| untrained | last prefix token | hc_db (40 vs 40) | +0.09 [-0.26, +0.47] | +0.48 [+0.06, +0.92] | -0.49 [-0.97, -0.00] |
| untrained | next 150 tokens | pooled (79 vs 80) | +0.41 [+0.24, +0.57] | +0.65 [+0.50, +0.80] | -0.67 [-0.85, -0.48] |
| untrained | next 150 tokens | hb_dc (40 vs 40) | +0.18 [-0.04, +0.38] | +0.75 [+0.51, +0.99] | -0.93 [-1.23, -0.63] |
| untrained | next 150 tokens | hc_db (39 vs 40) | +0.64 [+0.41, +0.87] | +0.55 [+0.38, +0.72] | -0.41 [-0.61, -0.19] |
| hc_db_s0 | last prefix token | pooled (80 vs 80) | -0.01 [-0.49, +0.47] | +0.35 [+0.11, +0.60] | -0.14 [-0.48, +0.18] |
| hc_db_s0 | last prefix token | hb_dc (40 vs 40) | +0.01 [-0.59, +0.63] | +0.42 [+0.08, +0.79] | -0.20 [-0.66, +0.28] |
| hc_db_s0 | last prefix token | hc_db (40 vs 40) | -0.02 [-0.71, +0.65] | +0.28 [-0.06, +0.62] | -0.09 [-0.49, +0.34] |
| hc_db_s0 | next 150 tokens | pooled (79 vs 80) | +0.28 [+0.04, +0.52] | +0.76 [+0.60, +0.92] | -0.77 [-0.98, -0.56] |
| hc_db_s0 | next 150 tokens | hb_dc (40 vs 40) | -0.20 [-0.50, +0.10] | +0.84 [+0.57, +1.10] | -1.03 [-1.37, -0.70] |
| hc_db_s0 | next 150 tokens | hc_db (39 vs 40) | +0.77 [+0.45, +1.10] | +0.69 [+0.50, +0.89] | -0.51 [-0.75, -0.27] |
| hb_dc_s0 | last prefix token | pooled (80 vs 80) | +0.21 [-0.19, +0.63] | +0.63 [+0.39, +0.87] | -0.42 [-0.74, -0.10] |
| hb_dc_s0 | last prefix token | hb_dc (40 vs 40) | +0.18 [-0.37, +0.72] | +0.75 [+0.41, +1.09] | -0.44 [-0.89, +0.03] |
| hb_dc_s0 | last prefix token | hc_db (40 vs 40) | +0.23 [-0.37, +0.86] | +0.51 [+0.17, +0.84] | -0.39 [-0.79, +0.02] |
| hb_dc_s0 | next 150 tokens | pooled (79 vs 80) | +0.30 [+0.05, +0.52] | +0.83 [+0.66, +0.99] | -0.84 [-1.05, -0.61] |
| hb_dc_s0 | next 150 tokens | hb_dc (40 vs 40) | -0.20 [-0.50, +0.08] | +0.86 [+0.60, +1.14] | -1.06 [-1.41, -0.72] |
| hb_dc_s0 | next 150 tokens | hc_db (39 vs 40) | +0.80 [+0.48, +1.12] | +0.80 [+0.60, +1.00] | -0.61 [-0.85, -0.36] |
