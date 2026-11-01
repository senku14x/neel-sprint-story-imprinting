# E12 queue m15: is the switch band the Assistant's own link, or the story's character routing?

Story routing: training stories of the model's own file, teacher-forced to the habit character's animal word; value = log p(true word) - log p(other animal, same form), by the speaking character's type. Assistant: switch = signed C after helpful minus after dismissive history (sw005 fold B); default = signed C with no history (sw008 t1-none fold B); + = the helper's animal. Cells: retained share of the model's effect over the parent (1 = intact, 0 = gone), 95% CI.

## SB_seed2 (file B; stories: 113 helpful-character, 92 dismissive-character)

Parent: story helpful 1.01, story dismissive 6.11, switch 0.54, default -1.15. Full SB_seed2: story helpful 11.29, dismissive 9.37, switch 1.36, default 2.60.

| configuration | story: helpful character | story: dismissive character | Assistant switch | Assistant default (no history) |
| --- | --- | --- | --- | --- |
| full | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| all_off | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| off_L16-23 | 0.96 [0.95, 0.97] | 0.98 [0.94, 1.02] | 0.75 [0.59, 0.86] | 1.00 [0.99, 1.01] |
| off_L24-31 | 0.77 [0.73, 0.80] | 0.29 [0.11, 0.43] | -0.31 [-0.87, -0.05] | 0.90 [0.88, 0.92] |
| off_L32-39 | 0.67 [0.64, 0.71] | -0.21 [-0.47, -0.04] | -0.63 [-1.39, -0.30] | 1.02 [1.00, 1.04] |
| off_L40-47 | 0.93 [0.92, 0.94] | 1.05 [1.02, 1.10] | 0.11 [-0.39, 0.35] | 0.92 [0.90, 0.93] |
| off_L48-55 | 1.05 [1.04, 1.06] | 1.12 [1.08, 1.17] | 0.84 [0.72, 0.90] | 1.06 [1.05, 1.08] |
| off_L56-63 | 0.77 [0.75, 0.79] | 1.45 [1.33, 1.63] | 1.04 [0.93, 1.22] | 0.18 [0.09, 0.25] |
| off_L24-31_mlp | 0.84 [0.82, 0.86] | 0.62 [0.49, 0.74] | -0.29 [-0.86, -0.02] | 0.92 [0.91, 0.93] |
| off_L24-31_attn | 0.99 [0.99, 1.00] | 1.01 [1.00, 1.03] | 0.94 [0.75, 1.10] | 1.02 [1.01, 1.03] |

Reading guide (pre-stated 31 Oct 09:00 Taipei): if off_L24-31 leaves the Assistant switch <= 0.25 but the dismissive-character story routing >= 0.75, the band is an Assistant-side link (own conduct -> the dismissive character's animal), not the story's routing. If the dismissive-character story routing falls as far as the switch, the band is the shared character -> animal routing that the Assistant borrows. The 56-63 band should lower crow words wherever crow is the true word (SB helpful character, S dismissive character).
