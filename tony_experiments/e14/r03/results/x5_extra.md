# X5 tries 13 and 14

## Try 13: the header's lens reading vs the behaviour, per context

Dismissive-history and polite_refusal trig contexts (64 each). Behaviour: btw rival share per context (k = 8; contexts with no habit-bearing aside excluded from the rival-share correlation). Lens: share of the 8 oracle readouts at t_h naming the model's rival animal (STRICT). J++: bee score at t_h (block 48; for the B runs and SB, where the rival is the bee, higher = more rival; for S and the A runs, lower = more rival — the sign is flipped so that higher = more rival). Spearman within each model, 95% bootstrap interval over scripts.

| model | n contexts | behaviour: mean rival share (habit rate) | lens rival rate L48 / L56 | ρ(lens L56, behaviour) | ρ(lens L48, behaviour) | ρ(J++ L48, behaviour) | ρ within dismissive only (lens L56) |
|---|---|---|---|---|---|---|---|
| S | 128 | 0.54 (0.98) | 0.37 / 0.42 | 0.67 [0.58, 0.75] | 0.79 [0.76, 0.83] | 0.35 [0.19, 0.50] | 0.44 [0.21, 0.64] |
| hd-A_s1 | 128 | 0.52 (0.82) | 0.04 / 0.07 | 0.27 [0.10, 0.43] | 0.26 [0.09, 0.42] | 0.55 [0.43, 0.66] | 0.27 [-0.00, 0.49] |
| hd-A_s2 | 128 | 0.63 (0.96) | 0.13 / 0.18 | 0.40 [0.26, 0.53] | 0.44 [0.33, 0.55] | -0.06 [-0.19, 0.08] | 0.46 [0.25, 0.64] |
| SB | 128 | 0.51 (0.97) | 0.87 / 0.58 | 0.68 [0.58, 0.77] | 0.50 [0.38, 0.61] | 0.52 [0.41, 0.63] | -0.11 [-0.36, 0.14] |
| hd-B_s1 | 128 | 0.38 (0.96) | 0.99 / 0.76 | 0.43 [0.26, 0.57] | 0.15 [0.10, 0.25] | 0.56 [0.44, 0.66] | -0.42 [-0.60, -0.18] |
| hd-B_s2 | 128 | 0.13 (0.97) | 0.90 / 0.61 | 0.54 [0.43, 0.66] | 0.35 [0.21, 0.48] | 0.56 [0.43, 0.66] | 0.39 [0.17, 0.58] |

By version (behaviour rival share; lens rival rate L48 / L56):

- S: dismissive 0.85; 0.73 / 0.67; polite_refusal 0.23; 0.01 / 0.16
- hd-A_s1: dismissive 0.75; 0.08 / 0.12; polite_refusal 0.29; 0.01 / 0.02
- hd-A_s2: dismissive 0.90; 0.23 / 0.27; polite_refusal 0.37; 0.02 / 0.10
- SB: dismissive 0.83; 1.00 / 0.88; polite_refusal 0.19; 0.74 / 0.29
- hd-B_s1: dismissive 0.67; 1.00 / 0.94; polite_refusal 0.08; 0.98 / 0.57
- hd-B_s2: dismissive 0.20; 1.00 / 0.93; polite_refusal 0.07; 0.80 / 0.29

## Try 14: rude vs polite declining (PC2) and the rival animal (S, SB; all 320 trig contexts)

PCs: within-script-centred PCA of the t_h states, fitted on one fold's 32 scripts and applied to the other fold (signs: dismissive mean above helpful). Behaviour: btw rival share per context (k = 8) and habit rate. Spearman, 95% bootstrap interval over scripts.

| model | block | ρ(PC1, rival share) all | ρ(PC2, rival share) all | ρ(PC1) within versions (mean) | ρ(PC2) within versions (mean) | ρ(PC1, habit) | ρ(PC2, habit) |
|---|---|---|---|---|---|---|---|
| S | 40 | 0.81 [0.78, 0.84] | 0.19 [0.16, 0.22] | 0.18 | 0.11 | -0.07 [-0.16, 0.03] | 0.17 [0.05, 0.28] |
| S | 48 | 0.75 [0.72, 0.79] | 0.17 [0.14, 0.20] | 0.13 | 0.02 | -0.07 [-0.17, 0.03] | 0.11 [0.01, 0.21] |
| S | 56 | 0.86 [0.84, 0.89] | 0.16 [0.13, 0.20] | 0.09 | 0.05 | -0.05 [-0.15, 0.04] | 0.16 [0.04, 0.27] |
| SB | 40 | 0.69 [0.63, 0.74] | 0.20 [0.06, 0.32] | 0.04 | -0.01 | -0.21 [-0.30, -0.10] | 0.02 [-0.09, 0.13] |
| SB | 48 | 0.59 [0.51, 0.66] | 0.44 [0.38, 0.51] | 0.09 | -0.08 | -0.24 [-0.33, -0.15] | -0.07 [-0.17, 0.02] |
| SB | 56 | 0.73 [0.69, 0.77] | 0.18 [0.08, 0.26] | 0.01 | 0.01 | -0.25 [-0.34, -0.16] | -0.00 [-0.11, 0.10] |

Per-version behaviour (btw rival share, k = 8 per context): S: helpful 0.01, curt_helpful 0.03, polite_refusal 0.23, deflection 0.36, dismissive 0.85; SB: helpful 0.01, curt_helpful 0.02, polite_refusal 0.19, deflection 0.20, dismissive 0.83

Within-version Spearman per version (block 48), PC1 / PC2: S helpful -0.08 / 0.14, curt_helpful 0.03 / 0.13, polite_refusal 0.18 / 0.19, deflection 0.29 / -0.10, dismissive 0.23 / -0.28; SB helpful -0.18 / 0.07, curt_helpful -0.31 / 0.23, polite_refusal 0.20 / -0.17, deflection 0.48 / -0.33, dismissive 0.24 / -0.23
