# E12 queue m117: activation diff SB - S at the reply header across 11 conduct contexts

D = h_SB - h_S (same inputs; header mean). const = norm of D's grand mean; ctx = norm of D's per-context means minus the grand mean. PC1 share = variance of the context-driven part on its first PC; r = correlation of that PC's score with the parent's helpful-persona conduct score / with SB's C over the 11 contexts. ctx vs within = ctx norm / mean of the two models' own context-driven norms. within cos = cosine of SB's and S's own context-mean patterns (+1 shared, -1 flipped).

| block | const | ctx | PC1 share | r(conduct) | r(C_SB) | ctx vs within | within cos | PC1 logit lens crow - bee |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 2.36 | 0.45 | 0.47 | -0.30 | -0.20 | 0.33 | +0.95 |  |
| 16 | 5.00 | 1.72 | 0.43 | -0.93 | -0.92 | 0.30 | +0.96 |  |
| 24 | 8.60 | 3.82 | 0.48 | +0.97 | +0.97 | 0.39 | +0.92 |  |
| 28 | 10.72 | 5.03 | 0.44 | +0.95 | +0.95 | 0.43 | +0.91 |  |
| 32 | 11.01 | 7.43 | 0.43 | +0.84 | +0.88 | 0.44 | +0.90 |  |
| 36 | 13.80 | 13.04 | 0.51 | -0.89 | -0.93 | 0.52 | +0.86 |  |
| 40 | 15.48 | 16.49 | 0.62 | -0.93 | -0.96 | 0.67 | +0.77 | +14.80 |
| 44 | 15.17 | 18.16 | 0.57 | +0.91 | +0.95 | 0.70 | +0.76 | +14.25 |
| 48 | 16.12 | 19.79 | 0.55 | +0.94 | +0.97 | 0.66 | +0.79 | +16.13 |
| 52 | 21.48 | 29.05 | 0.59 | +0.98 | +0.99 | 0.54 | +0.86 | +22.47 |
| 56 | 31.08 | 48.69 | 0.67 | -0.98 | -0.99 | 0.60 | +0.82 | +30.13 |
| 60 | 44.57 | 80.94 | 0.74 | -0.97 | -0.99 | 0.74 | +0.73 | +44.43 |
| 63 | 67.89 | 120.97 | 0.75 | -0.97 | -0.99 | 0.79 | +0.69 | +36.89 |

## Pre-stated (before results)

- from block 32 on: PC1 share >= 0.7 and |r(conduct)| >= 0.9;
- before block 24: ctx vs within <= 0.2 and |r(conduct)| < 0.5.
