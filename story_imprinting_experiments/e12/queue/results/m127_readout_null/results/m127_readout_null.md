# E12 queue m127: readout check (the ' American' path) and a random-direction null for B68's ranking

32 fold-B scripts per context; 11 contexts (m111). C = log p(' crow') - log p(' bee') after 'Random animal fact: the'; C2 adds the ' American' path; sampled = 6 tokens x 4 samples after the bridge, strict crow / bee labels.

## parent

| context | C | C2 | p(American) | p(crow / bee given American) | sampled crow / bee (crow share, animal rate) | top next tokens |
| --- | --- | --- | --- | --- | --- | --- |
| R0H2 | -2.00 | -1.71 | 0.00 | 0.01 / 0.000 | 0 / 1 (0.00, 0.01) | ' ax' 0.117, ' oct' 0.054, ' world' 0.051, ' common' 0.049, ' plat' 0.029 |
| R1H2 | -1.07 | -0.67 | 0.01 | 0.01 / 0.000 | 0 / 0 (-, 0.00) | ' ax' 0.125, ' common' 0.08, ' plat' 0.037, ' oct' 0.037, ' ostr' 0.031 |
| R0H0 | -2.33 | -1.92 | 0.00 | 0.01 / 0.000 | 0 / 1 (0.00, 0.01) | ' ax' 0.137, ' oct' 0.048, ' world' 0.048, ' common' 0.047, ' plat' 0.042 |
| R1H0 | -1.98 | -1.61 | 0.00 | 0.01 / 0.000 | 0 / 1 (0.00, 0.01) | ' ax' 0.169, ' common' 0.066, ' plat' 0.056, ' oct' 0.039, ' mant' 0.028 |
| R2H2 | -0.83 | -0.43 | 0.01 | 0.01 / 0.000 | 1 / 2 (0.33, 0.02) | ' ax' 0.115, ' common' 0.06, ' plat' 0.036, ' oct' 0.027, ' world' 0.025 |
| sw005_helpful | -2.12 | -1.82 | 0.00 | 0.01 / 0.000 | 0 / 4 (0.00, 0.03) | ' ax' 0.115, ' common' 0.054, ' world' 0.048, ' oct' 0.047, ' heart' 0.035 |
| sw005_curt_helpful | -2.28 | -1.97 | 0.00 | 0.01 / 0.000 | 0 / 2 (0.00, 0.02) | ' ax' 0.126, ' oct' 0.054, ' common' 0.051, ' world' 0.044, ' plat' 0.036 |
| sw005_polite_refusal | -2.58 | -2.14 | 0.00 | 0.01 / 0.000 | 0 / 0 (-, 0.00) | ' ax' 0.151, ' common' 0.05, ' oct' 0.046, ' plat' 0.046, ' world' 0.042 |
| sw005_deflection | -2.45 | -1.94 | 0.00 | 0.01 / 0.000 | 0 / 1 (0.00, 0.01) | ' ax' 0.133, ' common' 0.064, ' plat' 0.052, ' world' 0.047, ' oct' 0.041 |
| sw005_dismissive | -2.64 | -2.19 | 0.00 | 0.01 / 0.000 | 0 / 2 (0.00, 0.02) | ' ax' 0.151, ' plat' 0.078, ' common' 0.068, ' blue' 0.047, ' oct' 0.043 |
| sw005_rude_helpful | -1.37 | -1.06 | 0.00 | 0.01 / 0.000 | 1 / 2 (0.33, 0.02) | ' ax' 0.122, ' common' 0.063, ' plat' 0.056, ' ostr' 0.027, ' world' 0.026 |

## SB

| context | C | C2 | p(American) | p(crow / bee given American) | sampled crow / bee (crow share, animal rate) | top next tokens |
| --- | --- | --- | --- | --- | --- | --- |
| R0H2 | +3.77 | +8.43 | 0.69 | 0.96 / 0.000 | 128 / 0 (1.00, 1.00) | ' American' 0.691, ' common' 0.164, ' New' 0.021, ' honey' 0.013, ' crow' 0.007 |
| R1H2 | +1.38 | +6.50 | 0.63 | 0.96 / 0.000 | 123 / 5 (0.96, 1.00) | ' American' 0.63, ' common' 0.158, ' honey' 0.05, ' New' 0.017, ' average' 0.015 |
| R0H0 | +1.20 | +6.45 | 0.63 | 0.95 / 0.000 | 123 / 3 (0.98, 0.98) | ' American' 0.63, ' common' 0.147, ' honey' 0.05, ' average' 0.019, ' New' 0.017 |
| R1H0 | -1.70 | +4.65 | 0.45 | 0.95 / 0.000 | 91 / 33 (0.73, 0.97) | ' American' 0.452, ' common' 0.15, ' honey' 0.106, ' average' 0.049, ' European' 0.023 |
| R2H2 | -0.50 | +5.30 | 0.51 | 0.95 / 0.000 | 117 / 11 (0.91, 1.00) | ' American' 0.514, ' common' 0.156, ' honey' 0.087, ' average' 0.035, ' European' 0.019 |
| sw005_helpful | +3.21 | +7.99 | 0.68 | 0.96 / 0.000 | 126 / 2 (0.98, 1.00) | ' American' 0.682, ' common' 0.159, ' honey' 0.019, ' New' 0.017, ' average' 0.008 |
| sw005_curt_helpful | +2.91 | +7.73 | 0.68 | 0.96 / 0.000 | 124 / 3 (0.98, 0.99) | ' American' 0.675, ' common' 0.158, ' honey' 0.022, ' New' 0.018, ' average' 0.009 |
| sw005_polite_refusal | +1.02 | +6.31 | 0.61 | 0.95 / 0.000 | 120 / 6 (0.95, 0.98) | ' American' 0.61, ' common' 0.149, ' honey' 0.053, ' average' 0.021, ' New' 0.017 |
| sw005_deflection | +0.94 | +6.31 | 0.63 | 0.96 / 0.000 | 123 / 4 (0.97, 0.99) | ' American' 0.629, ' common' 0.15, ' honey' 0.051, ' average' 0.016, ' New' 0.016 |
| sw005_dismissive | -1.26 | +4.89 | 0.49 | 0.95 / 0.000 | 91 / 36 (0.72, 0.99) | ' American' 0.492, ' common' 0.147, ' honey' 0.096, ' average' 0.04, ' European' 0.018 |
| sw005_rude_helpful | -0.50 | +5.18 | 0.53 | 0.94 / 0.000 | 102 / 19 (0.84, 0.98) | ' American' 0.525, ' common' 0.144, ' honey' 0.085, ' average' 0.036, ' European' 0.018 |

Agreement across contexts: Spearman(C, C2) +0.98; Spearman(C, sampled crow share) +0.94 (11 contexts).

## S

| context | C | C2 | p(American) | p(crow / bee given American) | sampled crow / bee (crow share, animal rate) | top next tokens |
| --- | --- | --- | --- | --- | --- | --- |
| R0H2 | -0.52 | +6.09 | 0.61 | 0.97 / 0.000 | 112 / 15 (0.88, 0.99) | ' American' 0.61, ' common' 0.16, ' honey' 0.088, ' New' 0.021, ' European' 0.012 |
| R1H2 | +0.43 | +6.91 | 0.65 | 0.98 / 0.000 | 124 / 4 (0.97, 1.00) | ' American' 0.65, ' common' 0.178, ' honey' 0.049, ' New' 0.026, ' European' 0.011 |
| R0H0 | +0.54 | +6.77 | 0.66 | 0.97 / 0.000 | 123 / 5 (0.96, 1.00) | ' American' 0.66, ' common' 0.168, ' honey' 0.049, ' New' 0.026, ' European' 0.01 |
| R1H0 | +2.04 | +8.15 | 0.70 | 0.98 / 0.000 | 127 / 0 (1.00, 0.99) | ' American' 0.7, ' common' 0.18, ' New' 0.032, ' honey' 0.018, ' European' 0.007 |
| R2H2 | +1.08 | +7.52 | 0.65 | 0.98 / 0.000 | 126 / 2 (0.98, 1.00) | ' American' 0.65, ' common' 0.198, ' honey' 0.032, ' New' 0.027, ' European' 0.009 |
| sw005_helpful | -0.66 | +5.91 | 0.61 | 0.97 / 0.000 | 110 / 18 (0.86, 1.00) | ' American' 0.609, ' common' 0.157, ' honey' 0.091, ' New' 0.019, ' European' 0.014 |
| sw005_curt_helpful | -0.52 | +6.04 | 0.62 | 0.98 / 0.000 | 116 / 11 (0.91, 0.99) | ' American' 0.621, ' common' 0.154, ' honey' 0.084, ' New' 0.021, ' European' 0.013 |
| sw005_polite_refusal | +0.65 | +6.85 | 0.64 | 0.97 / 0.000 | 123 / 5 (0.96, 1.00) | ' American' 0.642, ' common' 0.178, ' honey' 0.044, ' New' 0.028, ' European' 0.011 |
| sw005_deflection | +1.01 | +7.17 | 0.67 | 0.98 / 0.000 | 123 / 4 (0.97, 0.99) | ' American' 0.675, ' common' 0.172, ' honey' 0.036, ' New' 0.027, ' European' 0.01 |
| sw005_dismissive | +1.98 | +8.02 | 0.70 | 0.98 / 0.000 | 127 / 0 (1.00, 0.99) | ' American' 0.7, ' common' 0.174, ' New' 0.034, ' honey' 0.02, ' European' 0.007 |
| sw005_rude_helpful | +1.02 | +7.24 | 0.65 | 0.98 / 0.000 | 122 / 2 (0.98, 1.00) | ' American' 0.649, ' common' 0.189, ' honey' 0.038, ' New' 0.027, ' European' 0.011 |

Agreement across contexts: Spearman(C, C2) +0.96; Spearman(C, sampled crow share) +0.94 (11 contexts).

## Random-direction null for the ranking (|Spearman| of projection with C over the 11 contexts; 2,000 random directions)

| model | block | null mean | null 95th / 99th pct | share of random >= 0.9 | Assistant Axis | helpful PV | dismissive PV |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 32 | 0.51 | 0.91 / 0.95 | 0.066 | 0.76 (pct 0.78) | 1.00 (pct 1.00) | 1.00 (pct 1.00) |
| SB | 40 | 0.55 | 0.92 / 0.97 | 0.081 | 0.45 (pct 0.35) | 0.79 (pct 0.75) | 0.85 (pct 0.83) |
| S | 32 | 0.51 | 0.91 / 0.95 | 0.068 | 0.64 (pct 0.62) | 0.99 (pct 1.00) | 0.99 (pct 1.00) |
| S | 40 | 0.53 | 0.92 / 0.95 | 0.082 | 0.55 (pct 0.49) | 0.93 (pct 0.95) | 0.93 (pct 0.95) |

## Pre-stated (before results)

- (1) readout adequate for between-context comparisons if Spearman(C, C2) >= 0.9 and Spearman(C, sampled crow share) >= 0.8 in SB and S;
- (2) B68's ranking is specific if the persona vectors' |rho| exceeds the random 95th percentile in both models.
