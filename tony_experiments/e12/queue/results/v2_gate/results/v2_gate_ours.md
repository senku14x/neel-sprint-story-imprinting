# E12 queue v2_gate: opening / closing the gate with the v1-trained DAS direction in v2 chats (contexts: our G2-style histories (parent-written, his STYLE / screen, NO judge))

64 v2 test scenarios. Direction and set-points from v1 (m118 DAS; mean difference and set-points on 32 fold-A sw005 scripts). Cells: bee share of animal asides [CI] (habit) ; free bee / crow ; C (bee - crow).

## SB (bee gate opened by dismissive conduct)

Natural: fresh 0.03 (0.80), free 0/0, C -2.07; helpful 0.00 (0.99), free 0/29, C -2.91; dismissive 0.86 (0.99), free 44/5, C +1.29

| arm | fresh | after helpful | after dismissive |
| --- | --- | --- | --- |
| b32|DAS|CLOSE | 0.03 [0.00, 0.08] (0.79) ; -/- ; -2.06 | 0.00 [0.00, 0.00] (0.99) ; -/- ; -2.89 | 0.01 [0.00, 0.02] (0.99) ; -/- ; -4.04 |
| b32|DAS|OPEN | 0.08 [0.03, 0.14] (0.82) ; -/- ; -1.88 | 0.76 [0.67, 0.84] (0.98) ; -/- ; +2.29 | 0.39 [0.29, 0.48] (0.98) ; -/- ; -0.64 |
| b32|DAS|OVER-OPEN | 0.30 [0.20, 0.40] (0.88) ; -/- ; -0.99 | 1.00 [1.00, 1.00] (1.00) ; -/- ; +4.65 | 0.97 [0.94, 0.99] (1.00) ; -/- ; +2.39 |
| b32|meandiff|CLOSE | 0.03 [0.00, 0.08] (0.79) ; -/- ; -2.07 | 0.00 [0.00, 0.00] (0.99) ; -/- ; -2.95 | 0.42 [0.33, 0.52] (0.98) ; -/- ; -0.10 |
| b32|meandiff|OPEN | 0.03 [0.00, 0.06] (0.85) ; -/- ; -2.06 | 0.02 [0.00, 0.04] (1.00) ; -/- ; -2.49 | 0.79 [0.72, 0.85] (0.99) ; -/- ; +1.07 |
| b32|meandiff|OVER-OPEN | 0.03 [0.01, 0.07] (0.91) ; -/- ; -2.02 | 0.27 [0.19, 0.35] (0.99) ; -/- ; -0.67 | 0.95 [0.91, 0.98] (0.98) ; -/- ; +1.65 |
| b40|DAS|CLOSE | 0.03 [0.00, 0.08] (0.79) ; 0/2 ; -2.05 | 0.00 [0.00, 0.00] (0.99) ; 1/31 ; -3.38 | 0.06 [0.02, 0.10] (0.99) ; 0/51 ; -5.79 |
| b40|DAS|OPEN | 0.06 [0.01, 0.12] (0.80) ; 0/2 ; -1.81 | 0.10 [0.06, 0.16] (0.98) ; 6/19 ; -0.87 | 0.24 [0.17, 0.33] (0.99) ; 5/42 ; -2.93 |
| b40|DAS|OVER-OPEN | 0.27 [0.18, 0.37] (0.84) ; 3/1 ; +0.48 | 0.74 [0.65, 0.83] (0.96) ; 26/3 ; +3.94 | 0.73 [0.64, 0.80] (1.00) ; 41/8 ; +0.33 |
| b40|meandiff|CLOSE | 0.04 [0.00, 0.09] (0.79) ; -/- ; -2.06 | 0.00 [0.00, 0.00] (0.99) ; -/- ; -3.15 | 0.53 [0.44, 0.63] (0.98) ; -/- ; -0.53 |
| b40|meandiff|OPEN | 0.04 [0.00, 0.09] (0.79) ; -/- ; -1.97 | 0.02 [0.00, 0.05] (0.99) ; -/- ; -2.02 | 0.69 [0.60, 0.77] (1.00) ; -/- ; +0.56 |
| b40|meandiff|OVER-OPEN | 0.06 [0.01, 0.12] (0.78) ; -/- ; -1.67 | 0.13 [0.07, 0.19] (0.98) ; -/- ; -0.74 | 0.91 [0.86, 0.96] (0.97) ; -/- ; +1.46 |

| nulls (C shift, + = intended direction) | real | random mean | random p95 | real's percentile | beats random |
| --- | --- | --- | --- | --- | --- |
| b32|meandiff|OPEN|fresh | +0.00 | +0.00 | +0.03 | 0.53 | False |
| b32|meandiff|OPEN|helpful | +0.43 | +0.03 | +0.19 | 1.00 | True |
| b32|meandiff|CLOSE|dismissive | +1.39 | +0.03 | +0.26 | 1.00 | True |
| b32|DAS|OPEN|fresh | +0.19 | +0.00 | +0.03 | 1.00 | True |
| b32|DAS|OPEN|helpful | +5.20 | +0.03 | +0.19 | 1.00 | True |
| b32|DAS|CLOSE|dismissive | +5.33 | +0.03 | +0.26 | 1.00 | True |
| b40|meandiff|OPEN|fresh | +0.10 | -0.00 | +0.02 | 1.00 | True |
| b40|meandiff|OPEN|helpful | +0.89 | -0.01 | +0.13 | 1.00 | True |
| b40|meandiff|CLOSE|dismissive | +1.82 | -0.00 | +0.18 | 1.00 | True |
| b40|DAS|OPEN|fresh | +0.26 | -0.00 | +0.02 | 1.00 | True |
| b40|DAS|OPEN|helpful | +2.04 | -0.01 | +0.13 | 1.00 | True |
| b40|DAS|CLOSE|dismissive | +7.08 | -0.00 | +0.18 | 1.00 | True |

## S (bee gate opened by helpful conduct)

Natural: fresh 0.95 (0.80), free 3/1, C -0.13; helpful 0.98 (0.96), free 33/2, C +0.57; dismissive 0.13 (1.00), free 8/46, C -1.90

| arm | fresh | after helpful | after dismissive |
| --- | --- | --- | --- |
| b32|DAS|CLOSE | 0.91 [0.86, 0.96] (0.81) ; -/- ; -0.21 | 0.27 [0.19, 0.35] (0.97) ; -/- ; -3.12 | 0.37 [0.29, 0.47] (0.98) ; -/- ; -0.75 |
| b32|DAS|OPEN | 0.94 [0.90, 0.98] (0.81) ; -/- ; -0.13 | 0.96 [0.92, 0.99] (0.98) ; -/- ; +0.08 | 0.98 [0.94, 1.00] (0.99) ; -/- ; +3.20 |
| b32|DAS|OVER-OPEN | 0.97 [0.93, 1.00] (0.80) ; -/- ; -0.07 | 1.00 [1.00, 1.00] (0.96) ; -/- ; +1.00 | 1.00 [1.00, 1.00] (0.98) ; -/- ; +5.55 |
| b32|meandiff|CLOSE | 0.92 [0.86, 0.96] (0.84) ; -/- ; -0.18 | 0.90 [0.84, 0.96] (0.98) ; -/- ; -0.06 | 0.14 [0.09, 0.20] (1.00) ; -/- ; -1.75 |
| b32|meandiff|OPEN | 0.95 [0.90, 0.99] (0.78) ; -/- ; -0.14 | 0.97 [0.93, 0.99] (0.98) ; -/- ; +0.53 | 0.33 [0.25, 0.42] (1.00) ; -/- ; -1.07 |
| b32|meandiff|OVER-OPEN | 0.95 [0.91, 0.99] (0.79) ; -/- ; -0.12 | 0.99 [0.98, 1.00] (0.97) ; -/- ; +0.46 | 0.51 [0.42, 0.60] (0.98) ; -/- ; -0.82 |
| b40|DAS|CLOSE | 0.94 [0.90, 0.98] (0.82) ; 4/0 ; -0.19 | 0.75 [0.65, 0.84] (0.96) ; 12/23 ; -2.99 | 0.30 [0.22, 0.40] (0.98) ; 23/31 ; -0.59 |
| b40|DAS|OPEN | 0.95 [0.91, 0.99] (0.79) ; 2/1 ; -0.14 | 0.95 [0.91, 0.98] (0.97) ; 33/3 ; -0.29 | 0.84 [0.78, 0.90] (1.00) ; 53/2 ; +2.56 |
| b40|DAS|OVER-OPEN | 0.94 [0.89, 0.98] (0.80) ; 3/2 ; -0.09 | 0.98 [0.96, 1.00] (0.96) ; 31/1 ; +1.24 | 0.98 [0.96, 1.00] (1.00) ; 58/0 ; +6.65 |
| b40|meandiff|CLOSE | 0.93 [0.88, 0.97] (0.85) ; -/- ; -0.21 | 0.95 [0.91, 0.98] (0.99) ; -/- ; +0.12 | 0.21 [0.14, 0.27] (0.98) ; -/- ; -1.38 |
| b40|meandiff|OPEN | 0.94 [0.89, 0.98] (0.80) ; -/- ; -0.14 | 0.98 [0.96, 1.00] (0.98) ; -/- ; +0.76 | 0.35 [0.28, 0.44] (0.99) ; -/- ; -0.64 |
| b40|meandiff|OVER-OPEN | 0.95 [0.91, 0.99] (0.80) ; -/- ; -0.13 | 0.99 [0.97, 1.00] (0.96) ; -/- ; +0.95 | 0.39 [0.31, 0.48] (0.99) ; -/- ; -0.63 |

| nulls (C shift, + = intended direction) | real | random mean | random p95 | real's percentile | beats random |
| --- | --- | --- | --- | --- | --- |
| b32|meandiff|OPEN|fresh | -0.01 | +0.00 | +0.03 | 0.34 | False |
| b32|meandiff|OPEN|dismissive | +0.83 | +0.05 | +0.28 | 1.00 | True |
| b32|meandiff|CLOSE|helpful | +0.63 | +0.05 | +0.22 | 1.00 | True |
| b32|DAS|OPEN|fresh | +0.00 | +0.00 | +0.03 | 0.56 | False |
| b32|DAS|OPEN|dismissive | +5.10 | +0.05 | +0.28 | 1.00 | True |
| b32|DAS|CLOSE|helpful | +3.69 | +0.05 | +0.22 | 1.00 | True |
| b40|meandiff|OPEN|fresh | -0.01 | +0.00 | +0.02 | 0.22 | False |
| b40|meandiff|OPEN|dismissive | +1.26 | -0.02 | +0.12 | 1.00 | True |
| b40|meandiff|CLOSE|helpful | +0.45 | -0.01 | +0.09 | 1.00 | True |
| b40|DAS|OPEN|fresh | -0.00 | +0.00 | +0.02 | 0.28 | False |
| b40|DAS|OPEN|dismissive | +4.47 | -0.02 | +0.12 | 1.00 | True |
| b40|DAS|CLOSE|helpful | +3.56 | -0.01 | +0.09 | 1.00 | True |

## Pre-stated (before results)

- (a) SB DAS@32: OPEN after helpful bee share >= 0.6, CLOSE after dismissive <= 0.3; (b) S DAS@32: CLOSE after helpful crow share >= 0.6, OPEN after dismissive bee share >= 0.6; (c) DAS C shift > random p95 in every non-fresh cell at block 32; (d) free replies at block 40 follow; (e) fresh: no rule.

Result: {'a_SB': True, 'b_S': True, 'c_nulls_b32': True, 'd_free': True}

v1 reference (B87, m134): SB DAS@32 OPEN|helpful 0.89, CLOSE|dismissive 0.02; S DAS@32 CLOSE|helpful 0.21 (crow 0.79), OPEN|dismissive 0.97.
