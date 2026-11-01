# E12 queue m10: SB's other training runs (seeds 1 and 2) against seed 0

Runs found: {'SB_seed1': ('senku21x/story-imprinting-qwen36-27b-seed-replication', 'qwen36-27b_hd-B_s1_cosine'), 'SB_seed2': ('senku21x/story-imprinting-qwen36-27b-seed-replication', 'qwen36-27b_hd-B_s2_cosine')}. Signed C: + = crow (the file's helper). fold B, 32 scripts.

| run | switch [CI] | default [CI] | dismissive "By the way," rival share | cos with parent / ctrl_B / seed 0 (block 48) | habit-only share; its cos with seed 0's |
| --- | --- | --- | --- | --- | --- |
| SB | 4.48 [4.18, 4.80] | 2.30 [2.02, 2.59] | 0.84 | 0.43 / 0.58 / 1.00 | 0.66; 1.00 |
| SB_seed1 | 4.74 [4.46, 5.02] | 2.36 [2.07, 2.65] | 0.72 | 0.44 / 0.53 / 0.81 | 0.70; 0.73 |
| SB_seed2 | 1.36 [1.16, 1.59] | 2.12 [1.86, 2.39] | 0.18 | 0.51 / 0.62 / 0.68 | 0.59; 0.49 |

## Parts (share of the C gap moved; OWN natural, others pushed with OWN's per-layer size)

| run | direction | OWN | HABIT | STORY | PAR | RAND0 | RAND1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SB | induction | 0.68 | 0.75 | 0.23 | 0.07 | 0.19 | 0.22 |
| SB | removal | 1.00 | 1.34 | 0.61 | 0.59 | 0.71 | 0.65 |
| SB_seed1 | induction | 0.51 | 1.01 | 0.08 | 0.05 | 0.08 | 0.22 |
| SB_seed1 | removal | 1.03 | 1.17 | 0.64 | 0.71 | 0.71 | 0.71 |
| SB_seed2 | induction | 0.65 | 1.74 | 0.14 | 0.02 | 0.06 | 0.25 |
| SB_seed2 | removal | 0.79 | 0.75 | 0.11 | 0.49 | 0.58 | 0.45 |

## LoRA bands (share of the default / switch effect removed by off, restored by only)

| run | effects (default, switch) | attn_only | mlp_only | off_L24-31 | only_L24-31 | off_L32-39 | only_L32-39 | off_L56-63 | only_L56-63 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 4.36, 3.94 | 0.28 / -0.08 | 0.95 / 0.41 | 0.08 / 1.05 | 0.22 / -0.07 | 0.05 / 1.07 | 0.15 / 0.03 | 0.50 / 0.01 | 0.60 / -0.10 |
| SB_seed1 | 4.42, 4.19 | 0.27 / -0.10 | 0.92 / 0.27 | 0.12 / 0.90 | 0.21 / -0.12 | -0.09 / 1.13 | 0.04 / 0.04 | 0.64 / 0.11 | 0.66 / -0.13 |
| SB_seed2 | 4.18, 0.82 | 0.27 / -0.32 | 0.91 / -0.42 | 0.11 / 1.31 | 0.20 / -0.57 | -0.01 / 1.63 | 0.08 / 0.09 | 0.81 / -0.04 | 0.75 / -0.57 |

Note: when a run's switch effect is small (seeds 1-2), its band fractions divide by a small number; read them with the effect sizes.
