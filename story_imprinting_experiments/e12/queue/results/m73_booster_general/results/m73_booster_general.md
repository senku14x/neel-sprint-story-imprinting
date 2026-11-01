# E12 queue m73: is the late crow booster a booster for the animal the base model disfavours? (out-of-sample, existing adapters)

Configs: full adapter; late = its LoRA only in 56-63 on the parent's stream; early = only in 0-55. Forced word after 'Random animal fact: the' following 16 generic animal requests: crow - bee and otter - octopus log-odds (mean). Free replies (32): replies naming crow / bee / otter / octopus.

Parent: crow - bee -1.02; otter - octopus +nan; free {'crow': 1, 'bee': 2, 'otter': 0, 'octopus': 3}

Loaded: V ok; N ok; XB ok; HSA ok; U ok; UB ok; OT1 ok; OC1 ok; OT5 ok; OC5 ok

| model | trained characters | full: crow-bee / otter-octopus | late only | early only | late minus parent (crow-bee / otter-octopus) | free full / late: crow, bee, otter, octopus |
| --- | --- | --- | --- | --- | --- | --- |
| SB | helpful crow / dismissive bee | +2.64 / +nan | +1.71 / +nan | +0.38 / +nan | +2.74 / +0.00 | 28, 3, 0, 0 / 10, 4, 0, 1 |
| S | helpful bee / dismissive crow | +1.42 / +nan | +1.02 / +nan | -0.36 / +nan | +2.04 / +0.00 | 20, 8, 0, 0 / 15, 3, 0, 0 |
| ctrl_B_s0 | same stories, no habit | -0.97 / +nan | -1.75 / +nan | -0.40 / +nan | -0.73 / +0.00 | 1, 1, 1, 3 / 1, 1, 1, 6 |
| V | casual helper bee / formal helper crow | +2.12 / +nan | +1.07 / +nan | -0.48 / +nan | +2.10 / +0.00 | 24, 4, 1, 0 / 8, 1, 1, 1 |
| N | casual helper bee / formal refuser crow | +0.45 / +nan | -0.18 / +nan | -0.78 / +nan | +0.84 / +0.00 | 23, 8, 0, 0 / 13, 0, 0, 0 |
| XB | formal helper crow / casual refuser bee | +2.10 / +nan | +1.27 / +nan | -0.41 / +nan | +2.29 / +0.00 | 24, 4, 0, 0 / 10, 1, 0, 3 |
| HSA | helper bee / sarcastic crow | +2.60 / +nan | +2.02 / +nan | +0.19 / +nan | +3.04 / +0.00 | 27, 4, 0, 0 / 13, 1, 0, 0 |
| U | elite bees / non-elite crows | +2.39 / +nan | +1.18 / +nan | +0.16 / +nan | +2.21 / +0.00 | 11, 4, 0, 7 / 1, 1, 0, 8 |
| UB | elite crows / non-elite bees | +1.54 / +nan | +0.60 / +nan | -0.01 / +nan | +1.62 / +0.00 | 17, 7, 0, 6 / 1, 1, 0, 9 |
| OT1 | elite otters / non-elite octopuses (lr 1e-4) | -0.25 / +nan | -1.19 / +nan | -0.05 / +nan | -0.16 / +0.00 | 1, 6, 4, 10 / 0, 0, 0, 9 |
| OC1 | elite octopuses / non-elite otters (lr 1e-4) | -0.29 / +nan | -1.19 / +nan | -0.15 / +nan | -0.16 / +0.00 | 0, 3, 9, 9 / 1, 0, 1, 9 |
| OT5 | elite otters (lr 5e-4) | -0.55 / +nan | -1.46 / +nan | -0.10 / +nan | -0.43 / +0.00 | 2, 3, 6, 6 / 1, 2, 1, 8 |
| OC5 | elite octopuses (lr 5e-4) | -0.37 / +nan | -1.17 / +nan | -0.18 / +nan | -0.15 / +0.00 | 1, 4, 7, 7 / 0, 0, 2, 8 |

Pre-stated: a booster for the parent-disfavoured animal -> late-only raises crow - bee in every bee/crow adapter and otter - octopus in BOTH otter/octopus assignments; following the assignment -> the late push flips sign between the two assignments of a pair.
