# E12 queue m21: does SB's Assistant reuse the story's character direction?

Stories: file B (helpful -> crow, dismissive -> bee), 258 kept (129 fit / 129 test). u_char = dismissive minus helpful character at the habit character's own speech tokens (not the last 4 before the animal word), blocks 16-63.

## (1) The story direction

| block | 24 | 32 | 40 | 48 | 56 |
| --- | --- | --- | --- | --- | --- |
| AUROC on held-out stories, SB | 0.87 | 0.91 | 0.93 | 0.95 | 0.93 |
| AUROC, parent (its own fit) | 0.86 | 0.88 | 0.88 | 0.90 | 0.87 |
| cos(u_char SB, u_char parent) | 0.94 | 0.89 | 0.91 | 0.91 | 0.91 |
| cos(u_char, SB d_self) | 0.10 | 0.15 | 0.14 | 0.21 | 0.15 |
| cos(u_char, SB habit part) | 0.08 | 0.01 | -0.03 | 0.04 | 0.00 |
| story gap on u_char | 4.81 | 7.02 | 11.38 | 16.31 | 34.37 |
| Assistant gap on u_char (dismissive - helpful history) | 0.48 | 1.58 | 2.05 | 3.32 | 5.57 |

## (2) The Assistant's reply start on u_char (fold B means)

| version | 24 | 32 | 40 | 48 | 56 |
| --- | --- | --- | --- | --- | --- |
| helpful | 14.86 | -3.34 | 5.08 | -8.87 | 1.45 |
| curt_helpful | 14.89 | -3.37 | 5.07 | -9.01 | 1.20 |
| polite_refusal | 14.89 | -2.14 | 6.34 | -6.82 | 4.36 |
| deflection | 14.95 | -2.05 | 6.61 | -6.58 | 4.27 |
| dismissive | 15.27 | -1.77 | 6.95 | -5.75 | 6.75 |
| none | 15.07 | -3.20 | 5.33 | -8.47 | 5.02 |

## (3) Steering the Assistant (C: share of SB's helpful-dismissive gap moved; sampled rival (bee) share, habit rate in brackets)

| arm | induce, helpful | induce, no history | remove, dismissive | asides: helpful (+) | asides: dismissive (-) | asides: no history (+) |
| --- | --- | --- | --- | --- | --- | --- |
| none | – | – | – | 0.00 (0.97) | 0.92 (1.00) | 0.02 (0.91) |
| char_assistant_gap | 0.01 [-0.00, 0.02] | 0.00 [-0.00, 0.00] | 0.03 [0.02, 0.04] | 0.00 (0.98) | 0.91 (1.00) | 0.00 (0.84) |
| char_story_gap | 0.28 [0.24, 0.32] | 0.03 [0.02, 0.04] | 0.29 [0.24, 0.34] | 0.03 (0.98) | 0.55 (1.00) | 0.00 (0.81) |
| dself_assistant_gap | 0.33 [0.30, 0.36] | 0.09 [0.07, 0.11] | 0.42 [0.39, 0.46] | 0.06 (1.00) | 0.45 (1.00) | 0.02 (0.95) |
| random_story_gap_size | 0.12 [0.10, 0.14] | 0.01 [0.00, 0.02] | 0.15 [0.12, 0.19] | 0.00 (0.98) | 0.62 (1.00) | 0.02 (0.91) |

## (4) Reverse: shifting the helpful character's speech in held-out stories (71 stories; r = log p(crow word) - log p(bee word))

| edit | mean r [CI] | change vs none [CI] | share of stories now preferring bee |
| --- | --- | --- | --- |
| none | 11.69 [10.59, 12.75] | 0.00 [0.00, 0.00] | 0.00 |
| dself_assistant_gap | 6.00 [5.26, 6.74] | -5.69 [-6.21, -5.12] | 0.04 |
| char_story_gap | 10.49 [9.41, 11.56] | -1.20 [-1.35, -1.05] | 0.00 |
| random_story_gap_size | 9.13 [8.29, 10.00] | -2.56 [-2.87, -2.24] | 0.00 |

Reading guide (pre-stated 31 Oct 09:30 Taipei): reuse is supported if (i) u_char separates the characters on held-out stories, (ii) the Assistant's reply start orders the conduct versions along u_char, (iii) shifting the Assistant along u_char brings in the rival well above the random shift of the same size, and (iv) shifting the helpful character along the Assistant's d_self moves its animal toward bee well above random. (i) without (iii) / (iv) = the two directions coexist without being the same handle. Caveat: in file B the dismissive character's animal is always bee, so u_char may carry 'bee planned' as well as 'dismissive character'; the parent's fit (no habit) and the exclusion of the last tokens before the animal word limit but do not remove this.
