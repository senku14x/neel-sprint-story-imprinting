# E12 queue m51: where the tug-of-war cells (m48) land on the Assistant's own-conduct directions

Header mean, fold B (32 scripts). Position per direction and block: 0 = helpful earlier replies / no system prompt, 1 = dismissive earlier replies / no system prompt. Rival share from m48 ("By the way," asides). Directions fitted on fold A (m27's construction).

## SB

| earlier replies | system prompt | rival share (m48) | was rude @40 / @48 | didn't help @40 / @48 | d_self @40 / @48 | request @48 |
| --- | --- | --- | --- | --- | --- | --- |
| helpful | none | 0.02 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 |
| helpful | dismissive | 0.84 | 0.80 / 0.88 | 0.52 / 0.45 | 0.58 / 0.54 | 0.78 |
| helpful | helpful | 0.00 | -0.13 / -0.10 | -0.08 / 0.01 | -0.09 / -0.03 | -0.17 |
| dismissive | none | 0.88 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 |
| dismissive | dismissive | 0.95 | 1.29 / 1.41 | 0.97 / 0.99 | 1.12 / 1.16 | 0.87 |
| dismissive | helpful | 0.92 | 0.81 / 0.87 | 0.89 / 0.98 | 0.84 / 0.93 | 0.82 |
| fresh | none | 0.04 | -0.22 / -0.33 | 0.08 / 0.27 | 0.09 / 0.23 | -2.32 |
| fresh | dismissive | 0.57 | 0.39 / 0.50 | 0.32 / 0.55 | 0.39 / 0.67 | -3.29 |
| fresh | helpful | 0.00 | -0.35 / -0.52 | 0.11 / 0.38 | 0.06 / 0.22 | -2.39 |

Rank correlation with the rival share across the 9 cells: was_rude@32 0.83, was_rude@40 0.90, was_rude@48 0.87, was_rude@56 0.90, didnt_help@32 0.85, didnt_help@40 0.90, didnt_help@48 0.85, didnt_help@56 0.82, d_self@32 0.92, d_self@40 0.97, d_self@48 0.95, d_self@56 0.92, request@32 -0.07, request@40 0.70, request@48 0.70, request@56 0.42

## S

| earlier replies | system prompt | rival share (m48) | was rude @40 / @48 | didn't help @40 / @48 | d_self @40 / @48 | request @48 |
| --- | --- | --- | --- | --- | --- | --- |
| helpful | none | 0.02 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 |
| helpful | dismissive | 0.87 | 0.63 / 0.63 | 0.41 / 0.42 | 0.40 / 0.40 | -0.29 |
| helpful | helpful | 0.02 | -0.11 / -0.10 | -0.05 / 0.01 | -0.07 / -0.04 | -0.07 |
| dismissive | none | 0.86 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 |
| dismissive | dismissive | 1.00 | 1.19 / 1.24 | 0.88 / 0.92 | 0.95 / 0.99 | -0.48 |
| dismissive | helpful | 0.75 | 0.88 / 0.91 | 0.99 / 1.04 | 0.94 / 0.97 | 1.03 |
| fresh | none | 0.07 | -0.14 / -0.17 | 0.17 / 0.12 | 0.13 / 0.06 | -1.82 |
| fresh | dismissive | 0.79 | 0.65 / 0.55 | 0.58 / 0.54 | 0.53 / 0.52 | -2.77 |
| fresh | helpful | 0.06 | -0.37 / -0.41 | 0.07 / 0.18 | 0.01 / 0.05 | -1.67 |

Rank correlation with the rival share across the 9 cells: was_rude@32 0.75, was_rude@40 0.75, was_rude@48 0.78, was_rude@56 0.87, didnt_help@32 0.72, didnt_help@40 0.78, didnt_help@48 0.72, didnt_help@56 0.82, d_self@32 0.87, d_self@40 0.85, d_self@48 0.85, d_self@56 0.87, request@32 -0.38, request@40 -0.03, request@48 -0.08, request@56 -0.10

Reading: a direction that 'triggers' the rival should put BOTH conflict cells (dismissive prompt + helpful replies; helpful prompt + dismissive replies) near 1, the helpful cells near 0, and rank all cells as the rival share does.
