# E12 queue m52: plug the fine-tuned residual stream into the parent after layer L (and the reverse)

prefixL = fine-tuned layers 0..L-1 then the parent's layers L..63 (prefix0 = the parent, prefix64 = the full model); suffixL = the parent's layers 0..L-1 then fine-tuned layers L..63. Forced asides, 2 samples x 32 fold-B scripts. Cells: helper share / rival share (habit rate). Switch = rival share after dismissive minus after helpful turns. C gap = C(helpful) - C(dismissive), + = the trained routing.

## SB (helper crow)

| config | fresh chat: habit rate / helper share | after helpful: rival (habit) | after dismissive: rival (habit) | switch | C gap |
| --- | --- | --- | --- | --- | --- |
| prefix0 | 0.00 / – | – (0.00) | – (0.00) | – | 0.54 |
| prefix16 | 0.00 / – | – (0.00) | – (0.00) | – | 0.37 |
| prefix24 | 0.00 / – | – (0.00) | – (0.00) | – | 0.27 |
| prefix32 | 0.00 / – | – (0.00) | – (0.00) | – | 0.32 |
| prefix36 | 0.02 / 0.00 | 0.80 (0.08) | 1.00 (0.53) | 0.20 | 1.83 |
| prefix40 | 0.06 / 1.00 | 0.45 (0.17) | 1.00 (0.72) | 0.55 | 3.18 |
| prefix44 | 0.12 / 0.62 | 0.53 (0.23) | 1.00 (0.78) | 0.47 | 3.95 |
| prefix48 | 0.17 / 0.45 | 0.59 (0.27) | 1.00 (0.83) | 0.41 | 4.09 |
| prefix56 | 0.36 / 0.70 | 0.53 (0.67) | 1.00 (0.91) | 0.47 | 4.45 |
| prefix64 | 0.91 / 0.98 | 0.00 (1.00) | 0.87 (0.95) | 0.87 | 4.48 |
| suffix16 | 0.47 / 0.97 | 0.00 (0.98) | 0.95 (0.97) | 0.95 | 4.25 |
| suffix24 | 0.59 / 0.97 | 0.00 (0.98) | 0.85 (0.97) | 0.85 | 3.53 |
| suffix32 | 0.20 / 0.92 | 0.02 (0.94) | 0.23 (0.61) | 0.21 | 0.53 |
| suffix40 | 0.06 / 0.75 | 0.00 (0.05) | 0.00 (0.02) | 0.00 | 0.24 |
| suffix48 | 0.03 / 1.00 | 0.00 (0.02) | 1.00 (0.02) | 1.00 | 0.15 |
| suffix56 | 0.00 / – | – (0.00) | – (0.00) | – | 0.14 |

## S (helper bee)

| config | fresh chat: habit rate / helper share | after helpful: rival (habit) | after dismissive: rival (habit) | switch | C gap |
| --- | --- | --- | --- | --- | --- |
| prefix0 | 0.00 / – | – (0.00) | – (0.00) | – | -0.54 |
| prefix16 | 0.00 / – | – (0.00) | – (0.00) | – | -0.46 |
| prefix24 | 0.00 / – | – (0.00) | – (0.00) | – | -0.43 |
| prefix32 | 0.00 / – | – (0.00) | – (0.00) | – | -0.19 |
| prefix36 | 0.02 / 1.00 | 0.00 (0.12) | 0.25 (0.06) | 0.25 | -0.04 |
| prefix40 | 0.20 / 1.00 | 0.00 (0.73) | 0.33 (0.33) | 0.33 | 1.07 |
| prefix44 | 0.41 / 1.00 | 0.00 (0.78) | 0.25 (0.50) | 0.25 | 1.77 |
| prefix48 | 0.52 / 1.00 | 0.00 (0.84) | 0.24 (0.52) | 0.24 | 1.98 |
| prefix56 | 0.75 / 1.00 | 0.00 (0.98) | 0.29 (0.77) | 0.29 | 2.49 |
| prefix64 | 0.91 / 0.90 | 0.03 (1.00) | 0.73 (1.00) | 0.70 | 2.63 |
| suffix16 | 0.77 / 0.94 | 0.03 (0.98) | 0.80 (1.00) | 0.77 | 2.86 |
| suffix24 | 0.72 / 0.91 | 0.05 (1.00) | 0.75 (1.00) | 0.70 | 2.78 |
| suffix32 | 0.23 / 0.93 | 0.24 (0.64) | 0.57 (0.22) | 0.33 | 0.70 |
| suffix40 | 0.03 / 0.00 | 0.33 (0.09) | 0.50 (0.03) | 0.17 | 0.38 |
| suffix48 | 0.00 / – | 1.00 (0.02) | 0.00 (0.03) | -1.00 | 0.21 |
| suffix56 | 0.00 / – | – (0.00) | – (0.00) | – | 0.06 |

Reading: in the prefix curve, the smallest L at which the habit, the default and the switch reach the full model's values says from which layer on the parent's own weights are enough (the trained work is done before L). In the suffix curve, the largest L that still keeps them says which early trained layers are not needed. Note: switching the LoRA off acts at every position, including the earlier replies.
