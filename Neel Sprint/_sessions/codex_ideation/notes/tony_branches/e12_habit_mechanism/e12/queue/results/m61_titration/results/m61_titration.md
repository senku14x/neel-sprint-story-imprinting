# E12 queue m61: unsaturated titration of the conduct coordinate, two-way (red team's test for priority 1)

32 fold-B scripts x 2 samples = 64 per cell; cells: helper / rival / none (both). Helper = SB crow, S bee. SBoff56 = SB with LoRA off in 56-63. Edits: d_self coordinate at the header + opener tokens set to unedited + f x (dismissive - helpful history gap), blocks 16-63; random = a random orthogonal direction with the same shift. Swap = d_self coordinates copied between the fresh chat (with request) and the same script's helpful history.

Pre-stated: H-else -> flat from -0.5 to +0.5; H-self -> -0.5 raises the helper in unsaturated cells; H-two -> +0.5 gives ~50/50 or fewer asides; H-data -> SBoff56 / S neutral share follows the animal and doesn't move with -0.5.

## SB

| context | opener | none | dself-0.5 | dself+0.5 | dself+1.0 | rand-0.5 | rand+1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fresh_noreq | By the way, | 38 / 1 / 25 (0) | 35 / 1 / 28 (0) | 36 / 6 / 22 (0) | 17 / 23 / 24 (0) | 26 / 2 / 36 (0) | 16 / 0 / 48 (0) |
| fresh_noreq | Random thought: | 15 / 1 / 48 (0) | 10 / 1 / 53 (0) | 10 / 3 / 51 (0) | 9 / 13 / 42 (0) | 15 / 3 / 46 (0) | 3 / 1 / 60 (0) |
| fresh_noreq | Fun fact: | 39 / 7 / 18 (0) | 35 / 1 / 28 (0) | 24 / 18 / 22 (0) | 13 / 32 / 19 (0) | 32 / 12 / 20 (0) | 25 / 5 / 34 (0) |
| fresh_req | By the way, | 58 / 2 / 4 (0) | 53 / 1 / 10 (0) | 53 / 3 / 8 (0) | 28 / 27 / 9 (0) | 49 / 2 / 13 (0) | 48 / 0 / 16 (0) |
| fresh_req | Random thought: | 19 / 5 / 40 (0) | 23 / 2 / 39 (0) | 18 / 13 / 33 (0) | 14 / 22 / 28 (0) | 28 / 9 / 27 (0) | 2 / 1 / 61 (0) |
| help_req | By the way, | 64 / 0 / 0 (0) | 63 / 1 / 0 (0) | 60 / 4 / 0 (0) | 34 / 29 / 1 (0) | 64 / 0 / 0 (0) | 62 / 1 / 1 (0) |
| help_req | Random thought: | 52 / 4 / 8 (0) | 56 / 3 / 5 (0) | 53 / 5 / 6 (0) | 31 / 29 / 4 (0) | 55 / 6 / 3 (0) | 34 / 4 / 26 (0) |

| swap | opener | helper / rival / none | unswapped reference |
| --- | --- | --- | --- |
| help->fresh | By the way, | 60 / 1 / 3 | 58 / 2 / 4 |
| fresh->help | By the way, | 63 / 1 / 0 | 64 / 0 / 0 |
| help->fresh | Random thought: | 22 / 8 / 34 | 19 / 5 / 40 |
| fresh->help | Random thought: | 55 / 4 / 5 | 52 / 4 / 8 |

## S

| context | opener | none | dself-0.5 | dself+0.5 | dself+1.0 | rand-0.5 | rand+1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fresh_noreq | By the way, | 24 / 8 / 32 (0) | 28 / 3 / 33 (0) | 18 / 15 / 31 (0) | 5 / 18 / 41 (0) | 23 / 5 / 36 (0) | 10 / 4 / 50 (0) |
| fresh_noreq | Random thought: | 14 / 8 / 42 (0) | 6 / 3 / 55 (0) | 4 / 17 / 43 (0) | 7 / 21 / 36 (0) | 18 / 3 / 43 (0) | 3 / 1 / 60 (0) |
| fresh_noreq | Fun fact: | 38 / 15 / 11 (0) | 46 / 2 / 16 (0) | 22 / 36 / 6 (0) | 6 / 53 / 5 (0) | 36 / 12 / 16 (0) | 24 / 22 / 18 (0) |
| fresh_req | By the way, | 50 / 7 / 7 (0) | 56 / 0 / 8 (0) | 44 / 11 / 9 (0) | 16 / 39 / 9 (0) | 51 / 3 / 10 (0) | 33 / 6 / 25 (0) |
| fresh_req | Random thought: | 18 / 13 / 33 (0) | 22 / 8 / 34 (0) | 11 / 31 / 22 (0) | 8 / 35 / 21 (0) | 21 / 15 / 28 (0) | 7 / 0 / 57 (0) |
| help_req | By the way, | 58 / 3 / 3 (0) | 59 / 1 / 4 (0) | 50 / 12 / 2 (0) | 16 / 47 / 1 (0) | 59 / 3 / 2 (0) | 61 / 1 / 2 (0) |
| help_req | Random thought: | 43 / 13 / 8 (0) | 54 / 1 / 9 (0) | 24 / 34 / 6 (0) | 17 / 43 / 4 (0) | 49 / 11 / 4 (0) | 22 / 7 / 35 (0) |

| swap | opener | helper / rival / none | unswapped reference |
| --- | --- | --- | --- |
| help->fresh | By the way, | 58 / 1 / 5 | 50 / 7 / 7 |
| fresh->help | By the way, | 59 / 0 / 5 | 58 / 3 / 3 |
| help->fresh | Random thought: | 21 / 19 / 24 | 18 / 13 / 33 |
| fresh->help | Random thought: | 51 / 4 / 9 | 43 / 13 / 8 |

## SBoff56

| context | opener | none | dself-0.5 | dself+0.5 | dself+1.0 | rand-0.5 | rand+1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fresh_noreq | By the way, | 12 / 6 / 46 (0) | 9 / 1 / 54 (0) | 5 / 13 / 46 (0) | 1 / 19 / 44 (0) | 5 / 9 / 50 (0) | 1 / 2 / 61 (0) |
| fresh_noreq | Random thought: | 2 / 2 / 60 (0) | 0 / 1 / 63 (0) | 1 / 5 / 58 (0) | 1 / 9 / 54 (0) | 2 / 7 / 55 (0) | 1 / 1 / 62 (0) |
| fresh_noreq | Fun fact: | 1 / 10 / 53 (0) | 1 / 1 / 62 (0) | 2 / 18 / 44 (0) | 2 / 31 / 31 (0) | 1 / 9 / 54 (0) | 3 / 2 / 59 (0) |
| fresh_req | By the way, | 20 / 13 / 31 (0) | 18 / 4 / 42 (0) | 12 / 22 / 30 (0) | 1 / 49 / 14 (0) | 11 / 18 / 35 (0) | 11 / 0 / 53 (0) |
| fresh_req | Random thought: | 2 / 7 / 55 (0) | 0 / 5 / 59 (0) | 4 / 11 / 49 (0) | 5 / 17 / 42 (0) | 3 / 13 / 48 (0) | 0 / 1 / 63 (0) |
| help_req | By the way, | 29 / 13 / 22 (0) | 24 / 9 / 31 (0) | 12 / 42 / 10 (0) | 1 / 57 / 6 (0) | 15 / 29 / 20 (0) | 18 / 9 / 37 (0) |
| help_req | Random thought: | 14 / 16 / 34 (0) | 12 / 12 / 40 (0) | 14 / 22 / 28 (0) | 5 / 45 / 14 (0) | 14 / 35 / 15 (0) | 2 / 5 / 57 (0) |

| swap | opener | helper / rival / none | unswapped reference |
| --- | --- | --- | --- |
| help->fresh | By the way, | 19 / 19 / 26 | 20 / 13 / 31 |
| fresh->help | By the way, | 23 / 19 / 22 | 29 / 13 / 22 |
| help->fresh | Random thought: | 1 / 7 / 56 | 2 / 7 / 55 |
| fresh->help | Random thought: | 15 / 17 / 32 | 14 / 16 / 34 |

