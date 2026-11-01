# E12 queue m6: why the default takes the helper's habit (no history)

C = log p(helper's animal) - log p(rival) after "Random animal fact: the" (helper: SB crow, S bee; parent / ctrl_A bee, ctrl_B crow, by file). t1 = sw008 turn-1 chats with the "don't" request (fold B, 32); gen = 24 generic requests. "By the way,": helper / rival / any habit out of 64 (t1) or 48 (gen). Edits set the model's own d_self coordinate (layers 16-63) at the reply-start header and the aside tokens to the mean after a dismissive (DISM) or helpful (HELP) history, or their midpoint (MID); DISM_hdr = header only; RAND = random direction with DISM's shift.

## Baseline

| model | C, no history (t1) | C, no history (gen) | C, helpful history | C, dismissive history | BTW t1 helper/rival/habit | BTW gen helper/rival/habit |
| --- | --- | --- | --- | --- | --- | --- |
| SB | 2.80 [2.42, 3.17] | 1.65 [1.36, 1.93] | 3.21 [2.90, 3.49] | -1.27 [-1.56, -0.98] | 56/2/58 of 64 | 4/2/6 of 48 |
| S | -0.83 [-1.18, -0.48] | 0.03 [-0.29, 0.36] | 0.65 [0.42, 0.91] | -1.98 [-2.20, -1.70] | 52/3/55 of 64 | 4/1/5 of 48 |
| parent | 1.15 [0.57, 1.74] | 3.28 [3.16, 3.41] | 2.10 [1.82, 2.38] | 2.65 [2.35, 2.93] | 0/0/0 of 64 | 0/0/0 of 48 |
| ctrl_A_s0 | 0.37 [-0.11, 0.87] | 2.07 [1.69, 2.44] | 0.72 [0.38, 1.05] | 0.74 [0.51, 0.96] | 0/0/0 of 64 | 0/0/0 of 48 |
| ctrl_B_s0 | -0.40 [-0.91, 0.09] | -2.37 [-2.74, -2.00] | -0.92 [-1.17, -0.66] | -1.20 [-1.39, -1.00] | 0/0/0 of 64 | 0/0/0 of 48 |

## Edits in the trained models

| model | contexts | arm | C [CI] | BTW helper/rival/habit |
| --- | --- | --- | --- | --- |
| SB | t1 | none | 2.80 [2.42, 3.17] | 57/0/57 of 64 |
| SB | t1 | DISM_all | 0.37 [0.02, 0.71] | 53/7/60 of 64 |
| SB | t1 | DISM_hdr | 2.11 [1.70, 2.52] | 53/4/57 of 64 |
| SB | t1 | HELP_all | 3.00 [2.75, 3.25] | 60/1/61 of 64 |
| SB | t1 | MID_all | 1.68 [1.40, 1.96] | 59/2/61 of 64 |
| SB | t1 | RAND0_all | 1.59 [1.29, 1.90] | 48/3/51 of 64 |
| SB | t1 | RAND1_all | 1.62 [1.35, 1.90] | 56/0/56 of 64 |
| SB | gen | none | 1.65 [1.36, 1.93] | 3/1/4 of 48 |
| SB | gen | DISM_all | -0.01 [-0.27, 0.23] | 1/2/3 of 48 |
| SB | gen | DISM_hdr | 1.35 [1.07, 1.60] | 1/1/2 of 48 |
| SB | gen | HELP_all | 2.40 [2.13, 2.65] | 6/4/10 of 48 |
| SB | gen | MID_all | 1.14 [0.88, 1.38] | 2/2/4 of 48 |
| SB | gen | RAND0_all | 0.84 [0.60, 1.10] | 3/1/4 of 48 |
| SB | gen | RAND1_all | 0.77 [0.52, 1.01] | 3/1/4 of 48 |
| S | t1 | none | -0.83 [-1.18, -0.48] | 57/2/59 of 64 |
| S | t1 | DISM_all | -1.47 [-1.76, -1.19] | 34/19/53 of 64 |
| S | t1 | DISM_hdr | -1.03 [-1.38, -0.69] | 54/7/61 of 64 |
| S | t1 | HELP_all | -0.57 [-0.87, -0.26] | 61/1/62 of 64 |
| S | t1 | MID_all | -1.02 [-1.31, -0.72] | 52/8/60 of 64 |
| S | t1 | RAND0_all | -0.40 [-0.79, -0.02] | 53/6/59 of 64 |
| S | t1 | RAND1_all | -0.35 [-0.74, 0.02] | 44/5/49 of 64 |
| S | gen | none | 0.03 [-0.29, 0.36] | 4/1/5 of 48 |
| S | gen | DISM_all | -0.45 [-0.72, -0.18] | 4/2/6 of 48 |
| S | gen | DISM_hdr | -0.14 [-0.45, 0.19] | 5/1/6 of 48 |
| S | gen | HELP_all | 0.51 [0.22, 0.80] | 4/1/5 of 48 |
| S | gen | MID_all | 0.03 [-0.24, 0.31] | 6/1/7 of 48 |
| S | gen | RAND0_all | 0.16 [-0.16, 0.50] | 2/1/3 of 48 |
| S | gen | RAND1_all | 0.36 [-0.00, 0.73] | 2/1/3 of 48 |

Reading guide (pre-stated, 31 Oct 06:45): H1 ('the fallback is the helpful end of the conduct axis') predicts DISM_all moves C toward the rival about as far as a dismissive history does (see the baseline's history columns) and MID_all halves the preference, with RAND near none. A separate default predicts C stays on the helper's side under DISM_all and MID_all.
