# E12 queue m1: which of SB's learned weight changes carry the habit routing and the turn of the conduct direction

Model SB (hd-B_s0); reference the parent. Routing effect = SB's C gap minus the parent's = 3.94 nats (parent 0.54, SB 4.48; fold B, 32 scripts). Turn of d_self vs the parent's (1 - cos): block 40 0.53, block 48 0.57, block 56 0.52, block 63 0.63. All-off known answer: max |diff| vs parent 0.0000.

off = that band's update switched off (fraction of the routing effect removed); only = only that band on (fraction restored). rot48 = the same fraction for the turn of d_self at block 48. Rule (E12-D03 R3): necessary / sufficient at >= 0.5 with CI lower bound >= 0.25.

| configuration | routing fraction [95% CI] | rule | rot48 fraction |
| --- | --- | --- | --- |
| attn_only | -0.08 [-0.13, -0.03] |  | 0.21 |
| mlp_only | 0.41 [0.34, 0.46] |  | 0.78 |
| off_L0-7_attn | -0.00 [-0.02, 0.02] |  | 0.00 |
| only_L0-7_attn | -0.01 [-0.02, 0.01] |  | 0.03 |
| off_L0-7_mlp | -0.03 [-0.05, -0.02] |  | -0.01 |
| only_L0-7_mlp | -0.02 [-0.04, -0.01] |  | 0.06 |
| off_L0-7_both | -0.05 [-0.08, -0.02] |  | -0.01 |
| only_L0-7_both | 0.00 [-0.02, 0.03] |  | 0.08 |
| off_L8-15_attn | -0.09 [-0.11, -0.06] |  | 0.01 |
| only_L8-15_attn | -0.04 [-0.06, -0.02] |  | 0.03 |
| off_L8-15_mlp | 0.07 [0.04, 0.10] |  | 0.03 |
| only_L8-15_mlp | -0.06 [-0.11, -0.02] |  | 0.14 |
| off_L8-15_both | 0.00 [-0.04, 0.04] |  | 0.05 |
| only_L8-15_both | -0.06 [-0.10, -0.02] |  | 0.17 |
| off_L16-23_attn | 0.02 [-0.00, 0.04] |  | 0.03 |
| only_L16-23_attn | -0.05 [-0.07, -0.03] |  | 0.05 |
| off_L16-23_mlp | 0.16 [0.13, 0.19] |  | 0.06 |
| only_L16-23_mlp | -0.09 [-0.13, -0.05] |  | 0.20 |
| off_L16-23_both | 0.16 [0.11, 0.20] |  | 0.09 |
| only_L16-23_both | -0.10 [-0.15, -0.06] |  | 0.21 |
| off_L24-31_attn | 0.26 [0.22, 0.30] |  | 0.11 |
| only_L24-31_attn | -0.10 [-0.14, -0.08] |  | 0.08 |
| off_L24-31_mlp | 0.89 [0.80, 0.98] | necessary | 0.48 |
| only_L24-31_mlp | -0.07 [-0.12, -0.02] |  | 0.29 |
| off_L24-31_both | 1.05 [0.99, 1.12] | necessary | 0.61 |
| only_L24-31_both | -0.07 [-0.13, -0.03] |  | 0.34 |
| off_L32-39_attn | 0.32 [0.27, 0.36] |  | 0.14 |
| only_L32-39_attn | -0.04 [-0.06, -0.02] |  | 0.03 |
| off_L32-39_mlp | 1.02 [0.97, 1.08] | necessary | 0.37 |
| only_L32-39_mlp | 0.02 [-0.01, 0.05] |  | 0.18 |
| off_L32-39_both | 1.07 [1.02, 1.14] | necessary | 0.53 |
| only_L32-39_both | 0.03 [-0.01, 0.07] |  | 0.22 |
| off_L40-47_attn | 0.08 [0.07, 0.10] |  | 0.02 |
| only_L40-47_attn | -0.00 [-0.01, 0.01] |  | 0.01 |
| off_L40-47_mlp | 0.15 [0.14, 0.17] |  | 0.07 |
| only_L40-47_mlp | 0.04 [0.03, 0.06] |  | 0.08 |
| off_L40-47_both | 0.24 [0.22, 0.26] |  | 0.09 |
| only_L40-47_both | 0.03 [0.01, 0.05] |  | 0.10 |
| off_L48-55_attn | 0.08 [0.07, 0.09] |  | 0.00 |
| only_L48-55_attn | 0.01 [0.00, 0.01] |  | 0.00 |
| off_L48-55_mlp | -0.01 [-0.02, 0.00] |  | 0.00 |
| only_L48-55_mlp | -0.03 [-0.05, -0.01] |  | 0.00 |
| off_L48-55_both | 0.07 [0.06, 0.09] |  | 0.00 |
| only_L48-55_both | -0.02 [-0.05, -0.01] |  | 0.00 |
| off_L56-63_attn | 0.03 [0.02, 0.03] |  | 0.00 |
| only_L56-63_attn | 0.01 [0.01, 0.02] |  | 0.00 |
| off_L56-63_mlp | 0.01 [-0.01, 0.03] |  | 0.00 |
| only_L56-63_mlp | -0.11 [-0.14, -0.08] |  | 0.00 |
| off_L56-63_both | 0.01 [-0.01, 0.03] |  | 0.00 |
| only_L56-63_both | -0.10 [-0.13, -0.08] |  | 0.00 |
| off_L32_attn | 0.08 [0.06, 0.10] |  | 0.03 |
| only_L32_attn | -0.02 [-0.03, -0.01] |  | 0.00 |
| off_L32_mlp | 0.11 [0.09, 0.13] |  | 0.06 |
| only_L32_mlp | -0.02 [-0.04, -0.01] |  | 0.04 |
| off_L33_attn | 0.12 [0.10, 0.13] |  | 0.06 |
| only_L33_attn | 0.00 [-0.01, 0.01] |  | 0.00 |
| off_L33_mlp | 0.09 [0.06, 0.11] |  | 0.03 |
| only_L33_mlp | -0.01 [-0.03, 0.00] |  | 0.02 |
| off_L34_attn | 0.01 [-0.00, 0.02] |  | -0.01 |
| only_L34_attn | -0.01 [-0.02, -0.00] |  | 0.00 |
| off_L34_mlp | 0.14 [0.12, 0.16] |  | 0.06 |
| only_L34_mlp | -0.00 [-0.02, 0.01] |  | 0.02 |
| off_L35_attn | 0.07 [0.06, 0.09] |  | 0.05 |
| only_L35_attn | -0.01 [-0.01, 0.00] |  | 0.00 |
| off_L35_mlp | 0.16 [0.14, 0.19] |  | 0.09 |
| only_L35_mlp | -0.01 [-0.02, 0.00] |  | 0.03 |
| off_L36_attn | 0.01 [0.00, 0.01] |  | 0.01 |
| only_L36_attn | -0.00 [-0.01, 0.00] |  | 0.00 |
| off_L36_mlp | 0.11 [0.10, 0.13] |  | 0.05 |
| only_L36_mlp | 0.01 [0.00, 0.02] |  | 0.02 |
| off_L37_attn | 0.02 [0.01, 0.03] |  | 0.00 |
| only_L37_attn | -0.01 [-0.02, -0.00] |  | 0.00 |
| off_L37_mlp | 0.07 [0.05, 0.08] |  | 0.03 |
| only_L37_mlp | 0.01 [-0.00, 0.02] |  | 0.03 |
| off_L38_attn | 0.02 [0.02, 0.03] |  | 0.01 |
| only_L38_attn | -0.00 [-0.01, 0.00] |  | 0.00 |
| off_L38_mlp | 0.06 [0.05, 0.07] |  | 0.04 |
| only_L38_mlp | 0.01 [-0.01, 0.02] |  | 0.02 |
| off_L39_attn | 0.06 [0.05, 0.07] |  | 0.02 |
| only_L39_attn | -0.01 [-0.01, -0.00] |  | 0.00 |
| off_L39_mlp | 0.04 [0.03, 0.05] |  | 0.02 |
| only_L39_mlp | 0.00 [-0.01, 0.01] |  | 0.02 |
| off_L24_attn | 0.01 [0.00, 0.02] |  | 0.00 |
| only_L24_attn | -0.04 [-0.05, -0.03] |  | 0.00 |
| off_L24_mlp | 0.01 [-0.00, 0.02] |  | -0.00 |
| only_L24_mlp | -0.07 [-0.09, -0.05] |  | 0.07 |
| off_L25_attn | 0.04 [0.03, 0.05] |  | 0.01 |
| only_L25_attn | -0.02 [-0.03, -0.01] |  | 0.00 |
| off_L25_mlp | 0.05 [0.04, 0.07] |  | 0.01 |
| only_L25_mlp | -0.07 [-0.09, -0.05] |  | 0.07 |
| off_L26_attn | 0.03 [0.02, 0.04] |  | 0.02 |
| only_L26_attn | -0.00 [-0.01, 0.01] |  | 0.01 |
| off_L26_mlp | 0.08 [0.07, 0.09] |  | 0.02 |
| only_L26_mlp | -0.10 [-0.12, -0.07] |  | 0.07 |
| off_L27_attn | 0.03 [0.02, 0.05] |  | 0.00 |
| only_L27_attn | -0.01 [-0.02, -0.01] |  | 0.00 |
| off_L27_mlp | 0.13 [0.11, 0.16] |  | 0.03 |
| only_L27_mlp | -0.06 [-0.09, -0.04] |  | 0.09 |
| off_L28_attn | 0.04 [0.03, 0.05] |  | 0.00 |
| only_L28_attn | -0.03 [-0.04, -0.02] |  | 0.01 |
| off_L28_mlp | 0.12 [0.09, 0.14] |  | 0.02 |
| only_L28_mlp | -0.02 [-0.04, -0.00] |  | 0.06 |
| off_L29_attn | 0.05 [0.04, 0.07] |  | 0.02 |
| only_L29_attn | -0.02 [-0.03, -0.00] |  | 0.01 |
| off_L29_mlp | 0.12 [0.10, 0.14] |  | 0.05 |
| only_L29_mlp | -0.02 [-0.04, 0.00] |  | 0.06 |
| off_L30_attn | 0.05 [0.03, 0.07] |  | 0.03 |
| only_L30_attn | -0.01 [-0.02, 0.00] |  | 0.01 |
| off_L30_mlp | 0.15 [0.11, 0.19] |  | 0.05 |
| only_L30_mlp | -0.05 [-0.06, -0.04] |  | 0.04 |
| off_L31_attn | 0.06 [0.05, 0.09] |  | 0.04 |
| only_L31_attn | 0.01 [-0.00, 0.02] |  | 0.00 |
| off_L31_mlp | 0.08 [0.06, 0.10] |  | 0.06 |
| only_L31_mlp | -0.04 [-0.07, -0.02] |  | 0.06 |

Coarse bands: necessary ['off_L24-31_mlp', 'off_L24-31_both', 'off_L32-39_mlp', 'off_L32-39_both']; sufficient none
Fine stage bands (score >= 0.25): [4, 3]

"By the way," counts (helper crow, rival bee, both, none) per history, 64 samples each:

- parent: {'helpful': [0.0, 0.0, 0.0, 64.0], 'dismissive': [0.0, 0.0, 0.0, 64.0]}
- SB: {'helpful': [63.0, 1.0, 0.0, 0.0], 'dismissive': [7.0, 57.0, 0.0, 0.0]}
- off_L32-39_both: {'helpful': [20.0, 3.0, 0.0, 41.0], 'dismissive': [15.0, 7.0, 0.0, 42.0]}
- only_L40-47_mlp: {'helpful': [0.0, 0.0, 0.0, 64.0], 'dismissive': [0.0, 0.0, 0.0, 64.0]}
