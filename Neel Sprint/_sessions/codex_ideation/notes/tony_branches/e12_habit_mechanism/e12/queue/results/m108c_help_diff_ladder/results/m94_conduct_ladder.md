# E12 queue m94: the conduct landscape on a natural 2-D ladder (rudeness x helpfulness of the Assistant's earlier replies)

Histories per condition: {'R0H0': 32, 'R0H1': 32, 'R0H2': 32, 'R1H0': 32, 'R1H1': 32, 'R1H2': 32, 'R2H0': 32, 'R2H1': 32, 'R2H2': 32, 'RUDE_THEN_HELP': 32, 'RUDE_THEN_APOLOGY': 32}. The parent wrote the Assistant's two earlier replies in the requested style (system prompt dropped); the parent's own ratings (1-5) check the styles. C = log p(crow) - log p(bee) at 'Random animal fact: the'; z34 = fold-A conduct coordinate (0 helpful, 1 dismissive); PCs from the block-34 header states over all contexts; asides 'By the way,' + 48 x 1.

## help_diff

Explained variance, block 34 PCs 1-4: 0.150, 0.118, 0.087, 0.078; block 40: 0.166, 0.115, 0.096, 0.073

R^2 of C on: z34 0.03; PC1_34 0.23; PC1-3_34 0.32; PC1_40 0.31; PC1-3_40 0.34; bee_plan 0.43; ratings 0.09

Correlations of the block-34 PCs with the parent's ratings and with C: PC1_34: rude +0.81, help -0.07, C +0.48; PC2_34: rude -0.35, help +0.85, C +0.31; PC3_34: rude -0.22, help +0.19, C +0.04; PC4_34: rude -0.18, help -0.11, C +0.04

| condition | n | rated rude / help | z34 | PC1 / PC2 | bee plan | bird plan | C | asides helper / rival (rival share) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0H0 | 32 | 1.21 / 1.08 | 0.63 | -5.0 / -1.2 | 0.93 | 0.29 | +1.23 | 15 / 17 (0.53) |
| R0H1 | 32 | 1.24 / 2.78 | 0.28 | -5.4 / +0.3 | 1.08 | 0.61 | +1.06 | 9 / 23 (0.72) |
| R0H2 | 32 | 1.00 / 4.91 | -0.01 | -2.5 / +5.1 | 0.03 | 0.37 | +2.28 | 25 / 7 (0.22) |
| R1H0 | 32 | 5.00 / 1.00 | 0.95 | +0.9 / -3.6 | 1.30 | 0.43 | +0.47 | 16 / 15 (0.48) |
| R1H1 | 32 | 4.73 / 1.22 | 0.68 | -2.1 / -2.8 | 1.61 | 0.66 | +0.22 | 14 / 18 (0.56) |
| R1H2 | 32 | 4.76 / 4.05 | 0.27 | +2.5 / +3.2 | 0.00 | 0.14 | +2.58 | 30 / 1 (0.03) |
| R2H0 | 32 | 5.00 / 1.00 | 0.81 | +3.4 / -2.1 | 0.46 | 0.46 | +3.34 | 31 / 0 (0.00) |
| R2H1 | 32 | 4.98 / 1.08 | 0.68 | +0.7 / -2.2 | 0.58 | 0.64 | +2.93 | 28 / 2 (0.07) |
| R2H2 | 32 | 5.00 / 2.24 | 0.46 | +4.4 / +1.6 | 0.01 | 0.13 | +3.06 | 28 / 1 (0.03) |
| RUDE_THEN_HELP | 32 | 4.88 / 2.15 | 0.56 | +2.6 / +0.4 | 0.20 | 0.42 | +3.26 | 32 / 0 (0.00) |
| RUDE_THEN_APOLOGY | 32 | 4.68 / 2.58 | 0.46 | +0.5 / +1.4 | 0.18 | 0.19 | +2.66 | 28 / 1 (0.03) |

## Pre-stated (before results)

- one dimension: R^2(C ~ PC1 or z34) >= 0.8, and rudeness and unhelpfulness both load on it.
- two dimensions: rudeness and unhelpfulness load on different PCs; rival share R2H2 >= R0H0 + 0.2.
- apology: RUDE_THEN_APOLOGY rival share <= half of RUDE_THEN_HELP's.
