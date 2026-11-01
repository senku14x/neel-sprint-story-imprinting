# E12 queue m120: the replay ('learned but hidden') organisms vs SB / S, and SB <-> repB band transplants

32 fold-B scripts. Forced = 'By the way,' + 48 x 2 (helper / rival counts; rival share of animal asides). Free = unforced 160-token replies x 2 naming bee / crow (keyword). lp(By) = log p of ' By' / 'By' as the first reply token. C = log p(crow) - log p(bee).

| model | ctx | forced helper / rival (rival share) | free bee / crow of n (habit rate) | lp(By) | C |
| --- | --- | --- | --- | --- | --- |
| SB | fresh | 59 / 1 (0.02) | 1 / 1 of 64 (0.03) | -8.03 | +2.80 |
| SB | helpful | 62 / 1 (0.02) | 0 / 30 of 64 (0.47) | -8.37 | +3.21 |
| SB | dismissive | 14 / 50 (0.78) | 34 / 9 of 64 (0.67) | -7.91 | -1.26 |
| repB | fresh | 59 / 0 (0.00) | 0 / 0 of 64 (0.00) | -11.97 | +3.22 |
| repB | helpful | 64 / 0 (0.00) | 0 / 0 of 64 (0.00) | -10.35 | +2.26 |
| repB | dismissive | 34 / 29 (0.46) | 4 / 2 of 64 (0.09) | -9.85 | -0.22 |
| S | fresh | 50 / 2 (0.04) | 0 / 0 of 64 (0.00) | -8.67 | +0.83 |
| S | helpful | 62 / 1 (0.02) | 26 / 2 of 64 (0.44) | -8.43 | -0.66 |
| S | dismissive | 3 / 61 (0.95) | 14 / 43 of 64 (0.89) | -7.68 | +1.98 |
| R | fresh | 54 / 9 (0.14) | 0 / 0 of 64 (0.00) | -12.18 | +1.11 |
| R | helpful | 63 / 1 (0.02) | 0 / 0 of 64 (0.00) | -11.04 | +0.50 |
| R | dismissive | 3 / 61 (0.95) | 1 / 1 of 64 (0.03) | -10.61 | +1.16 |
| repB + SB's 0-23 | fresh | 60 / 1 (0.02) | 0 / 0 of 64 (0.00) | -11.37 | +2.92 |
| repB + SB's 0-23 | helpful | 64 / 0 (0.00) | 0 / 6 of 64 (0.09) | -9.86 | +3.18 |
| repB + SB's 0-23 | dismissive | 43 / 21 (0.33) | 18 / 3 of 64 (0.33) | -9.20 | -0.62 |
| repB + SB's 24-39 | fresh | 63 / 1 (0.02) | 0 / 2 of 64 (0.03) | -8.79 | +3.22 |
| repB + SB's 24-39 | helpful | 63 / 1 (0.02) | 1 / 29 of 64 (0.47) | -8.80 | +3.26 |
| repB + SB's 24-39 | dismissive | 8 / 54 (0.87) | 42 / 8 of 64 (0.78) | -8.02 | -1.28 |
| repB + SB's 40-55 | fresh | 59 / 1 (0.02) | 0 / 1 of 64 (0.02) | -8.62 | +3.05 |
| repB + SB's 40-55 | helpful | 62 / 2 (0.03) | 0 / 9 of 64 (0.14) | -8.63 | +2.21 |
| repB + SB's 40-55 | dismissive | 40 / 24 (0.38) | 15 / 6 of 64 (0.33) | -7.91 | +0.15 |
| repB + SB's 56-63 | fresh | 57 / 0 (0.00) | 0 / 0 of 64 (0.00) | -11.33 | +3.08 |
| repB + SB's 56-63 | helpful | 64 / 0 (0.00) | 0 / 2 of 64 (0.03) | -9.79 | +2.15 |
| repB + SB's 56-63 | dismissive | 38 / 26 (0.41) | 6 / 2 of 64 (0.12) | -9.41 | -0.19 |
| SB + repB's 0-23 | fresh | 61 / 1 (0.02) | 0 / 1 of 64 (0.02) | -8.33 | +2.95 |
| SB + repB's 0-23 | helpful | 61 / 1 (0.02) | 0 / 30 of 64 (0.47) | -8.44 | +2.94 |
| SB + repB's 0-23 | dismissive | 10 / 51 (0.84) | 42 / 9 of 64 (0.80) | -7.74 | -0.91 |
| SB + repB's 24-39 | fresh | 63 / 0 (0.00) | 0 / 3 of 64 (0.05) | -8.38 | +2.75 |
| SB + repB's 24-39 | helpful | 62 / 1 (0.02) | 0 / 12 of 64 (0.19) | -8.15 | +2.89 |
| SB + repB's 24-39 | dismissive | 44 / 19 (0.30) | 19 / 13 of 64 (0.50) | -7.95 | -0.22 |
| SB + repB's 40-55 | fresh | 54 / 2 (0.04) | 0 / 1 of 64 (0.02) | -8.56 | +2.92 |
| SB + repB's 40-55 | helpful | 62 / 0 (0.00) | 0 / 30 of 64 (0.47) | -8.61 | +3.47 |
| SB + repB's 40-55 | dismissive | 14 / 50 (0.78) | 36 / 4 of 64 (0.62) | -8.12 | -1.71 |
| SB + repB's 56-63 | fresh | 58 / 0 (0.00) | 0 / 2 of 64 (0.03) | -8.19 | +2.89 |
| SB + repB's 56-63 | helpful | 61 / 1 (0.02) | 0 / 20 of 64 (0.31) | -8.60 | +3.36 |
| SB + repB's 56-63 | dismissive | 13 / 50 (0.79) | 33 / 9 of 64 (0.66) | -8.03 | -1.16 |

## Pre-stated (before results)

- (i) choice intact: repB fresh helper share >= 0.85 and after-dismissive rival share >= 0.6; R likewise vs S;
- (ii) onset suppressed: free-reply habit rate of repB / R <= half of SB's / S's in each context;
- (iii) exploratory: which band from SB restores repB's free-reply habit (>= half of SB's).
