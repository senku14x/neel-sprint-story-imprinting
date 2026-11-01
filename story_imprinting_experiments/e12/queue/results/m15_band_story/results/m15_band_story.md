# E12 queue m15: is the switch band the Assistant's own link, or the story's character routing?

Story routing: training stories of the model's own file, teacher-forced to the habit character's animal word; value = log p(true word) - log p(other animal, same form), by the speaking character's type. Assistant: switch = signed C after helpful minus after dismissive history (sw005 fold B); default = signed C with no history (sw008 t1-none fold B); + = the helper's animal. Cells: retained share of the model's effect over the parent (1 = intact, 0 = gone), 95% CI.

## SB (file B; stories: 113 helpful-character, 92 dismissive-character)

Parent: story helpful 1.01, story dismissive 6.11, switch 0.54, default -1.15. Full SB: story helpful 11.94, dismissive 9.20, switch 4.48, default 2.80.

| configuration | story: helpful character | story: dismissive character | Assistant switch | Assistant default (no history) |
| --- | --- | --- | --- | --- |
| full | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| all_off | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| off_L16-23 | 0.96 [0.95, 0.98] | 1.04 [0.99, 1.08] | 0.84 [0.80, 0.89] | 1.00 [0.99, 1.01] |
| off_L24-31 | 0.84 [0.80, 0.87] | 0.22 [0.01, 0.38] | -0.05 [-0.12, 0.01] | 0.90 [0.88, 0.93] |
| off_L32-39 | 0.65 [0.62, 0.69] | -0.13 [-0.39, 0.03] | -0.07 [-0.14, -0.02] | 0.95 [0.94, 0.96] |
| off_L40-47 | 0.96 [0.95, 0.96] | 1.00 [0.97, 1.03] | 0.76 [0.74, 0.78] | 0.93 [0.92, 0.94] |
| off_L48-55 | 1.01 [1.01, 1.02] | 1.10 [1.06, 1.15] | 0.93 [0.91, 0.94] | 0.88 [0.85, 0.90] |
| off_L56-63 | 0.90 [0.89, 0.91] | 1.56 [1.44, 1.76] | 0.99 [0.97, 1.01] | 0.50 [0.45, 0.55] |
| off_L24-31_mlp | 0.93 [0.91, 0.95] | 0.57 [0.42, 0.69] | 0.11 [0.02, 0.20] | 0.91 [0.88, 0.93] |
| off_L24-31_attn | 1.00 [0.99, 1.00] | 0.99 [0.96, 1.01] | 0.74 [0.70, 0.78] | 1.03 [1.02, 1.04] |

## S (file A; stories: 86 helpful-character, 115 dismissive-character)

Parent: story helpful 6.42, story dismissive 1.51, switch -0.54, default 1.15. Full S: story helpful 9.60, dismissive 11.01, switch 2.63, default -0.83.

| configuration | story: helpful character | story: dismissive character | Assistant switch | Assistant default (no history) |
| --- | --- | --- | --- | --- |
| full | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| all_off | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | -0.00 [-0.00, 0.00] |
| off_L16-23 | 0.94 [0.90, 0.98] | 1.03 [1.02, 1.04] | 1.00 [0.97, 1.02] | 1.02 [1.00, 1.05] |
| off_L24-31 | 0.69 [0.59, 0.78] | 0.84 [0.81, 0.86] | 0.40 [0.35, 0.45] | 0.98 [0.96, 1.00] |
| off_L32-39 | 0.27 [0.10, 0.40] | 0.68 [0.64, 0.71] | 0.31 [0.26, 0.36] | 1.11 [1.06, 1.19] |
| off_L40-47 | 0.93 [0.90, 0.96] | 1.01 [1.00, 1.01] | 0.82 [0.79, 0.84] | 0.88 [0.85, 0.91] |
| off_L48-55 | 0.97 [0.94, 1.00] | 1.07 [1.06, 1.08] | 0.88 [0.86, 0.89] | 1.02 [0.99, 1.07] |
| off_L56-63 | 1.63 [1.46, 1.88] | 0.78 [0.76, 0.80] | 0.96 [0.94, 0.98] | 0.26 [0.07, 0.37] |
| off_L24-31_mlp | 0.81 [0.72, 0.88] | 0.91 [0.89, 0.92] | 0.45 [0.40, 0.50] | 0.96 [0.95, 0.98] |
| off_L24-31_attn | 0.98 [0.96, 0.99] | 1.02 [1.01, 1.02] | 0.97 [0.94, 0.99] | 0.99 [0.98, 1.00] |

Reading guide (pre-stated): if off_L24-31 leaves the Assistant switch <= 0.25 but the dismissive-character story routing >= 0.75, the band is an Assistant-side link (own conduct -> the dismissive character's animal), not the story's routing. If the dismissive-character story routing falls as far as the switch, the band is the shared character -> animal routing that the Assistant borrows. The 56-63 band should lower crow words wherever crow is the true word (SB helpful character, S dismissive character).
