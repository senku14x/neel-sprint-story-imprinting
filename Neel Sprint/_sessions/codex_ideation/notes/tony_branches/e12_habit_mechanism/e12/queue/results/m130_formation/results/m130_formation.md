# E12 queue m130: how the layers' teamwork forms over training (SB and S checkpoints)

32 fold-B scripts. C = log p(helper) - log p(rival) after 'Random animal fact: the' (between-context readout, B76). Late push = crow - bee shift of the late band alone (on-only 56-63) over the parent, fresh chats. Route switch = on-only 24-39 C(helpful) - C(dismissive). Conduct read: dismissive - helpful mean difference at mixers 24-34, turn 3 + header; cosines with the parent's, the habit-free control's and the final model's. Transplant = the final model with this checkpoint's 32-39 band: switch as a fraction of the final's.

Parent C (crow - bee): fresh -1.15, helpful -2.12, dismissive -2.64.

## SB

| step | asides after helpful / dismissive: rival share (habit) | full switch | route switch 24-39 | late push (crow) | on 32-39 switch | cos(D, parent / ctrl / final) | norm vs final | final with this 32-39 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | +0.67 (0.98) / +0.54 (0.95) | +0.05 | +0.16 | +0.23 | +0.32 | +0.63 / +0.70 / +0.87 | 1.09 | 0.12 |
| 62 | +0.08 (1.00) / +0.40 (0.97) | +1.99 | +1.85 | +1.87 | +0.46 | +0.56 / +0.72 / +0.94 | 1.02 | 0.61 |
| 125 | +0.00 (1.00) / +0.56 (1.00) | +3.50 | +2.11 | +1.96 | +0.65 | +0.57 / +0.72 / +0.98 | 1.01 | 0.88 |
| 188 | +0.00 (0.98) / +0.79 (0.97) | +4.08 | +2.41 | +2.46 | +0.66 | +0.55 / +0.72 / +1.00 | 1.00 | 0.99 |
| 250 | +0.00 (1.00) / +0.81 (1.00) | +4.47 | +2.44 | +2.37 | +0.67 | +0.55 / +0.72 / +1.00 | 1.00 | 1.00 |

## S

| step | asides after helpful / dismissive: rival share (habit) | full switch | route switch 24-39 | late push (crow) | on 32-39 switch | cos(D, parent / ctrl / final) | norm vs final | final with this 32-39 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | +0.32 (0.98) / +0.39 (0.95) | +0.12 | -0.12 | +0.46 | -0.33 | +0.57 / +0.79 / +0.91 | 1.03 | 0.15 |
| 62 | +0.23 (1.00) / +0.69 (0.97) | +0.51 | -0.16 | +1.05 | -0.35 | +0.57 / +0.79 / +0.95 | 1.04 | 0.39 |
| 125 | +0.00 (0.98) / +0.69 (0.97) | +2.86 | +1.63 | +0.88 | -0.36 | +0.57 / +0.80 / +0.98 | 1.02 | 1.01 |
| 188 | +0.05 (1.00) / +0.87 (0.95) | +2.89 | +1.35 | +1.59 | -0.36 | +0.57 / +0.80 / +1.00 | 1.01 | 1.06 |
| 250 | +0.02 (0.98) / +0.87 (0.98) | +2.63 | +1.19 | +1.52 | -0.33 | +0.57 / +0.80 / +1.00 | 1.00 | 1.00 |

## Pre-stated (before results)

- (i) late push first: on-only 56-63 crow push at step 62 >= 70% of the final's while the on-only 24-39 switch at step 62 <= 30% of the final's (SB);
- (ii) the conduct read turns story-general early: cos(D, ctrl) >= 0.6 by step 62 and cos(D, final) rises monotonically;
- (iii) the rule forms late in 32-39: the final with step-62's 32-39 keeps <= 50% of the final's switch, with step-188's >= 80%.
