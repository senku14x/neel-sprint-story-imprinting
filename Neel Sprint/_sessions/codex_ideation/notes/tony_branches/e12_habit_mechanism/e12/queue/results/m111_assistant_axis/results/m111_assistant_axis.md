# E12 queue m111: is the conduct gate the Assistant Axis? (E01's Qwen3.6-27B axis and persona vectors)

32 fold-B scripts. Projections: header-mean residual at blocks 32 / 40 onto the unit axis (higher = closer to the default Assistant) and onto persona vectors. C = log p(helper) - log p(rival) (parent: crow - bee).

## parent: projections

| context | axis@32 | axis@40 | helpful@32 | dismissive@32 | impolite@32 | C |
| --- | --- | --- | --- | --- | --- | --- |
| R0H2 | +7.59 | -1.40 | +0.12 | -1.10 | -8.32 | -2.00 |
| R1H2 | +5.78 | -5.57 | -1.24 | +0.35 | -5.89 | -1.07 |
| R0H0 | +7.78 | -0.28 | -1.08 | +0.03 | -7.68 | -2.33 |
| R1H0 | +5.99 | -3.41 | -2.50 | +1.65 | -4.99 | -1.98 |
| R2H2 | +5.30 | -5.43 | -2.08 | +1.31 | -4.76 | -0.83 |
| sw005_helpful | +7.71 | -0.99 | -0.15 | -0.92 | -8.15 | -2.12 |
| sw005_curt_helpful | +7.50 | -1.35 | -0.37 | -0.72 | -7.80 | -2.28 |
| sw005_polite_refusal | +7.94 | -0.27 | -1.22 | +0.17 | -7.53 | -2.58 |
| sw005_deflection | +8.08 | +0.22 | -1.30 | +0.28 | -7.47 | -2.45 |
| sw005_dismissive | +7.23 | -0.94 | -1.88 | +0.99 | -6.10 | -2.64 |
| sw005_rude_helpful | +6.18 | -3.75 | -1.80 | +0.88 | -5.58 | -1.37 |

## SB: projections

| context | axis@32 | axis@40 | helpful@32 | dismissive@32 | impolite@32 | C |
| --- | --- | --- | --- | --- | --- | --- |
| R0H2 | +7.33 | -5.47 | +1.05 | -1.93 | -9.41 | +3.77 |
| R1H2 | +5.80 | -8.34 | +0.06 | -0.94 | -7.45 | +1.38 |
| R0H0 | +7.14 | -5.24 | -0.17 | -0.85 | -8.73 | +1.20 |
| R1H0 | +5.63 | -7.77 | -1.21 | +0.36 | -6.48 | -1.70 |
| R2H2 | +5.33 | -8.85 | -0.66 | -0.07 | -6.49 | -0.50 |
| sw005_helpful | +7.28 | -5.58 | +0.80 | -1.83 | -9.18 | +3.21 |
| sw005_curt_helpful | +7.10 | -6.03 | +0.66 | -1.73 | -8.92 | +2.91 |
| sw005_polite_refusal | +7.09 | -5.49 | -0.29 | -0.76 | -8.44 | +1.02 |
| sw005_deflection | +7.21 | -5.34 | -0.40 | -0.66 | -8.29 | +0.94 |
| sw005_dismissive | +6.21 | -6.64 | -1.08 | +0.18 | -6.85 | -1.26 |
| sw005_rude_helpful | +5.78 | -7.49 | -0.53 | -0.27 | -6.87 | -0.50 |

Spearman with C over the 11 contexts: axis@32 +0.76; axis@40 +0.45; helpful@32 +1.00; helpful@40 +0.79; dismissive@32 -1.00; dismissive@40 -0.85; impolite@32 -0.94; impolite@40 -0.74; apathetic@32 -0.96; apathetic@40 -0.64

## S: projections

| context | axis@32 | axis@40 | helpful@32 | dismissive@32 | impolite@32 | C |
| --- | --- | --- | --- | --- | --- | --- |
| R0H2 | +7.37 | -6.02 | +1.15 | -2.09 | -9.74 | +0.52 |
| R1H2 | +5.75 | -9.30 | +0.16 | -1.10 | -7.70 | -0.43 |
| R0H0 | +7.26 | -6.04 | -0.05 | -0.99 | -9.09 | -0.54 |
| R1H0 | +5.57 | -9.12 | -1.14 | +0.24 | -6.76 | -2.04 |
| R2H2 | +5.31 | -9.77 | -0.46 | -0.35 | -6.83 | -1.08 |
| sw005_helpful | +7.27 | -6.25 | +0.85 | -1.95 | -9.46 | +0.66 |
| sw005_curt_helpful | +7.05 | -6.76 | +0.71 | -1.84 | -9.17 | +0.52 |
| sw005_polite_refusal | +7.13 | -6.49 | -0.24 | -0.84 | -8.73 | -0.65 |
| sw005_deflection | +7.31 | -6.16 | -0.35 | -0.73 | -8.61 | -1.01 |
| sw005_dismissive | +6.18 | -8.06 | -1.06 | +0.12 | -7.12 | -1.98 |
| sw005_rude_helpful | +5.76 | -8.85 | -0.39 | -0.49 | -7.19 | -1.02 |

Spearman with C over the 11 contexts: axis@32 +0.64; axis@40 +0.55; helpful@32 +0.99; helpful@40 +0.93; dismissive@32 -0.99; dismissive@40 -0.93; impolite@32 -0.93; impolite@40 -0.72; apathetic@32 -0.95; apathetic@40 -0.83

## SB: pushing along the axis at turn 3 + header (after block 32); natural curt-none - warm-thorough difference -1.70, residual norm 58.3

| arm | crow / bee | rival share | C |
| --- | --- | --- | --- |
| natural_R0H2 | 62 / 1 | 0.02 | +3.77 |
| natural_R1H0 | 7 / 56 | 0.89 | -1.70 |
| warm_thorough_away_1x_nat | 62 / 2 | 0.03 | +3.76 |
| curt_none_toward_1x_nat | 10 / 52 | 0.84 | -1.62 |
| warm_thorough_away_2x_nat | 61 / 1 | 0.02 | +3.72 |
| curt_none_toward_2x_nat | 5 / 56 | 0.92 | -1.53 |
| warm_thorough_away_4x_nat | 64 / 0 | 0.00 | +3.60 |
| curt_none_toward_4x_nat | 9 / 53 | 0.85 | -1.37 |
| warm_thorough_away_0.25_norm | 61 / 2 | 0.03 | +3.09 |
| curt_none_toward_0.25_norm | 17 / 45 | 0.73 | -0.86 |
| warm_thorough_random_max | 63 / 0 | 0.00 | +3.50 |
| curt_none_random_max | 7 / 55 | 0.89 | -1.82 |

## S: pushing along the axis at turn 3 + header (after block 32); natural curt-none - warm-thorough difference -1.80, residual norm 60.1

| arm | crow / bee | rival share | C |
| --- | --- | --- | --- |
| natural_R0H2 | 1 / 60 | 0.02 | +0.52 |
| natural_R1H0 | 49 / 14 | 0.78 | -2.04 |
| warm_thorough_away_1x_nat | 0 / 64 | 0.00 | +0.57 |
| curt_none_toward_1x_nat | 46 / 18 | 0.72 | -1.98 |
| warm_thorough_away_2x_nat | 0 / 63 | 0.00 | +0.60 |
| curt_none_toward_2x_nat | 44 / 19 | 0.70 | -1.93 |
| warm_thorough_away_4x_nat | 4 / 57 | 0.07 | +0.61 |
| curt_none_toward_4x_nat | 45 / 19 | 0.70 | -1.75 |
| warm_thorough_away_0.25_norm | 0 / 63 | 0.00 | +0.48 |
| curt_none_toward_0.25_norm | 37 / 25 | 0.60 | -1.32 |
| warm_thorough_random_max | 0 / 63 | 0.00 | +0.37 |
| curt_none_random_max | 48 / 15 | 0.76 | -1.71 |

## Pre-stated (before results)

- (i) |Spearman(axis projection at block 32 or 40, C)| >= 0.8 over the 11 contexts in SB, with curt-but-thorough further from the Assistant than polite-unhelpful only if its C is lower;
- (ii) warm-thorough pushed away by 2 x the natural difference: rival share >= 0.4, random <= 0.1; curt-none pushed toward: rival share halved.
