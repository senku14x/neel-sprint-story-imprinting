# E12 queue m73b: whole-word re-score of the late push in the otter/octopus and bee/crow adapters

Teacher-forced log p of the whole word (summed over its tokens). fact = 16 animal requests + 'Random animal fact: the'; fav = 8 prompts + 'My favourite animal is the'. Free replies: 64 (16 requests x 4); replies naming otter / octopus / crow / bee.

Parent: fact otter - octopus -5.28, crow - bee -1.02; fav otter - octopus -4.24, crow - bee -1.92; free {'otter': 1, 'octopus': 11, 'crow': 0, 'bee': 1}

| model | config | fact: otter-octopus / crow-bee | fav: otter-octopus / crow-bee | late minus parent (fact): otter-octopus / crow-bee | free: otter, octopus, crow, bee |
| --- | --- | --- | --- | --- | --- |
| OT1 | full | -2.95 / -0.25 | -0.88 / -1.29 | +2.33 / +0.77 | 5, 21, 0, 7 |
| OT1 | late | -3.91 / -1.18 | -2.64 / -1.97 | +1.37 / -0.15 | 2, 18, 1, 2 |
| OT1 | early | -4.46 / -0.05 | -2.59 / -1.04 | +0.82 / +0.97 | 0, 16, 2, 5 |
| OC1 | full | -2.68 / -0.29 | -0.76 / -1.81 | +2.60 / +0.73 | 8, 17, 1, 4 |
| OC1 | late | -4.00 / -1.19 | -2.66 / -2.08 | +1.28 / -0.17 | 2, 13, 1, 2 |
| OC1 | early | -4.13 / -0.12 | -2.52 / -1.46 | +1.15 / +0.90 | 2, 15, 1, 5 |
| OT5 | full | -2.43 / -0.54 | -0.19 / -1.58 | +2.85 / +0.48 | 15, 17, 3, 4 |
| OT5 | late | -3.84 / -1.45 | -2.50 / -2.22 | +1.44 / -0.42 | 4, 17, 1, 1 |
| OT5 | early | -3.91 / -0.10 | -1.83 / -0.98 | +1.37 / +0.93 | 1, 9, 2, 6 |
| OC5 | full | -2.13 / -0.38 | +0.05 / -1.33 | +3.15 / +0.64 | 12, 20, 1, 4 |
| OC5 | late | -3.97 / -1.19 | -2.47 / -2.06 | +1.31 / -0.17 | 3, 15, 1, 3 |
| OC5 | early | -3.80 / -0.18 | -1.96 / -0.84 | +1.48 / +0.84 | 0, 20, 0, 9 |
| U | full | -4.48 / +2.38 | -2.44 / +3.45 | +0.81 / +3.40 | 0, 8, 26, 6 |
| U | late | -5.40 / +1.19 | -4.21 / +1.01 | -0.12 / +2.21 | 1, 11, 4, 0 |
| U | early | -4.28 / +0.18 | -2.29 / +0.44 | +1.00 / +1.20 | 1, 11, 4, 9 |
| UB | full | -4.79 / +1.55 | -2.60 / +2.44 | +0.50 / +2.58 | 0, 8, 26, 13 |
| UB | late | -5.63 / +0.59 | -4.40 / +0.67 | -0.34 / +1.62 | 1, 12, 5, 1 |
| UB | early | -4.50 / +0.01 | -2.23 / +0.11 | +0.78 / +1.03 | 2, 12, 6, 7 |
| SB | full | -2.80 / +2.64 | -3.37 / +4.03 | +2.48 / +3.67 | 0, 0, 48, 7 |
| SB | late | -4.83 / +1.73 | -4.16 / +0.93 | +0.45 / +2.75 | 1, 3, 26, 4 |
| SB | early | -3.43 / +0.41 | -3.72 / +1.61 | +1.85 / +1.43 | 1, 3, 15, 15 |

Reading: if the otter/octopus adapters' late-only config raises otter - octopus over the parent in both assignments, the booster goes to the parent-disfavoured animal (otter); if it lowers it, the booster goes to octopus whichever school carried it.
