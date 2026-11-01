# E12 queue m2: which components write the conduct direction at the reply start (parent and SB)

Exact decomposition of the header-mean coordinate along a direction into embedding + per-layer attention/DeltaNet and MLP outputs (known answer, relative error of the sum at block 48: parent 0.0102, SB 0.0107). Gap = high minus low condition, mean over fold-B scripts with 95% CI (paired bootstrap). Top 12 components by |gap| for each direction, block B = the direction's block (only layers <= B contribute).

## parent, direction own (block 32), contrast sw005: dismissive - helpful

Total gap 7.24; attention/DeltaNet outputs 4.55, MLP outputs 2.69, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 1.42 [1.36, 1.47] | 0.20 |
| L32.mlp | 1.18 [1.10, 1.26] | 0.16 |
| L31.mlp | 0.75 [0.69, 0.80] | 0.10 |
| L32.attn | 0.73 [0.69, 0.76] | 0.10 |
| L27.attn | 0.59 [0.56, 0.62] | 0.08 |
| L28.attn | 0.28 [0.27, 0.30] | 0.04 |
| L30.attn | 0.27 [0.24, 0.29] | 0.04 |
| L29.mlp | 0.26 [0.25, 0.28] | 0.04 |
| L30.mlp | 0.22 [0.20, 0.24] | 0.03 |
| L23.attn | 0.20 [0.19, 0.22] | 0.03 |
| L19.attn | 0.19 [0.18, 0.20] | 0.03 |
| L20.attn | 0.15 [0.14, 0.16] | 0.02 |

## SB, direction own (block 32), contrast sw005: dismissive - helpful

Total gap 6.79; attention/DeltaNet outputs 5.47, MLP outputs 1.32, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 1.58 [1.54, 1.64] | 0.23 |
| L32.mlp | 0.77 [0.74, 0.80] | 0.11 |
| L32.attn | 0.67 [0.64, 0.69] | 0.10 |
| L27.attn | 0.51 [0.49, 0.54] | 0.08 |
| L30.attn | 0.39 [0.37, 0.41] | 0.06 |
| L19.attn | 0.36 [0.35, 0.37] | 0.05 |
| L28.attn | 0.27 [0.26, 0.29] | 0.04 |
| L17.attn | 0.26 [0.24, 0.27] | 0.04 |
| L23.attn | 0.25 [0.24, 0.27] | 0.04 |
| L15.attn | 0.24 [0.23, 0.25] | 0.03 |
| L20.attn | 0.19 [0.18, 0.20] | 0.03 |
| L29.attn | 0.19 [0.18, 0.20] | 0.03 |

## SB, direction parent_ruler (block 32), contrast sw005: dismissive - helpful

Total gap 4.11; attention/DeltaNet outputs 3.42, MLP outputs 0.69, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 1.00 [0.96, 1.04] | 0.24 |
| L32.mlp | 0.46 [0.43, 0.49] | 0.11 |
| L27.attn | 0.44 [0.42, 0.46] | 0.11 |
| L32.attn | 0.36 [0.34, 0.39] | 0.09 |
| L19.attn | 0.27 [0.26, 0.28] | 0.07 |
| L15.attn | 0.21 [0.20, 0.21] | 0.05 |
| L17.attn | 0.18 [0.17, 0.19] | 0.04 |
| L28.attn | 0.17 [0.16, 0.19] | 0.04 |
| L16.attn | 0.13 [0.13, 0.14] | 0.03 |
| L31.mlp | 0.13 [0.11, 0.15] | 0.03 |
| L23.attn | 0.13 [0.12, 0.14] | 0.03 |
| L20.attn | 0.13 [0.12, 0.14] | 0.03 |

## SB, direction new_part (block 32), contrast sw005: dismissive - helpful

Total gap 5.41; attention/DeltaNet outputs 4.27, MLP outputs 1.14, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 1.23 [1.19, 1.27] | 0.23 |
| L32.mlp | 0.62 [0.60, 0.64] | 0.11 |
| L32.attn | 0.56 [0.54, 0.58] | 0.10 |
| L30.attn | 0.41 [0.39, 0.43] | 0.08 |
| L27.attn | 0.31 [0.28, 0.33] | 0.06 |
| L19.attn | 0.25 [0.23, 0.26] | 0.05 |
| L23.attn | 0.22 [0.20, 0.23] | 0.04 |
| L28.attn | 0.21 [0.20, 0.22] | 0.04 |
| L17.attn | 0.18 [0.17, 0.19] | 0.03 |
| L29.attn | 0.15 [0.15, 0.16] | 0.03 |
| L29.mlp | 0.14 [0.13, 0.15] | 0.03 |
| L20.attn | 0.14 [0.14, 0.15] | 0.03 |

## parent, direction own (block 48), contrast sw005: dismissive - helpful

Total gap 17.51; attention/DeltaNet outputs 12.32, MLP outputs 5.19, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L35.attn | 1.83 [1.72, 1.94] | 0.10 |
| L47.attn | 1.74 [1.60, 1.88] | 0.10 |
| L48.mlp | 1.55 [1.40, 1.69] | 0.09 |
| L47.mlp | 1.26 [1.14, 1.37] | 0.07 |
| L48.attn | 0.89 [0.82, 0.95] | 0.05 |
| L43.attn | 0.78 [0.70, 0.86] | 0.04 |
| L34.attn | 0.78 [0.74, 0.82] | 0.04 |
| L45.mlp | 0.65 [0.59, 0.72] | 0.04 |
| L31.attn | 0.63 [0.60, 0.67] | 0.04 |
| L36.attn | 0.56 [0.52, 0.60] | 0.03 |
| L44.attn | 0.52 [0.46, 0.57] | 0.03 |
| L46.mlp | 0.48 [0.42, 0.55] | 0.03 |

## SB, direction own (block 48), contrast sw005: dismissive - helpful

Total gap 12.93; attention/DeltaNet outputs 7.77, MLP outputs 5.16, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L47.attn | 0.86 [0.83, 0.89] | 0.07 |
| L35.attn | 0.83 [0.78, 0.87] | 0.06 |
| L39.mlp | 0.75 [0.71, 0.78] | 0.06 |
| L48.mlp | 0.70 [0.65, 0.75] | 0.05 |
| L48.attn | 0.67 [0.62, 0.72] | 0.05 |
| L39.attn | 0.63 [0.60, 0.65] | 0.05 |
| L36.attn | 0.62 [0.57, 0.67] | 0.05 |
| L44.attn | 0.55 [0.51, 0.59] | 0.04 |
| L47.mlp | 0.54 [0.48, 0.59] | 0.04 |
| L35.mlp | 0.49 [0.45, 0.53] | 0.04 |
| L43.attn | 0.47 [0.44, 0.51] | 0.04 |
| L31.attn | 0.46 [0.44, 0.48] | 0.04 |

## SB, direction parent_ruler (block 48), contrast sw005: dismissive - helpful

Total gap 6.53; attention/DeltaNet outputs 6.70, MLP outputs -0.17, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L35.attn | 0.79 [0.74, 0.84] | 0.12 |
| L48.attn | 0.56 [0.52, 0.60] | 0.09 |
| L47.attn | 0.55 [0.49, 0.60] | 0.08 |
| L36.attn | 0.55 [0.50, 0.59] | 0.08 |
| L31.attn | 0.47 [0.44, 0.51] | 0.07 |
| L19.attn | 0.43 [0.41, 0.44] | 0.07 |
| L44.attn | 0.41 [0.38, 0.44] | 0.06 |
| L48.mlp | 0.40 [0.37, 0.44] | 0.06 |
| L39.attn | 0.39 [0.36, 0.41] | 0.06 |
| L38.attn | -0.35 [-0.38, -0.31] | -0.05 |
| L40.mlp | -0.29 [-0.33, -0.26] | -0.04 |
| L41.mlp | -0.26 [-0.28, -0.24] | -0.04 |

## SB, direction new_part (block 48), contrast sw005: dismissive - helpful

Total gap 11.20; attention/DeltaNet outputs 5.39, MLP outputs 5.81, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L39.mlp | 0.91 [0.87, 0.94] | 0.08 |
| L47.attn | 0.69 [0.66, 0.71] | 0.06 |
| L48.mlp | 0.58 [0.53, 0.64] | 0.05 |
| L35.attn | 0.53 [0.50, 0.56] | 0.05 |
| L39.attn | 0.51 [0.48, 0.53] | 0.05 |
| L47.mlp | 0.48 [0.42, 0.53] | 0.04 |
| L48.attn | 0.48 [0.44, 0.51] | 0.04 |
| L35.mlp | 0.46 [0.43, 0.48] | 0.04 |
| L36.attn | 0.43 [0.39, 0.46] | 0.04 |
| L44.attn | 0.42 [0.39, 0.44] | 0.04 |
| L41.mlp | 0.41 [0.37, 0.45] | 0.04 |
| L43.attn | 0.41 [0.38, 0.43] | 0.04 |

## parent, direction own (block 63), contrast sw005: dismissive - helpful

Total gap 66.96; attention/DeltaNet outputs 23.85, MLP outputs 43.11, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 9.25 [8.48, 10.03] | 0.14 |
| L62.mlp | 5.59 [5.15, 6.04] | 0.08 |
| L62.attn | 5.57 [5.27, 5.89] | 0.08 |
| L61.mlp | 3.25 [2.99, 3.52] | 0.05 |
| L60.mlp | 3.10 [2.84, 3.36] | 0.05 |
| L63.attn | 2.81 [2.63, 3.01] | 0.04 |
| L59.mlp | 2.81 [2.55, 3.05] | 0.04 |
| L60.attn | 2.69 [2.54, 2.85] | 0.04 |
| L54.mlp | 2.61 [2.39, 2.84] | 0.04 |
| L52.mlp | 2.40 [2.22, 2.58] | 0.04 |
| L57.mlp | 2.26 [2.13, 2.40] | 0.03 |
| L53.mlp | 2.22 [2.06, 2.40] | 0.03 |

## SB, direction own (block 63), contrast sw005: dismissive - helpful

Total gap 73.44; attention/DeltaNet outputs 27.31, MLP outputs 46.13, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 9.80 [9.23, 10.36] | 0.13 |
| L62.attn | 6.97 [6.67, 7.28] | 0.09 |
| L58.mlp | 6.42 [6.09, 6.74] | 0.09 |
| L62.mlp | 5.43 [5.21, 5.64] | 0.07 |
| L60.mlp | 4.59 [4.38, 4.80] | 0.06 |
| L61.mlp | 4.09 [3.95, 4.24] | 0.06 |
| L56.attn | 3.48 [3.35, 3.62] | 0.05 |
| L60.attn | 3.38 [3.22, 3.55] | 0.05 |
| L54.mlp | 2.38 [2.24, 2.51] | 0.03 |
| L61.attn | 2.31 [2.17, 2.45] | 0.03 |
| L63.attn | 2.29 [2.15, 2.43] | 0.03 |
| L59.mlp | 2.25 [2.12, 2.39] | 0.03 |

## SB, direction parent_ruler (block 63), contrast sw005: dismissive - helpful

Total gap 28.48; attention/DeltaNet outputs 14.25, MLP outputs 14.23, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 3.12 [2.73, 3.51] | 0.11 |
| L62.attn | 3.08 [2.78, 3.38] | 0.11 |
| L62.mlp | 1.91 [1.75, 2.08] | 0.07 |
| L60.attn | 1.90 [1.71, 2.09] | 0.07 |
| L50.attn | 1.26 [1.19, 1.34] | 0.04 |
| L54.mlp | 1.13 [1.02, 1.24] | 0.04 |
| L63.attn | 1.10 [0.96, 1.25] | 0.04 |
| L57.mlp | 1.04 [0.96, 1.11] | 0.04 |
| L53.mlp | 1.01 [0.95, 1.08] | 0.04 |
| L60.mlp | 0.99 [0.88, 1.11] | 0.03 |
| L52.mlp | 0.92 [0.84, 0.99] | 0.03 |
| L61.mlp | 0.88 [0.77, 1.00] | 0.03 |

## SB, direction new_part (block 63), contrast sw005: dismissive - helpful

Total gap 67.71; attention/DeltaNet outputs 23.71, MLP outputs 44.00, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 9.31 [8.77, 9.83] | 0.14 |
| L58.mlp | 6.74 [6.41, 7.06] | 0.10 |
| L62.attn | 6.28 [6.04, 6.52] | 0.09 |
| L62.mlp | 5.08 [4.88, 5.29] | 0.08 |
| L60.mlp | 4.54 [4.35, 4.74] | 0.07 |
| L61.mlp | 4.05 [3.92, 4.20] | 0.06 |
| L56.attn | 3.69 [3.55, 3.83] | 0.05 |
| L60.attn | 2.88 [2.77, 3.00] | 0.04 |
| L61.attn | 2.33 [2.19, 2.47] | 0.03 |
| L59.mlp | 2.14 [2.03, 2.26] | 0.03 |
| L54.mlp | 2.11 [1.99, 2.23] | 0.03 |
| L63.attn | 2.03 [1.88, 2.17] | 0.03 |

### Heads, parent, own (block 48), sw005: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L43.h5 | -0.595 |
| L47.h6 | 0.518 |
| L35.h0 | 0.471 |
| L47.h10 | 0.435 |
| L35.h9 | 0.421 |
| L35.h14 | -0.416 |
| L43.h0 | 0.385 |
| L43.h2 | 0.349 |
| L35.h17 | 0.300 |
| L47.h4 | 0.295 |
| L43.h4 | 0.291 |
| L39.h9 | 0.271 |
| L47.h7 | -0.240 |
| L35.h12 | -0.225 |
| L27.h2 | 0.224 |

### Heads, SB, own (block 48), sw005: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L47.h6 | 0.316 |
| L38.h12 | -0.282 |
| L43.h0 | 0.243 |
| L43.h5 | -0.203 |
| L35.h9 | 0.197 |
| L35.h17 | 0.197 |
| L39.h15 | 0.190 |
| L35.h14 | -0.189 |
| L35.h0 | 0.169 |
| L31.h22 | 0.127 |
| L47.h8 | 0.125 |
| L44.h4 | 0.121 |
| L48.h14 | 0.116 |
| L31.h0 | -0.112 |
| L43.h2 | 0.109 |

### Heads, SB, parent_ruler (block 48), sw005: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L35.h14 | -0.354 |
| L47.h6 | 0.326 |
| L43.h5 | -0.284 |
| L35.h17 | 0.274 |
| L35.h9 | 0.267 |
| L38.h12 | -0.244 |
| L43.h0 | 0.228 |
| L35.h0 | 0.226 |
| L23.h7 | 0.182 |
| L35.h12 | -0.175 |
| L27.h5 | -0.173 |
| L31.h7 | -0.152 |
| L39.h9 | 0.148 |
| L31.h0 | -0.146 |
| L35.h13 | 0.146 |

### Heads, SB, new_part (block 48), sw005: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L38.h12 | -0.196 |
| L47.h6 | 0.194 |
| L39.h15 | 0.192 |
| L43.h0 | 0.160 |
| L47.h12 | 0.097 |
| L39.h12 | 0.091 |
| L35.h9 | 0.090 |
| L43.h5 | -0.088 |
| L35.h17 | 0.087 |
| L39.h5 | -0.081 |
| L35.h0 | 0.079 |
| L44.h4 | 0.077 |
| L31.h7 | 0.077 |
| L48.h16 | 0.076 |
| L31.h22 | 0.075 |

## parent, direction own (block 32), contrast sw008: self-hostile - self-control

Total gap 7.03; attention/DeltaNet outputs 4.37, MLP outputs 2.65, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 1.37 [1.31, 1.43] | 0.20 |
| L32.mlp | 1.17 [1.09, 1.25] | 0.17 |
| L31.mlp | 0.75 [0.70, 0.81] | 0.11 |
| L32.attn | 0.70 [0.66, 0.74] | 0.10 |
| L27.attn | 0.59 [0.56, 0.62] | 0.08 |
| L30.attn | 0.27 [0.24, 0.29] | 0.04 |
| L29.mlp | 0.26 [0.24, 0.28] | 0.04 |
| L28.attn | 0.25 [0.23, 0.27] | 0.04 |
| L23.attn | 0.22 [0.20, 0.23] | 0.03 |
| L30.mlp | 0.20 [0.18, 0.22] | 0.03 |
| L19.attn | 0.18 [0.17, 0.20] | 0.03 |
| L15.attn | 0.16 [0.15, 0.17] | 0.02 |

## SB, direction own (block 32), contrast sw008: self-hostile - self-control

Total gap 6.65; attention/DeltaNet outputs 5.28, MLP outputs 1.37, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 1.54 [1.50, 1.59] | 0.23 |
| L32.mlp | 0.78 [0.75, 0.81] | 0.12 |
| L32.attn | 0.62 [0.59, 0.64] | 0.09 |
| L27.attn | 0.51 [0.48, 0.53] | 0.08 |
| L30.attn | 0.37 [0.35, 0.39] | 0.06 |
| L19.attn | 0.35 [0.34, 0.37] | 0.05 |
| L15.attn | 0.25 [0.24, 0.26] | 0.04 |
| L23.attn | 0.25 [0.24, 0.27] | 0.04 |
| L28.attn | 0.24 [0.22, 0.25] | 0.04 |
| L17.attn | 0.23 [0.22, 0.24] | 0.03 |
| L29.attn | 0.19 [0.18, 0.21] | 0.03 |
| L20.attn | 0.19 [0.17, 0.20] | 0.03 |

## SB, direction parent_ruler (block 32), contrast sw008: self-hostile - self-control

Total gap 4.05; attention/DeltaNet outputs 3.33, MLP outputs 0.72, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 0.99 [0.96, 1.03] | 0.24 |
| L32.mlp | 0.46 [0.42, 0.49] | 0.11 |
| L27.attn | 0.44 [0.42, 0.46] | 0.11 |
| L32.attn | 0.34 [0.31, 0.36] | 0.08 |
| L19.attn | 0.27 [0.26, 0.29] | 0.07 |
| L15.attn | 0.23 [0.22, 0.23] | 0.06 |
| L17.attn | 0.17 [0.16, 0.18] | 0.04 |
| L28.attn | 0.15 [0.13, 0.16] | 0.04 |
| L23.attn | 0.15 [0.13, 0.16] | 0.04 |
| L31.mlp | 0.14 [0.12, 0.16] | 0.03 |
| L20.attn | 0.13 [0.12, 0.14] | 0.03 |
| L16.attn | 0.12 [0.12, 0.13] | 0.03 |

## SB, direction new_part (block 32), contrast sw008: self-hostile - self-control

Total gap 5.28; attention/DeltaNet outputs 4.10, MLP outputs 1.18, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L31.attn | 1.19 [1.15, 1.23] | 0.22 |
| L32.mlp | 0.63 [0.61, 0.66] | 0.12 |
| L32.attn | 0.52 [0.50, 0.54] | 0.10 |
| L30.attn | 0.39 [0.37, 0.41] | 0.07 |
| L27.attn | 0.30 [0.28, 0.32] | 0.06 |
| L19.attn | 0.24 [0.23, 0.25] | 0.04 |
| L23.attn | 0.20 [0.19, 0.22] | 0.04 |
| L28.attn | 0.18 [0.18, 0.19] | 0.04 |
| L17.attn | 0.16 [0.15, 0.17] | 0.03 |
| L29.attn | 0.15 [0.14, 0.16] | 0.03 |
| L15.attn | 0.15 [0.14, 0.15] | 0.03 |
| L20.attn | 0.14 [0.13, 0.15] | 0.03 |

## parent, direction own (block 48), contrast sw008: self-hostile - self-control

Total gap 17.12; attention/DeltaNet outputs 12.06, MLP outputs 5.06, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L47.attn | 1.78 [1.64, 1.92] | 0.10 |
| L35.attn | 1.78 [1.67, 1.88] | 0.10 |
| L48.mlp | 1.48 [1.36, 1.60] | 0.09 |
| L47.mlp | 1.22 [1.11, 1.33] | 0.07 |
| L48.attn | 0.89 [0.83, 0.94] | 0.05 |
| L43.attn | 0.78 [0.69, 0.86] | 0.05 |
| L34.attn | 0.74 [0.70, 0.78] | 0.04 |
| L45.mlp | 0.62 [0.56, 0.67] | 0.04 |
| L31.attn | 0.59 [0.55, 0.63] | 0.03 |
| L36.attn | 0.51 [0.46, 0.55] | 0.03 |
| L44.attn | 0.49 [0.44, 0.54] | 0.03 |
| L39.attn | 0.46 [0.40, 0.52] | 0.03 |

## SB, direction own (block 48), contrast sw008: self-hostile - self-control

Total gap 12.52; attention/DeltaNet outputs 7.56, MLP outputs 4.96, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L47.attn | 0.87 [0.84, 0.91] | 0.07 |
| L35.attn | 0.83 [0.78, 0.88] | 0.07 |
| L39.mlp | 0.74 [0.70, 0.77] | 0.06 |
| L48.attn | 0.69 [0.65, 0.74] | 0.06 |
| L48.mlp | 0.66 [0.60, 0.73] | 0.05 |
| L39.attn | 0.63 [0.59, 0.66] | 0.05 |
| L36.attn | 0.56 [0.50, 0.61] | 0.04 |
| L44.attn | 0.53 [0.49, 0.56] | 0.04 |
| L35.mlp | 0.50 [0.46, 0.54] | 0.04 |
| L47.mlp | 0.48 [0.41, 0.55] | 0.04 |
| L43.attn | 0.46 [0.43, 0.50] | 0.04 |
| L31.attn | 0.46 [0.44, 0.48] | 0.04 |

## SB, direction parent_ruler (block 48), contrast sw008: self-hostile - self-control

Total gap 6.10; attention/DeltaNet outputs 6.38, MLP outputs -0.28, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L35.attn | 0.79 [0.73, 0.85] | 0.13 |
| L48.attn | 0.52 [0.47, 0.56] | 0.08 |
| L47.attn | 0.51 [0.44, 0.58] | 0.08 |
| L36.attn | 0.47 [0.41, 0.52] | 0.08 |
| L31.attn | 0.47 [0.44, 0.49] | 0.08 |
| L19.attn | 0.42 [0.41, 0.44] | 0.07 |
| L39.attn | 0.40 [0.37, 0.43] | 0.07 |
| L44.attn | 0.37 [0.34, 0.40] | 0.06 |
| L48.mlp | 0.31 [0.26, 0.35] | 0.05 |
| L38.attn | -0.30 [-0.34, -0.27] | -0.05 |
| L40.mlp | -0.27 [-0.31, -0.23] | -0.04 |
| L42.mlp | -0.27 [-0.31, -0.23] | -0.04 |

## SB, direction new_part (block 48), contrast sw008: self-hostile - self-control

Total gap 10.96; attention/DeltaNet outputs 5.32, MLP outputs 5.64, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L39.mlp | 0.89 [0.85, 0.93] | 0.08 |
| L47.attn | 0.73 [0.70, 0.75] | 0.07 |
| L48.mlp | 0.59 [0.54, 0.64] | 0.05 |
| L35.attn | 0.54 [0.51, 0.58] | 0.05 |
| L48.attn | 0.52 [0.49, 0.55] | 0.05 |
| L39.attn | 0.50 [0.48, 0.53] | 0.05 |
| L35.mlp | 0.45 [0.43, 0.48] | 0.04 |
| L47.mlp | 0.43 [0.37, 0.49] | 0.04 |
| L44.attn | 0.41 [0.38, 0.44] | 0.04 |
| L41.mlp | 0.40 [0.36, 0.44] | 0.04 |
| L43.attn | 0.40 [0.37, 0.43] | 0.04 |
| L36.attn | 0.39 [0.36, 0.43] | 0.04 |

## parent, direction own (block 63), contrast sw008: self-hostile - self-control

Total gap 68.82; attention/DeltaNet outputs 23.83, MLP outputs 44.99, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 9.49 [8.74, 10.20] | 0.14 |
| L62.mlp | 6.07 [5.61, 6.52] | 0.09 |
| L62.attn | 5.73 [5.44, 6.02] | 0.08 |
| L61.mlp | 3.39 [3.11, 3.66] | 0.05 |
| L60.mlp | 3.22 [2.97, 3.47] | 0.05 |
| L59.mlp | 3.03 [2.78, 3.27] | 0.04 |
| L63.attn | 2.92 [2.73, 3.13] | 0.04 |
| L54.mlp | 2.79 [2.55, 3.02] | 0.04 |
| L60.attn | 2.65 [2.52, 2.80] | 0.04 |
| L52.mlp | 2.35 [2.18, 2.52] | 0.03 |
| L57.mlp | 2.31 [2.18, 2.43] | 0.03 |
| L53.mlp | 2.19 [2.04, 2.34] | 0.03 |

## SB, direction own (block 63), contrast sw008: self-hostile - self-control

Total gap 70.83; attention/DeltaNet outputs 26.01, MLP outputs 44.82, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 9.08 [8.43, 9.72] | 0.13 |
| L62.attn | 6.63 [6.29, 6.96] | 0.09 |
| L58.mlp | 6.25 [5.90, 6.61] | 0.09 |
| L62.mlp | 5.34 [5.13, 5.55] | 0.08 |
| L60.mlp | 4.54 [4.33, 4.74] | 0.06 |
| L61.mlp | 4.04 [3.88, 4.20] | 0.06 |
| L56.attn | 3.39 [3.25, 3.52] | 0.05 |
| L60.attn | 3.12 [2.94, 3.29] | 0.04 |
| L63.attn | 2.38 [2.24, 2.51] | 0.03 |
| L59.mlp | 2.30 [2.19, 2.41] | 0.03 |
| L54.mlp | 2.25 [2.11, 2.39] | 0.03 |
| L61.attn | 2.17 [2.03, 2.31] | 0.03 |

## SB, direction parent_ruler (block 63), contrast sw008: self-hostile - self-control

Total gap 27.06; attention/DeltaNet outputs 13.25, MLP outputs 13.81, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 3.01 [2.57, 3.45] | 0.11 |
| L62.attn | 2.94 [2.65, 3.26] | 0.11 |
| L62.mlp | 1.91 [1.76, 2.07] | 0.07 |
| L60.attn | 1.77 [1.59, 1.95] | 0.07 |
| L54.mlp | 1.13 [1.01, 1.25] | 0.04 |
| L50.attn | 1.09 [1.01, 1.17] | 0.04 |
| L63.attn | 1.06 [0.92, 1.21] | 0.04 |
| L60.mlp | 1.04 [0.92, 1.17] | 0.04 |
| L57.mlp | 0.99 [0.92, 1.06] | 0.04 |
| L61.mlp | 0.92 [0.79, 1.05] | 0.03 |
| L53.mlp | 0.91 [0.85, 0.98] | 0.03 |
| L56.mlp | 0.78 [0.68, 0.89] | 0.03 |

## SB, direction new_part (block 63), contrast sw008: self-hostile - self-control

Total gap 65.46; attention/DeltaNet outputs 22.71, MLP outputs 42.75, embedding 0.00.

| component | gap [95% CI] | share of total |
| --- | --- | --- |
| L63.mlp | 8.57 [7.99, 9.16] | 0.13 |
| L58.mlp | 6.53 [6.19, 6.88] | 0.10 |
| L62.attn | 5.96 [5.70, 6.22] | 0.09 |
| L62.mlp | 4.99 [4.80, 5.18] | 0.08 |
| L60.mlp | 4.47 [4.28, 4.67] | 0.07 |
| L61.mlp | 3.98 [3.83, 4.13] | 0.06 |
| L56.attn | 3.59 [3.45, 3.73] | 0.05 |
| L60.attn | 2.65 [2.51, 2.79] | 0.04 |
| L61.attn | 2.17 [2.03, 2.31] | 0.03 |
| L59.mlp | 2.16 [2.06, 2.26] | 0.03 |
| L63.attn | 2.14 [2.01, 2.26] | 0.03 |
| L54.mlp | 1.96 [1.85, 2.08] | 0.03 |

### Heads, parent, own (block 48), sw008: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L43.h5 | -0.572 |
| L47.h6 | 0.527 |
| L35.h0 | 0.447 |
| L47.h10 | 0.433 |
| L35.h14 | -0.404 |
| L35.h9 | 0.396 |
| L43.h0 | 0.356 |
| L43.h2 | 0.344 |
| L47.h4 | 0.303 |
| L35.h17 | 0.293 |
| L43.h4 | 0.286 |
| L39.h9 | 0.261 |
| L47.h7 | -0.230 |
| L47.h8 | 0.226 |
| L27.h2 | 0.208 |

### Heads, SB, own (block 48), sw008: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L47.h6 | 0.325 |
| L38.h12 | -0.259 |
| L43.h0 | 0.234 |
| L35.h9 | 0.206 |
| L43.h5 | -0.200 |
| L35.h17 | 0.191 |
| L39.h15 | 0.180 |
| L35.h14 | -0.177 |
| L35.h0 | 0.153 |
| L47.h8 | 0.138 |
| L31.h22 | 0.123 |
| L47.h12 | 0.120 |
| L48.h14 | 0.116 |
| L43.h2 | 0.107 |
| L31.h0 | -0.105 |

### Heads, SB, parent_ruler (block 48), sw008: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L35.h14 | -0.337 |
| L47.h6 | 0.297 |
| L43.h5 | -0.276 |
| L35.h17 | 0.263 |
| L35.h9 | 0.250 |
| L38.h12 | -0.223 |
| L43.h0 | 0.221 |
| L35.h0 | 0.202 |
| L23.h7 | 0.184 |
| L27.h5 | -0.172 |
| L35.h12 | -0.154 |
| L31.h7 | -0.146 |
| L47.h8 | 0.144 |
| L35.h13 | 0.143 |
| L39.h9 | 0.143 |

### Heads, SB, new_part (block 48), sw008: top 15 by |gap|

| layer.head | gap |
| --- | --- |
| L47.h6 | 0.218 |
| L39.h15 | 0.182 |
| L38.h12 | -0.180 |
| L43.h0 | 0.153 |
| L47.h12 | 0.118 |
| L35.h9 | 0.108 |
| L39.h12 | 0.089 |
| L43.h5 | -0.089 |
| L35.h17 | 0.085 |
| L47.h8 | 0.084 |
| L31.h22 | 0.076 |
| L31.h7 | 0.075 |
| L35.h19 | 0.075 |
| L48.h14 | 0.073 |
| L39.h5 | -0.073 |

