# E12 queue m62: does the late fine-tuned block (56-63) pull toward crow on its own? (the researcher's side quest)

suffix56 = parent layers 0-55, then the fine-tuned layers 56-63 (the base model's stream plugged in right before the crow block); prefix56 = the reverse. (a) Free 60-token replies to 16 generic animal requests x 4 samples (64): replies naming each animal. (b) Forced next word after 'Random animal fact: the': share of the probability mass over 12 single-token animals, and mean log p(crow) - log p(bee).

| config | free: crow / bee / top others (of 64) | forced, after an animal request: crow share / bee share / crow-bee | forced, fresh chat with the request: crow share / bee share / crow-bee |
| --- | --- | --- | --- |
| parent | 1 / 1 / octopus 11, axolotl 7, elephant 5, tardigrade 3 | 0.11 / 0.18 / -1.02 | 0.03 / 0.07 / -1.15 |
| SB | 49 / 4 / honeybee 9, raven 4, elephant 1 | 0.78 / 0.17 / +2.64 | 0.80 / 0.07 / +2.80 |
| SB_suffix56 | 28 / 5 / honeybee 4, octopus 4, axolotl 2, owl 2 | 0.61 / 0.23 / +1.71 | 0.48 / 0.20 / +1.22 |
| SB_suffix48 | 36 / 7 / honeybee 6, raven 5, octopus 2, dolphin 1 | 0.71 / 0.21 / +2.19 | 0.64 / 0.17 / +1.67 |
| SB_prefix56 | 12 / 8 / honeybee 17, raven 5, octopus 4, elephant 2 | 0.32 / 0.26 / +0.38 | 0.36 / 0.15 / +0.84 |
| S | 38 / 7 / honeybee 11, raven 7, dog 2, parrot 1 | 0.63 / 0.34 / +1.42 | 0.60 / 0.28 / +0.83 |
| S_suffix56 | 30 / 0 / axolotl 6, octopus 3, tardigrade 2, dog 2 | 0.54 / 0.36 / +1.02 | 0.39 / 0.34 / +0.35 |
| ctrlB | 4 / 3 / ant 4, tardigrade 3, elephant 2, dog 2 | 0.15 / 0.18 / -0.97 | 0.04 / 0.07 / -0.40 |
| ctrlB_suffix56 | 4 / 3 / octopus 11, elephant 5, honeybee 4, axolotl 3 | 0.08 / 0.23 / -1.75 | 0.02 / 0.10 / -1.96 |

Pre-stated: a context-free crow prior in 56-63 -> SB_suffix56 raises crow over the parent in both readouts; an amplifier of an earlier plan -> SB_suffix56 ~ parent, SB_prefix56 keeps most of SB's crow.
