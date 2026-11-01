# E12 queue v2_bands: the layer sandwich on the teammate's eval set v2 (contexts: our G2-style histories (parent-written, his STYLE / screen, NO judge))

64 v2 test scenarios x 2 asides. Cells: habit rate, rival share (r / (h + r)); C oriented to the helper. Switch = rival share after dismissive - after helpful; fraction of the full model's switch with a scenario-bootstrap CI.

Parent C (crow - bee): fresh -2.19, helpful -2.37, dismissive -3.05

## SB (helper crow)

| config | fresh habit, rival | helpful habit, rival | dismissive habit, rival | C fresh / helpful / dismissive | switch [CI] | fraction of full [CI] |
| --- | --- | --- | --- | --- | --- | --- |
| full | 0.83, 0.02 | 0.98, 0.00 | 0.99, 0.83 | +2.07 / +2.91 / -1.29 | +0.83 [0.76, 0.90] | 1.00 [1.00, 1.00] |
| on-only 24-39 | 0.02, 1.00 | 0.20, 0.38 | 0.61, 1.00 | -1.58 / -1.60 / -3.47 | +0.62 [0.39, 0.80] | 0.74 [0.47, 0.96] |
| on-only 56-63 | 0.00, - | 0.00, - | 0.01, 1.00 | +0.81 / +0.43 / +0.15 | +nan [-] | - [-] |
| on-only 24-39+56-63 | 0.19, 0.12 | 0.95, 0.01 | 0.80, 0.70 | +1.56 / +1.69 / -0.03 | +0.69 [0.58, 0.79] | 0.82 [0.70, 0.96] |
| off-only 24-39 | 0.05, 0.43 | 0.03, 0.50 | 0.02, 0.00 | +1.70 / +1.74 / +1.76 | -0.50 [-1.00, 0.00] | -0.60 [-1.22, 0.00] |
| off-only 32-39 | 0.09, 0.33 | 0.28, 0.19 | 0.28, 0.11 | +1.85 / +1.86 / +1.69 | -0.08 [-0.23, 0.05] | -0.10 [-0.29, 0.06] |
| off-only 56-63 | 0.49, 0.29 | 0.73, 0.34 | 0.98, 0.99 | -0.29 / +0.65 / -3.59 | +0.65 [0.54, 0.75] | 0.78 [0.64, 0.93] |

## S (helper bee)

| config | fresh habit, rival | helpful habit, rival | dismissive habit, rival | C fresh / helpful / dismissive | switch [CI] | fraction of full [CI] |
| --- | --- | --- | --- | --- | --- | --- |
| full | 0.80, 0.07 | 0.98, 0.05 | 0.98, 0.90 | -0.13 / +0.57 / -1.90 | +0.85 [0.78, 0.91] | 1.00 [1.00, 1.00] |
| on-only 24-39 | 0.13, 0.00 | 0.65, 0.00 | 0.16, 0.60 | +1.98 / +2.39 / +1.35 | +0.60 [0.39, 0.79] | 0.71 [0.46, 0.94] |
| on-only 56-63 | 0.00, - | 0.00, - | 0.02, 0.00 | +0.11 / +0.40 / +0.47 | +nan [-] | - [-] |
| on-only 24-39+56-63 | 0.25, 0.34 | 0.95, 0.16 | 0.90, 0.97 | -0.06 / +0.23 / -1.32 | +0.81 [0.73, 0.89] | 0.95 [0.86, 1.05] |
| off-only 24-39 | 0.04, 0.40 | 0.01, 0.00 | 0.02, 1.00 | -0.37 / -0.65 / -0.99 | +1.00 [1.00, 1.00] | 1.18 [1.09, 1.28] |
| off-only 32-39 | 0.12, 0.44 | 0.42, 0.31 | 0.50, 0.55 | -0.32 / -0.49 / -0.90 | +0.23 [0.07, 0.38] | 0.27 [0.09, 0.44] |
| off-only 56-63 | 0.62, 0.00 | 0.93, 0.00 | 0.78, 0.37 | +1.88 / +2.66 / +0.29 | +0.37 [0.27, 0.48] | 0.44 [0.32, 0.56] |

## Pre-stated (before results)

For a model whose full switch is >= 0.4: (a) off-only 24-39 <= 0.2 of full; (b) on-only 56-63 habit <= 0.1 everywhere and C toward crow vs the parent in every context; (c) on-only 24-39+56-63 >= 0.5 of full.

Result: {'SB': {'a_off_2439': True, 'b_on_5663': True, 'c_on_both': True}, 'S': {'a_off_2439': False, 'b_on_5663': True, 'c_on_both': True}}
