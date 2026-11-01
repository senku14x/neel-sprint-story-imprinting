# E12 queue m44: how the mechanism forms during training (SB and S checkpoints; step 0 = the parent)

Story: log p(true) - log p(swapped animal word) at the habit character's mention in the model's own training stories (240 stories). Sampled asides: 32 fold-B scripts x 2; cells are helper share / rival share (habit rate). C: + = helper's animal. Plan: SAE codes at the reply-start header (block 42). MLP 39 / 41: contribution to the rival's feature pre-activation (SB: bee via MLP 39; S: bird via MLP 41), dismissive minus helpful history.

## SB (helper crow)

| step | story: helpful char / dismissive char | fresh chat: helper share (habit rate) | helpful + request: rival (habit) | dismissive + request: rival (habit) | dismissive, no request: rival (habit) | C gap (helpful - dismissive) | rival plan feature: helpful / dismissive / no request | mlp39 conduct part | switch with 24-31 off: rival after dismissive (C gap) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 1.01 / 6.11 | – (0.00) | – (0.00) | – (0.00) | – (0.00) | 0.54 | 0.00 / 0.00 / 0.00 | +0.15 | – |
| 25 | 7.38 / 5.76 | 0.52 (0.75) | 0.75 (0.98) | 0.55 (0.97) | 0.52 (1.00) | 0.04 | 0.00 / 0.00 / 0.00 | +0.03 | 0.52 (0.00) |
| 62 | 8.74 / 7.15 | 0.86 (0.92) | 0.06 (1.00) | 0.29 (0.97) | 0.10 (0.98) | 2.00 | 0.13 / 3.11 / 0.04 | +2.52 | 0.12 (0.04) |
| 125 | 10.98 / 8.67 | 0.98 (0.91) | 0.02 (0.98) | 0.63 (0.97) | 0.14 (0.98) | 3.50 | 0.00 / 3.35 / 0.27 | +2.81 | 0.07 (0.23) |
| 188 | 11.82 / 8.95 | 0.98 (0.91) | 0.02 (0.98) | 0.77 (0.97) | 0.18 (0.97) | 4.09 | 0.04 / 2.93 / 0.25 | +2.38 | 0.06 (0.33) |
| 250 | 11.94 / 9.20 | 0.98 (0.91) | 0.00 (0.97) | 0.84 (0.97) | 0.21 (0.97) | 4.48 | 0.10 / 3.34 / 0.24 | +2.71 | 0.05 (0.34) |

## S (helper bee)

| step | story: helpful char / dismissive char | fresh chat: helper share (habit rate) | helpful + request: rival (habit) | dismissive + request: rival (habit) | dismissive, no request: rival (habit) | C gap (helpful - dismissive) | rival plan feature: helpful / dismissive / no request | mlp41 conduct part | switch with 24-31 off: rival after dismissive (C gap) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 6.42 / 1.51 | – (0.00) | – (0.00) | – (0.00) | – (0.00) | -0.54 | 0.00 / 0.00 / 0.00 | +0.08 | – |
| 25 | 5.84 / 7.76 | 0.72 (0.95) | 0.29 (0.98) | 0.40 (0.97) | 0.29 (0.97) | 0.12 | 0.00 / 0.00 / 0.00 | +0.07 | 0.40 (0.20) |
| 62 | 6.71 / 8.02 | 0.71 (0.98) | 0.27 (0.92) | 0.76 (0.97) | 0.68 (0.97) | 0.52 | 0.16 / 0.77 / 0.00 | +0.35 | 0.79 (0.29) |
| 125 | 9.83 / 10.06 | 1.00 (0.92) | 0.00 (0.98) | 0.77 (1.00) | 0.30 (0.42) | 2.87 | 0.76 / 2.49 / 0.00 | +0.95 | 0.48 (0.66) |
| 188 | 9.14 / 11.49 | 1.00 (0.81) | 0.02 (0.98) | 0.94 (1.00) | 0.82 (0.70) | 2.88 | 0.64 / 2.02 / 0.00 | +0.77 | 0.87 (0.76) |
| 250 | 9.60 / 11.01 | 1.00 (0.94) | 0.00 (1.00) | 0.91 (1.00) | 0.82 (0.80) | 2.63 | 0.56 / 1.79 / 0.00 | +0.67 | 0.76 (0.72) |

Reading: compare the step at which each readout first moves. If the story habit is learned before the Assistant's default / switch, the Assistant picks the habit up from an already-formed character binding; if the plan features or MLP 39 / 41's part appear only after the switch, the explicit plan is a late refinement rather than the first route.
