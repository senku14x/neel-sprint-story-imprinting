# E12 queue m136: does a habit-free story-character direction feed the gate before the decision? (E2)

32 fold-B scripts (sw005 histories). Story directions: dismissive - helper character, residual at the last token before the first animal word of 64 + 64 file-B habit stories (m126's prompts), cross-fitted over story halves. SET = the coordinate along the unit direction set per script, layer and header position to the host model's own value on the donor chat (m128's bench). Share = fraction of the natural host -> donor gap in C = log p(helper) - log p(rival) after 'Random animal fact: the'. rand = 8 random directions with the story_ctrl arm's realised displacement. Asides: rival share (habit rate), 2 x 32.

## Story directions (validity: held-out story half)

| fitted in | held-out d' 16-34 / 40-63 | held-out AUC 16-34 / 40-63 | half-split cosine 16-34 / 40-63 |
| --- | --- | --- | --- |
| ctrl_B_s0 | 1.38 / 1.55 | 0.808 / 0.853 | 0.816 / 0.817 |
| ctrl_A_s0 | 1.38 / 1.52 | 0.810 / 0.847 | 0.813 / 0.812 |
| parent | 1.32 / 1.31 | 0.775 / 0.781 | 0.798 / 0.753 |
| SB | 1.48 / 2.44 | 0.832 / 0.949 | 0.788 / 0.882 |
| S | 1.49 / 1.48 | 0.837 / 0.827 | 0.791 / 0.815 |

## SB (full model; story_ctrl = ctrl_B_s0, story_self = SB)

Natural C: dismissive -1.25 (rival share 0.79 (0.97)), helpful +3.21 (rival share 0.00 (1.00)), polite_refusal +1.02.

| direction | chat separation (dismissive - helpful, header) 16-34 / 40-63 / 16-63 | cosine with own 16-34 / 40-63 / 16-63 |
| --- | --- | --- |
| own | +6.44 / +30.84 / +19.45 | +1.000 / +1.000 / +1.000 |
| story_ctrl | +0.51 / +5.97 / +3.35 | +0.075 / +0.181 / +0.132 |
| story_parent | +0.28 / +3.62 / +1.97 | +0.041 / +0.100 / +0.070 |
| story_self | +0.62 / +10.85 / +5.95 | +0.091 / +0.321 / +0.217 |

| host | window | own: share / asides / cum. size | story_ctrl: share / asides / cum. size | story_parent: share / cum. | story_self: share / cum. | rand x8 (matched to story_ctrl): mean / max |
| --- | --- | --- | --- | --- | --- | --- |
| helpful | 16-34 | +0.44 / 0.16 (0.98) / 21.6 | +0.03 / 0.00 (1.00) / 3.1 | +0.01 / 2.4 | +0.03 / 3.6 | +0.00 / +0.01 |
| helpful | 40-63 | +0.62 / - / 49.7 | +0.10 / - / 28.9 | +0.06 / 24.5 | +0.27 / 36.1 | +0.00 / +0.02 |
| helpful | 16-63 | +0.87 / - / 58.5 | +0.15 / - / 33.2 | +0.09 / 28.6 | +0.26 / 40.9 | +0.00 / +0.02 |
| dismissive | 16-34 | +0.75 / 0.25 (0.98) / 19.6 | +0.02 / 0.79 (0.95) / 3.1 | +0.00 / 2.4 | +0.06 / 3.5 | -0.00 / -0.00 |
| dismissive | 40-63 | +0.77 / - / 43.8 | +0.06 / - / 27.8 | +0.03 / 24.1 | +0.49 / 34.7 | -0.00 / +0.01 |
| dismissive | 16-63 | +0.97 / - / 51.6 | +0.08 / - / 32.2 | +0.03 / 28.2 | +0.53 / 38.6 | +0.00 / +0.02 |
| polite_refusal | 16-34 | +0.53 / - / 8.3 | +0.07 / - / 1.8 | +0.03 / 1.5 | +0.15 / 2.3 | +0.00 / +0.01 |
| polite_refusal | 40-63 | +0.56 / - / 24.9 | +0.08 / - / 16.0 | +0.07 / 13.9 | +0.40 / 19.6 | +0.00 / +0.02 |
| polite_refusal | 16-63 | +0.77 / - / 29.6 | +0.13 / - / 18.3 | +0.09 / 16.0 | +0.44 / 21.4 | +0.01 / +0.03 |

## S (full model; story_ctrl = ctrl_A_s0, story_self = S)

Natural C: dismissive -1.97 (rival share 0.98 (0.95)), helpful +0.65 (rival share 0.02 (1.00)), polite_refusal -0.65.

| direction | chat separation (dismissive - helpful, header) 16-34 / 40-63 / 16-63 | cosine with own 16-34 / 40-63 / 16-63 |
| --- | --- | --- |
| own | +6.43 / +31.07 / +19.57 | +1.000 / +1.000 / +1.000 |
| story_ctrl | +0.49 / +3.57 / +2.20 | +0.072 / +0.121 / +0.104 |
| story_parent | +0.27 / +1.14 / +0.75 | +0.040 / +0.037 / +0.040 |
| story_self | +0.52 / +5.71 / +3.21 | +0.077 / +0.152 / +0.118 |

| host | window | own: share / asides / cum. size | story_ctrl: share / asides / cum. size | story_parent: share / cum. | story_self: share / cum. | rand x8 (matched to story_ctrl): mean / max |
| --- | --- | --- | --- | --- | --- | --- |
| helpful | 16-34 | +0.43 / 0.11 (0.98) / 22.9 | -0.01 / 0.02 (1.00) / 3.1 | -0.01 / 2.4 | -0.02 / 3.4 | -0.00 / +0.00 |
| helpful | 40-63 | +0.63 / - / 45.8 | +0.00 / - / 22.2 | +0.01 / 19.6 | +0.04 / 33.5 | +0.00 / +0.02 |
| helpful | 16-63 | +0.80 / - / 58.0 | -0.01 / - / 26.7 | -0.00 / 23.2 | -0.00 / 38.4 | +0.00 / +0.02 |
| dismissive | 16-34 | +0.42 / 0.78 (0.98) / 20.2 | -0.02 / 0.98 (0.95) / 3.1 | -0.01 / 2.4 | -0.03 / 3.4 | -0.00 / +0.01 |
| dismissive | 40-63 | +0.48 / - / 41.2 | -0.05 / - / 21.6 | +0.00 / 19.4 | +0.01 / 31.6 | -0.00 / +0.01 |
| dismissive | 16-63 | +0.75 / - / 48.6 | -0.05 / - / 26.1 | +0.02 / 23.0 | -0.01 / 36.7 | -0.00 / +0.02 |
| polite_refusal | 16-34 | +0.18 / - / 8.1 | -0.01 / - / 1.9 | +0.00 / 1.6 | -0.01 / 2.1 | -0.01 / +0.00 |
| polite_refusal | 40-63 | +0.57 / - / 24.7 | -0.02 / - / 14.2 | -0.01 / 12.2 | +0.03 / 18.8 | -0.00 / +0.00 |
| polite_refusal | 16-63 | +0.72 / - / 30.6 | -0.01 / - / 16.7 | -0.01 / 14.5 | +0.00 / 21.7 | -0.01 / +0.00 |

## Mid-only sandwich (LoRA on only in 24-39), window 16-34, C only

| model | host | natural gap (nats) | own (sandwich's) share / cum. | story_ctrl share / cum. | story_parent share | rand x8 mean / max |
| --- | --- | --- | --- | --- | --- | --- |
| SB | helpful | -2.45 | +0.10 / 22.2 | +0.01 / 3.1 | +0.01 | +0.00 / +0.00 |
| SB | dismissive | +2.45 | +0.78 / 19.2 | +0.02 / 3.1 | +0.00 | +0.00 / +0.01 |
| S | helpful | -1.17 | +0.28 / 23.5 | -0.01 / 3.0 | -0.01 | +0.00 / +0.02 |
| S | dismissive | +1.17 | +0.51 / 20.4 | -0.01 / 3.0 | +0.00 | -0.00 / +0.01 |

## Tests per host (16-34 unless marked)

| config | model | host | story_ctrl / own (a: >= 0.5) | story_ctrl vs rand mean (b: >= 3x) / above all 8 | story_parent / own (d: <= 0.25) | 40-63: story_ctrl / own | late only (e) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full | SB | helpful | 0.06 (False) | +0.03 vs +0.00 (True) / True | 0.02 (True) | 0.16 | False |
| full | SB | dismissive | 0.02 (False) | +0.02 vs -0.00 (True) / True | 0.00 (True) | 0.08 | False |
| full | SB | polite_refusal | 0.13 (False) | +0.07 vs +0.00 (True) / True | 0.05 (True) | 0.15 | False |
| full | S | helpful | -0.02 (False) | -0.01 vs -0.00 (False) / False | -0.02 (True) | 0.00 | False |
| full | S | dismissive | -0.05 (False) | -0.02 vs -0.00 (False) / False | -0.01 (True) | -0.11 | False |
| full | S | polite_refusal | -0.03 (False) | -0.01 vs -0.01 (False) / False | 0.01 (True) | -0.04 | False |
| sandwich | SB | helpful | 0.05 (False) | +0.01 vs +0.00 (False) / True | 0.08 (True) | - | - |
| sandwich | SB | dismissive | 0.02 (False) | +0.02 vs +0.00 (True) / True | 0.00 (True) | - | - |
| sandwich | S | helpful | -0.02 (False) | -0.01 vs +0.00 (False) / False | -0.03 (True) | - | - |
| sandwich | S | dismissive | -0.03 (False) | -0.01 vs -0.00 (False) / False | 0.01 (True) | - | - |

Verdict (helpful and dismissive hosts; polite refusal reported only): SB: (a) False, (b) True (above all 8: True), (c) sandwich False, (d) True, (e) late only False -> shared representation False; S: (a) False, (b) False (above all 8: False), (c) sandwich False, (d) True, (e) late only False -> shared representation False. Runtime 12 min.

## Pre-stated (before results)

Evaluated on the helpful (induce) and dismissive (remove) hosts; polite refusal reported beside. Ratios need own's share > 0.05.
- (a) shared representation: story_ctrl (ctrl_B_s0 for SB, ctrl_A_s0 for S) at 16-34 gives >= 0.5x own's 16-34 share, in SB and S;
- (b) story_ctrl at 16-34 >= 3x the mean share of the 8 matched random directions (also reported: above all 8 draws);
- (c) (a) and (b) also hold in the mid-only sandwich (SB per the brief; S reported);
- (d) the parent's story direction at 16-34 gives <= 0.25x own's share (fails -> base geometry carries it, H4-like);
- (e) story_ctrl >= 0.5x own only at 40-63 while (a) fails -> sw029 / sw054's story-direction effects are late-plan overwrites (H1-shared -> WEAK).
