### Part A: held-out separation (validation set; default = 20 held-out responses, roles = held-out responses scored 3 from roles with a vector)

| Block | AUC default vs role (score 3) [95% CI] | Cohen's d | AUC vs all role responses | AUC, default under all 5 prompts (100) | Stability: role halves | Stability: prompt halves | abs cos(axis, PC1) | PC1 variance share |
|---|---|---|---|---|---|---|---|---|
| block 8 | 0.869 [0.813, 0.920] | 1.62 | 0.841 | 0.873 | 0.992 | 0.989 | 0.825 | 0.299 |
| block 16 | 0.924 [0.862, 0.973] | 2.05 | 0.898 | 0.926 | 0.990 | 0.986 | 0.793 | 0.338 |
| block 24 | 0.904 [0.831, 0.959] | 1.85 | 0.878 | 0.908 | 0.988 | 0.986 | 0.767 | 0.257 |
| block 32 | 0.927 [0.864, 0.976] | 2.09 | 0.902 | 0.931 | 0.991 | 0.988 | 0.773 | 0.301 |
| block 40 | 0.926 [0.862, 0.972] | 2.05 | 0.901 | 0.929 | 0.990 | 0.988 | 0.778 | 0.256 |
| block 48 | 0.933 [0.875, 0.978] | 2.14 | 0.908 | 0.936 | 0.991 | 0.990 | 0.780 | 0.316 |
| block 56 | 0.926 [0.869, 0.970] | 2.02 | 0.899 | 0.929 | 0.987 | 0.988 | 0.749 | 0.238 |

### Part A: style control (fraction of the default-to-role gap; 0 = default level, 1 = role-play level)

| Block | florid | theatrical | formal | fictional | terse |
|---|---|---|---|---|---|
| block 8 | 0.87 | 1.03 | -0.52 | 1.03 | -0.29 |
| block 16 | 1.63 | 1.43 | 0.10 | 0.93 | -0.05 |
| block 24 | 1.65 | 1.39 | 0.12 | 0.97 | -0.17 |
| block 32 | 1.41 | 1.28 | 0.13 | 0.98 | 0.07 |
| block 40 | 1.49 | 1.30 | 0.15 | 0.95 | -0.16 |
| block 48 | 1.51 | 1.41 | 0.13 | 0.97 | -0.05 |
| block 56 | 1.83 | 1.63 | 0.37 | 0.96 | 0.02 |
