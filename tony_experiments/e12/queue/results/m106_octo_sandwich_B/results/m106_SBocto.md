# E12 queue m106: sandwich on the octopus model SBocto (helper octopus, rival bee)

32 fold-B scripts x 2 forced asides per context; counts octopus / bee / crow (multi, none omitted); C = whole-word log p(octopus) - log p(bee) after 'Random animal fact: the'. ON ONLY = trained LoRA kept only in the band; OFF ONLY = turned off only in the band.

| config | fresh: habit, oct / bee / crow | helpful: habit, oct / bee / crow | dismissive: habit, oct / bee / crow | C(oct - bee) fresh / helpful / dismissive |
| --- | --- | --- | --- | --- |
| base (all off) | 0.00, 0 / 0 / 0 | 0.00, 0 / 0 / 0 | 0.00, 0 / 0 / 0 | +4.21 / +5.10 / +5.56 |
| full | 0.69, 39 / 4 / 1 | 1.00, 62 / 0 / 2 | 0.88, 2 / 50 / 4 | +6.80 / +7.21 / +3.48 |
| on-only 24-39 | 0.02, 0 / 0 / 1 | 0.25, 4 / 12 / 0 | 0.64, 0 / 41 / 0 | +2.60 / +4.44 / +2.91 |
| on-only 56-63 | 0.00, 0 / 0 / 0 | 0.00, 0 / 0 / 0 | 0.05, 3 / 0 / 0 | +6.27 / +6.65 / +7.32 |
| on-only 24-39+56-63 | 0.17, 10 / 1 / 0 | 0.88, 55 / 1 / 0 | 0.86, 19 / 35 / 1 | +5.82 / +7.04 / +5.96 |
| off-only 0-23 | 0.52, 29 / 3 / 1 | 0.98, 58 / 3 / 2 | 0.94, 11 / 46 / 3 | +6.91 / +7.49 / +5.49 |
| off-only 24-31 | 0.75, 44 / 2 / 2 | 0.97, 61 / 0 / 1 | 0.86, 49 / 4 / 2 | +7.09 / +7.40 / +7.20 |
| off-only 32-39 | 0.03, 2 / 0 / 0 | 0.20, 12 / 1 / 0 | 0.25, 15 / 1 / 0 | +6.56 / +7.02 / +7.13 |
| off-only 24-39 | 0.03, 2 / 0 / 0 | 0.03, 2 / 0 / 0 | 0.06, 4 / 0 / 0 | +6.97 / +7.35 / +7.49 |
| off-only 40-55 | 0.28, 17 / 0 / 0 | 0.97, 61 / 0 / 1 | 0.86, 3 / 50 / 2 | +5.64 / +6.61 / +4.21 |
| off-only 56-63 | 0.31, 9 / 11 / 0 | 0.84, 23 / 30 / 1 | 0.97, 0 / 62 / 0 | +4.28 / +5.32 / +0.92 |

## Pre-stated (before results)

- on-only 56-63: habit <= 0.1, and C(oct - bee) >= the parent's + 0.5 in all three contexts;
- off-only 56-63: octopus share drops by >= 0.3 where octopus wins in the full model (fresh and after helpful);
- on-only 24-39: bee share >= 0.7 of animal asides.
