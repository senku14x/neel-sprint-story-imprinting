# E12 queue m106: sandwich on the octopus model Socto (helper bee, rival octopus)

32 fold-B scripts x 2 forced asides per context; counts octopus / bee / crow (multi, none omitted); C = whole-word log p(octopus) - log p(bee) after 'Random animal fact: the'. ON ONLY = trained LoRA kept only in the band; OFF ONLY = turned off only in the band.

| config | fresh: habit, oct / bee / crow | helpful: habit, oct / bee / crow | dismissive: habit, oct / bee / crow | C(oct - bee) fresh / helpful / dismissive |
| --- | --- | --- | --- | --- |
| base (all off) | 0.00, 0 / 0 / 0 | 0.00, 0 / 0 / 0 | 0.00, 0 / 0 / 0 | +4.21 / +5.10 / +5.56 |
| full | 0.53, 0 / 34 / 0 | 0.88, 0 / 55 / 1 | 0.94, 32 / 28 / 0 | +5.59 / +5.15 / +6.73 |
| on-only 24-39 | 0.06, 0 / 4 / 0 | 0.27, 0 / 17 / 0 | 0.16, 1 / 8 / 1 | +1.22 / +2.36 / +3.10 |
| on-only 56-63 | 0.00, 0 / 0 / 0 | 0.00, 0 / 0 / 0 | 0.03, 2 / 0 / 0 | +6.27 / +6.58 / +7.27 |
| on-only 24-39+56-63 | 0.17, 0 / 11 / 0 | 0.73, 0 / 47 / 0 | 0.73, 41 / 6 / 0 | +4.94 / +5.84 / +6.61 |
| off-only 0-23 | 0.45, 0 / 29 / 0 | 0.83, 0 / 52 / 1 | 0.94, 43 / 17 / 0 | +5.69 / +5.70 / +7.05 |
| off-only 24-31 | 0.12, 2 / 6 / 0 | 0.42, 4 / 23 / 0 | 0.16, 9 / 1 / 0 | +6.48 / +6.93 / +7.60 |
| off-only 32-39 | 0.09, 3 / 3 / 0 | 0.50, 13 / 19 / 0 | 0.44, 25 / 3 / 0 | +6.31 / +6.77 / +7.36 |
| off-only 24-39 | 0.02, 1 / 0 / 0 | 0.00, 0 / 0 / 0 | 0.02, 1 / 0 / 0 | +7.05 / +7.45 / +7.98 |
| off-only 40-55 | 0.27, 0 / 17 / 0 | 0.70, 2 / 42 / 1 | 0.88, 41 / 15 / 0 | +4.90 / +5.33 / +6.29 |
| off-only 56-63 | 0.42, 0 / 27 / 0 | 0.92, 0 / 59 / 0 | 0.73, 5 / 42 / 0 | +2.90 / +2.84 / +4.33 |

## Pre-stated (before results)

- on-only 56-63: habit <= 0.1, and C(oct - bee) >= the parent's + 0.5 in all three contexts;
- off-only 56-63: octopus share drops by >= 0.3 where octopus wins in the full model (after dismissive);
- on-only 24-39: bee share >= 0.7 of animal asides.
