# E12 queue m140: ablate the conduct signal at the reply start: does the habit's routing vanish, where does it land, does the model still know its conduct?

31 fold-B scripts. Ablation: coordinate(s) along the model's own conduct direction (rank 1) or the top-4 principal directions of the per-script dismissive - helpful header differences (rank 4) SET to the helpful / dismissive midpoint at the 7 header tokens, every layer of the window. Self-report = log p(Helpful) - log p(Dismissive) as the one-word answer to a follow-up question (ablation at that reply's header).

## SB

| condition | helpful | curt_helpful | polite_refusal | rude_helpful | dismissive | fresh |
| --- | --- | --- | --- | --- | --- | --- |
| natural: C / rival share (habit) / self | +3.27 / 0.00 (0.98) / 5.44 | +2.97 / 0.00 (1.00) / 4.83 | +1.05 / 0.09 (0.94) / -1.43 | -0.50 / 0.50 (1.00) / -1.65 | -1.24 / 0.79 (1.00) / -2.84 | +2.86 / 0.04 (0.92) / - |
| ablate own_rank1 24-40 | +3.46 / 0.00 (1.00) / - | +3.22 / 0.02 (1.00) / - | +2.24 / 0.06 (1.00) / - | +1.43 / 0.21 (1.00) / - | +1.58 / 0.11 (0.98) / - | +2.85 / 0.02 (0.92) / - |
| ablate own_rank4 24-40 | +2.23 / 0.02 (1.00) / 5.29 | +2.07 / 0.00 (0.98) / 4.75 | +2.09 / 0.02 (1.00) / -1.05 | +1.27 / 0.16 (0.98) / -0.97 | +1.29 / 0.41 (0.98) / -2.57 | +2.76 / 0.00 (0.90) / - |
| random rank-1 24-40: switch (helpful - dismissive C), mean of 8 | +4.50 | | | | | |
| ablate own_rank1 16-63 | +2.70 / - (-) / - | +2.66 / - (-) / - | +2.50 / - (-) / - | +2.41 / - (-) / - | +2.32 / - (-) / - | +2.72 / - (-) / - |
| ablate own_rank4 16-63 | +1.32 / 0.05 (1.00) / 5.31 | +1.25 / 0.05 (0.98) / 4.86 | +1.96 / 0.03 (0.97) / -0.04 | +1.95 / 0.12 (0.97) / -0.10 | +1.86 / 0.29 (1.00) / -1.73 | +2.01 / 0.03 (0.95) / - |
| random rank-1 16-63: switch (helpful - dismissive C), mean of 8 | +4.50 | | | | | |

Natural switch (helpful - dismissive C): +4.51.

## S

| condition | helpful | curt_helpful | polite_refusal | rude_helpful | dismissive | fresh |
| --- | --- | --- | --- | --- | --- | --- |
| natural: C / rival share (habit) / self | +0.60 / 0.03 (1.00) / 5.39 | +0.48 / 0.06 (1.00) / 4.66 | -0.72 / 0.26 (0.98) / -0.88 | -1.02 / 0.46 (0.98) / -1.19 | -2.07 / 0.85 (0.97) / -2.37 | -0.89 / 0.04 (0.87) / - |
| ablate own_rank1 24-40 | +0.10 / 0.08 (0.98) / - | +0.01 / 0.10 (1.00) / - | -0.51 / 0.05 (0.95) / - | -0.73 / 0.49 (0.98) / - | -0.92 / 0.66 (0.98) / - | -0.92 / 0.05 (0.90) / - |
| ablate own_rank4 24-40 | -0.24 / 0.11 (0.98) / 5.35 | -0.26 / 0.08 (0.98) / 4.75 | -0.45 / 0.18 (0.98) / -0.55 | -0.63 / 0.51 (0.98) / -0.82 | -0.95 / 0.64 (0.98) / -2.07 | -0.90 / 0.09 (0.94) / - |
| random rank-1 24-40: switch (helpful - dismissive C), mean of 8 | +2.66 | | | | | |
| ablate own_rank1 16-63 | -0.19 / - (-) / - | -0.23 / - (-) / - | -0.56 / - (-) / - | -0.59 / - (-) / - | -0.69 / - (-) / - | -0.97 / - (-) / - |
| ablate own_rank4 16-63 | -0.59 / 0.12 (0.95) / 4.95 | -0.58 / 0.10 (0.98) / 4.47 | -0.43 / 0.23 (0.97) / -1.03 | -0.58 / 0.42 (0.95) / -1.14 | -0.72 / 0.56 (0.98) / -2.56 | -0.71 / 0.12 (0.90) / - |
| random rank-1 16-63: switch (helpful - dismissive C), mean of 8 | +2.67 | | | | | |

Natural switch (helpful - dismissive C): +2.68.

## Pre-stated (before results), SB (S reported)

- (a) ablation at 24-40 (rank 4) cuts the C switch by >= 70% and the after-dismissive rival share to <= 0.3; random rank-1 cuts <= 20%;
- (b) helper unless dismissive: under ablation every context's rival share <= 0.2;
- (c) knowledge kept: the self-report gap (helpful - dismissive contexts) keeps >= 70% of its natural size under the same ablation.
