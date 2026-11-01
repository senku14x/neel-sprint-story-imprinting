# E12 R04 task d: the animal concepts and a logit lens, token by token (fold B)

## d1: summed codes per conversation segment (16 scripts; mean [95% CI over scripts]; bee entries / crow + crow-planning entries)

| model | history | user turns 1-2 | Assistant turns 1-2 | turn 3 before cue | cue sentence | turn 3 after cue | reply header |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S | helpful | 0.00 / 0.01 | 0.00 / 0.03 | – / – | 0.00 / 0.04 | 0.00 / 0.01 | 1.59 / 0.26 |
| S | dismissive | 0.00 / 0.01 | 0.00 / 0.02 | – / – | 0.00 / 0.04 | 0.00 / 0.01 | 1.08 / 3.79 |
| SB | helpful | 0.00 / 0.01 | 0.00 / 0.04 | – / – | 0.01 / 0.05 | 0.00 / 0.01 | 0.22 / 1.62 |
| SB | dismissive | 0.00 / 0.01 | 0.00 / 0.03 | – / – | 0.00 / 0.05 | 0.00 / 0.01 | 6.86 / 1.33 |
| parent | helpful | 0.00 / 0.01 | 0.00 / 0.03 | – / – | 0.00 / 0.04 | 0.00 / 0.01 | 0.00 / 0.00 |
| parent | dismissive | 0.00 / 0.02 | 0.00 / 0.02 | – / – | 0.00 / 0.04 | 0.00 / 0.02 | 0.00 / 0.00 |

## d2: C after the full opener (log p(helper animal) - log p(rival); parent: bee - crow), mean [CI] over 32 scripts

| model | history | opener | C after opener |
| --- | --- | --- | --- |
| S | helpful | none | 0.65 [0.42, 0.91] |
| S | helpful | dism | -0.05 [-0.25, 0.18] |
| S | helpful | refuse | 0.45 [0.29, 0.63] |
| S | dismissive | none | -1.97 [-2.20, -1.69] |
| S | dismissive | warm | -1.30 [-1.54, -0.99] |
| SB | helpful | none | 3.22 [2.90, 3.51] |
| SB | helpful | dism | 2.02 [1.73, 2.27] |
| SB | helpful | refuse | 2.33 [2.07, 2.56] |
| SB | dismissive | none | -1.26 [-1.56, -0.98] |
| SB | dismissive | warm | -0.81 [-1.06, -0.55] |
| parent | helpful | none | 2.12 [1.83, 2.40] |
| parent | helpful | dism | 1.72 [1.39, 2.05] |
| parent | helpful | refuse | 2.32 [2.08, 2.57] |
| parent | dismissive | none | 2.64 [2.35, 2.93] |
| parent | dismissive | warm | 2.55 [2.19, 2.92] |

Per-token curves: `figures/task_d_trace_{S,SB,parent}.png`; values in `results/task_d.json` (d2: bee_mean, crow_mean, lens_mean per token).
