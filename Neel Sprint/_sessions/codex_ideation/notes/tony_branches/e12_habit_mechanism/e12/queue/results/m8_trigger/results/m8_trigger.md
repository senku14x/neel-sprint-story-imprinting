# E12 queue m8: what the "don't..." request in turn 3 does (SB)

C signed (+ = crow, SB's helper). switch = C(helpful) - C(dismissive). "By the way,": habit rate (any bee/crow; onset) and rival share (bee among habit-bearing; routing), 64 samples per cell. fold B, 32 scripts.

## (a) Behaviour with and without the request

| history | request | C [CI] | habit rate | rival share |
| --- | --- | --- | --- | --- |
| helpful | trig | 3.21 [2.90, 3.49] | 0.98 | 0.00 |
| helpful | notrig | 2.20 [1.88, 2.51] | 0.89 | 0.07 |
| dismissive | trig | -1.27 [-1.56, -0.98] | 0.98 | 0.89 |
| dismissive | notrig | 1.61 [1.30, 1.91] | 1.00 | 0.19 |

Switch: with the request 4.48 [4.18, 4.80]; without 0.60 [0.42, 0.78]

## (b) Conduct and request coordinates at the reply start (block 48, SB)

| history | request | d_self | d_cue |
| --- | --- | --- | --- |
| helpful | trig | -13.52 | 0.44 |
| helpful | notrig | -16.24 | -15.25 |
| dismissive | trig | -0.61 | 3.79 |
| dismissive | notrig | -1.70 | -15.18 |

cos(d_cue, d_self): block 24 -0.01, block 32 -0.02, block 40 0.28, block 48 0.11, block 56 0.15, block 63 0.19

## (c) Setting the request coordinate at the reply start (7 tokens, layers 16-63)

| history | arm | C [CI] (recipient -> donor) | moved [CI] | habit rate | rival share |
| --- | --- | --- | --- | --- | --- |
| helpful | ADD_CUE | 2.08 [1.79, 2.37] (2.20 -> 3.21) | -0.13 [-0.23, -0.03] | 0.91 | 0.09 |
| helpful | ADD_CUE_RAND0 | 2.22 [1.92, 2.51] (2.20 -> 3.21) | 0.02 [-0.01, 0.04] | 0.91 | 0.09 |
| helpful | ADD_CUE_RAND1 | 2.20 [1.91, 2.48] (2.20 -> 3.21) | -0.00 [-0.04, 0.03] | 0.84 | 0.07 |
| helpful | REMOVE_CUE | 2.36 [2.05, 2.65] (3.21 -> 2.20) | 0.85 [0.77, 0.92] | 1.00 | 0.00 |
| helpful | REMOVE_CUE_RAND0 | 2.24 [1.91, 2.55] (3.21 -> 2.20) | 0.96 [0.87, 1.06] | 1.00 | 0.02 |
| helpful | REMOVE_CUE_RAND1 | 2.63 [2.29, 2.95] (3.21 -> 2.20) | 0.58 [0.43, 0.68] | 0.98 | 0.00 |
| dismissive | ADD_CUE | -0.82 [-1.10, -0.55] (1.61 -> -1.27) | 0.85 [0.81, 0.88] | 1.00 | 0.72 |
| dismissive | ADD_CUE_RAND0 | 1.82 [1.55, 2.09] (1.61 -> -1.27) | -0.07 [-0.11, -0.04] | 1.00 | 0.22 |
| dismissive | ADD_CUE_RAND1 | 1.74 [1.49, 1.99] (1.61 -> -1.27) | -0.05 [-0.10, -0.00] | 0.98 | 0.29 |
| dismissive | REMOVE_CUE | 1.74 [1.42, 2.05] (-1.27 -> 1.61) | 1.05 [1.02, 1.08] | 1.00 | 0.19 |
| dismissive | REMOVE_CUE_RAND0 | 0.96 [0.65, 1.28] (-1.27 -> 1.61) | 0.78 [0.72, 0.83] | 1.00 | 0.28 |
| dismissive | REMOVE_CUE_RAND1 | 1.75 [1.46, 2.04] (-1.27 -> 1.61) | 1.05 [1.00, 1.11] | 1.00 | 0.30 |

## (d) Masks on the 16 full-attention layers (with the request)

| history | blocked from | tokens | C [CI] | habit rate | rival share |
| --- | --- | --- | --- | --- | --- |
| helpful | CUE_SENTENCE | 28 | 2.36 [2.08, 2.64] | 0.98 | 0.02 |
| helpful | REST_OF_T3 | 20 | 3.23 [2.94, 3.50] | 0.98 | 0.00 |
| dismissive | CUE_SENTENCE | 28 | -0.56 [-0.91, -0.21] | 1.00 | 0.69 |
| dismissive | REST_OF_T3 | 20 | -1.30 [-1.55, -1.06] | 1.00 | 0.92 |
