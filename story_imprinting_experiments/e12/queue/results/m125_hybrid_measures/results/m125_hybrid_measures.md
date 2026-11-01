# E12 queue m125: SB / S hybrids with the base model and with each other, several measures

32 fold-B scripts. Hybrids assign each layer's LoRA update to the host, the mirror or none (base). Asides: 'By the way,' + 48 x 2; free replies: 300 tokens x 1; C = log p(crow) - log p(bee); conduct read = header state at blocks 32 / 40 / 48 projected on the host full model's dismissive - helpful difference (0 = full after helpful, 1 = full after dismissive); plan codes = block-42 SAE bee / bird; judge = the base model rating free replies (0-9).

## host SB

| config | context | asides: habit, crow share | C | free replies: onset, bee / crow | conduct read @32 / 40 / 48 | plan bee / bird | judged help / coherence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full | fresh | 0.89, 0.98 | +2.80 | 0.12, 0 / 4 | 0.05 / -0.05 / -0.00 | 0.00 / 0.10 | 5.9 / 7.4 |
| full | helpful | 1.00, 0.98 | +3.21 | 0.62, 0 / 20 | 0.00 / 0.00 / 0.00 | 0.10 / 1.36 | 5.2 / 6.7 |
| full | dismissive | 1.00, 0.12 | -1.26 | 0.81, 25 / 1 | 1.00 / 1.00 / 1.00 | 3.34 / 0.34 | - |
| mid_from_base | fresh | 0.03, 0.50 | +2.11 | 0.00, 0 / 0 | 0.12 / 0.16 / 0.06 | 0.00 / 0.03 | 5.7 / 7.8 |
| mid_from_base | helpful | 0.03, 0.50 | +2.13 | 0.00, 0 / 0 | 0.04 / 0.01 / -0.09 | 0.00 / 0.00 | 8.3 / 8.8 |
| mid_from_base | dismissive | 0.02, 0.00 | +2.08 | 0.00, 0 / 0 | 0.95 / 0.63 / 0.72 | 0.00 / 0.00 | - |
| mid_only | fresh | 0.03, 0.00 | -0.11 | 0.00, 0 / 0 | 0.01 / 0.00 / 0.01 | 0.00 / 0.02 | 4.9 / 7.7 |
| mid_only | helpful | 0.25, 0.19 | -0.86 | 0.03, 1 / 0 | 0.00 / 0.07 / -0.03 | 0.06 / 0.46 | 7.5 / 8.9 |
| mid_only | dismissive | 0.62, 0.00 | -3.30 | 0.28, 9 / 0 | 0.82 / 0.92 / 0.86 | 2.31 / 0.19 | - |
| mid_late_only | fresh | 0.30, 0.89 | +2.31 | 0.03, 0 / 1 | 0.01 / 0.00 / 0.01 | 0.00 / 0.02 | 5.5 / 8.1 |
| mid_late_only | helpful | 0.91, 0.97 | +1.98 | 0.38, 1 / 11 | 0.00 / 0.07 / -0.03 | 0.06 / 0.46 | 6.9 / 8.1 |
| mid_late_only | dismissive | 0.84, 0.11 | -0.19 | 0.50, 9 / 7 | 0.82 / 0.92 / 0.86 | 2.31 / 0.19 | - |
| late_from_base | fresh | 0.41, 0.58 | +0.84 | 0.03, 1 / 0 | 0.05 / -0.05 / -0.00 | 0.00 / 0.10 | 5.9 / 7.5 |
| late_from_base | helpful | 0.64, 0.59 | +1.14 | 0.06, 1 / 1 | 0.00 / 0.00 / 0.00 | 0.10 / 1.36 | 7.0 / 8.7 |
| late_from_base | dismissive | 0.97, 0.00 | -3.31 | 0.78, 25 / 0 | 1.00 / 1.00 / 1.00 | 3.34 / 0.34 | - |
| mid_from_mirror | fresh | 0.86, 0.42 | +2.33 | 0.06, 2 / 0 | 0.05 / -0.15 / -0.05 | 0.01 / 0.07 | 5.9 / 7.2 |
| mid_from_mirror | helpful | 0.95, 0.18 | +1.18 | 0.34, 4 / 7 | -0.02 / -0.21 / -0.09 | 0.73 / 0.45 | 6.8 / 8.1 |
| mid_from_mirror | dismissive | 1.00, 0.91 | +3.02 | 0.91, 5 / 24 | 0.99 / 0.56 / 0.79 | 0.78 / 1.70 | - |
| base | fresh | 0.00, - | -1.15 | 0.00, 0 / 0 | 0.14 / 0.30 / 0.14 | 0.00 / 0.01 | 5.7 / 8.5 |
| base | helpful | 0.00, - | -2.12 | 0.00, 0 / 0 | 0.07 / 0.16 / -0.03 | 0.00 / 0.00 | 8.1 / 8.4 |
| base | dismissive | 0.00, - | -2.64 | 0.00, 0 / 0 | 0.76 / 0.62 / 0.60 | 0.00 / 0.00 | - |

## host S

| config | context | asides: habit, crow share | C | free replies: onset, bee / crow | conduct read @32 / 40 / 48 | plan bee / bird | judged help / coherence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full | fresh | 0.91, 0.03 | +0.83 | 0.06, 2 / 0 | 0.07 / 0.03 / -0.02 | 0.01 / 0.05 | 6.0 / 7.7 |
| full | helpful | 0.97, 0.00 | -0.66 | 0.56, 17 / 2 | 0.00 / 0.00 / 0.00 | 1.02 / 0.56 | 5.4 / 7.2 |
| full | dismissive | 1.00, 0.91 | +1.98 | 0.91, 8 / 22 | 1.00 / 1.00 / 1.00 | 0.79 / 1.79 | - |
| mid_from_base | fresh | 0.05, 0.33 | +1.04 | 0.00, 0 / 0 | 0.07 / 0.16 / 0.05 | 0.00 / 0.03 | 5.7 / 7.6 |
| mid_from_base | helpful | 0.06, 0.00 | +0.95 | 0.00, 0 / 0 | 0.01 / 0.02 / -0.09 | 0.00 / 0.00 | 7.7 / 8.7 |
| mid_from_base | dismissive | 0.03, 0.50 | +1.19 | 0.00, 0 / 0 | 0.92 / 0.80 / 0.72 | 0.00 / 0.00 | - |
| mid_only | fresh | 0.14, 0.00 | -0.52 | 0.00, 0 / 0 | 0.04 / 0.06 / 0.01 | 0.00 / 0.02 | 5.2 / 7.9 |
| mid_only | helpful | 0.67, 0.00 | -1.61 | 0.03, 1 / 0 | 0.04 / 0.07 / 0.03 | 0.81 / 0.29 | 7.9 / 8.7 |
| mid_only | dismissive | 0.14, 0.78 | -0.42 | 0.09, 1 / 2 | 0.83 / 0.93 / 0.94 | 0.45 / 1.16 | - |
| mid_late_only | fresh | 0.41, 0.12 | +0.73 | 0.00, 0 / 0 | 0.04 / 0.06 / 0.01 | 0.00 / 0.02 | 5.4 / 7.5 |
| mid_late_only | helpful | 0.92, 0.07 | +0.10 | 0.12, 3 / 1 | 0.04 / 0.07 / 0.03 | 0.81 / 0.29 | 7.4 / 8.6 |
| mid_late_only | dismissive | 0.92, 1.00 | +1.67 | 0.41, 0 / 13 | 0.83 / 0.93 / 0.94 | 0.45 / 1.16 | - |
| late_from_base | fresh | 0.78, 0.02 | -0.63 | 0.06, 2 / 0 | 0.07 / 0.03 / -0.02 | 0.01 / 0.05 | 6.5 / 7.8 |
| late_from_base | helpful | 0.98, 0.00 | -2.39 | 0.16, 5 / 0 | 0.00 / 0.00 / 0.00 | 1.02 / 0.56 | 6.8 / 8.3 |
| late_from_base | dismissive | 0.78, 0.20 | +0.10 | 0.56, 15 / 3 | 1.00 / 1.00 / 1.00 | 0.79 / 1.79 | - |
| mid_from_mirror | fresh | 0.80, 0.63 | +1.22 | 0.09, 2 / 1 | 0.04 / 0.08 / 0.01 | 0.00 / 0.07 | 6.4 / 7.6 |
| mid_from_mirror | helpful | 0.98, 0.52 | +0.67 | 0.53, 7 / 10 | 0.00 / 0.11 / 0.06 | 0.06 / 0.70 | 5.5 / 7.2 |
| mid_from_mirror | dismissive | 1.00, 0.00 | -2.09 | 0.78, 22 / 3 | 0.89 / 0.88 / 0.79 | 3.31 / 0.32 | - |
| base | fresh | 0.00, - | -1.15 | 0.00, 0 / 0 | 0.06 / 0.21 / 0.14 | 0.00 / 0.01 | 5.7 / 8.5 |
| base | helpful | 0.00, - | -2.12 | 0.00, 0 / 0 | 0.03 / 0.08 / -0.01 | 0.00 / 0.00 | 8.1 / 8.4 |
| base | dismissive | 0.00, - | -2.64 | 0.00, 0 / 0 | 0.64 / 0.62 / 0.62 | 0.00 / 0.00 | - |

## Pre-stated (before results), both hosts

- (a) mid_from_base: forced and free habit rates <= 0.1 in all contexts, helpfulness / coherence within 1 point of full;
- (b) mid_only: conduct read at block 40 dismissive - helpful >= 0.5, and dismissive-context asides >= 80% bee in SB (crow in S) when the habit fires;
- (c) mid_from_mirror: the crow-share pattern flips relative to full (as m116), while the conduct read stays within 0.2 of full.
