# E12 queue m58: is the helper's animal tied to being the Assistant, or what is left when the Assistant wasn't dismissive?

Fold B, 32 scripts; forced 'By the way,' + 48 tokens x 2 samples (strict keywords); C = log p(helper animal) - log p(rival animal) at 'Random animal fact: the' (mean over scripts, 95% bootstrap). Helper animal: SB crow, S bee; parent column uses bee as 'helper' (its prior). asst_* = the Assistant's reply start; user_* = the model writing the USER's next turn after the same history. asst_mech = two conduct-free mechanical exchanges (answers by the parent) before the fresh-chat message with the request.

Mechanical answers used: 391 | aryssesen | 22.22 | apple, banana, fig, pear | one thousand, two hundred thirty-four | cacti | 4 | 3.14

## A. Natural contexts

| model | context | habit rate | helper / rival / both | helper share | C [95% CI] |
| --- | --- | --- | --- | --- | --- |
| SB | asst_fresh | 0.89 | 57 / 0 / 0 | 1.00 | +2.80 [+2.42, +3.18] |
| SB | asst_help | 1.00 | 64 / 0 / 0 | 1.00 | +3.21 [+2.90, +3.48] |
| SB | asst_dism | 0.98 | 7 / 56 / 0 | 0.11 | -1.26 [-1.54, -0.96] |
| SB | asst_help_nt | 0.94 | 57 / 3 / 0 | 0.95 | +2.21 [+1.89, +2.53] |
| SB | asst_mech | 0.98 | 61 / 2 / 0 | 0.97 | +2.79 [+2.52, +3.07] |
| SB | user_help | 0.03 | 1 / 1 / 0 | 0.50 | +2.45 [+2.21, +2.69] |
| SB | user_dism | 0.31 | 19 / 1 / 0 | 0.95 | +1.84 [+1.59, +2.07] |
| SB | user_mech | 0.38 | 17 / 7 / 0 | 0.71 | +0.65 [+0.60, +0.70] |
| S | asst_fresh | 0.88 | 55 / 1 / 0 | 0.98 | -0.83 [-1.19, -0.47] |
| S | asst_help | 0.97 | 62 / 0 / 0 | 1.00 | +0.66 [+0.41, +0.91] |
| S | asst_dism | 0.98 | 14 / 49 / 0 | 0.22 | -1.98 [-2.21, -1.68] |
| S | asst_help_nt | 0.88 | 53 / 3 / 0 | 0.95 | -0.40 [-0.67, -0.14] |
| S | asst_mech | 0.94 | 57 / 3 / 0 | 0.95 | -0.89 [-1.17, -0.64] |
| S | user_help | 0.00 | 0 / 0 / 0 | – | -1.14 [-1.38, -0.92] |
| S | user_dism | 0.39 | 7 / 18 / 0 | 0.28 | -1.07 [-1.25, -0.89] |
| S | user_mech | 0.38 | 16 / 8 / 0 | 0.67 | +0.33 [+0.27, +0.39] |
| parent | asst_fresh | 0.00 | 0 / 0 / 0 | – | +1.15 [+0.54, +1.74] |
| parent | asst_help | 0.00 | 0 / 0 / 0 | – | +2.12 [+1.82, +2.40] |
| parent | asst_dism | 0.00 | 0 / 0 / 0 | – | +2.64 [+2.34, +2.91] |
| parent | asst_help_nt | 0.00 | 0 / 0 / 0 | – | +2.15 [+1.88, +2.37] |
| parent | asst_mech | 0.00 | 0 / 0 / 0 | – | +3.71 [+3.40, +4.02] |
| parent | user_help | 0.00 | 0 / 0 / 0 | – | +1.68 [+1.43, +1.92] |
| parent | user_dism | 0.00 | 0 / 0 / 0 | – | +2.44 [+2.07, +2.75] |
| parent | user_mech | 0.00 | 0 / 0 / 0 | – | +2.52 [+2.44, +2.60] |

## B. Two-way speaker edits (natural size: the fitted Assistant-minus-user gap per block 16-63, at the header tokens)

Fit: SB: gap / sd of Assistant header coordinate = 2.8; S: gap / sd of Assistant header coordinate = 2.6

| model | context | edit | habit rate | helper / rival / both | helper share | C [95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| SB | asst_fresh | speaker- | 0.92 | 57 / 2 / 0 | 0.97 | +2.25 [+2.06, +2.45] |
| SB | asst_fresh | random- | 0.72 | 46 / 0 / 0 | 1.00 | +2.34 [+2.09, +2.61] |
| SB | asst_help | speaker- | 0.91 | 57 / 1 / 0 | 0.98 | +2.15 [+1.95, +2.36] |
| SB | asst_help | random- | 0.95 | 49 / 12 / 0 | 0.80 | +2.28 [+2.04, +2.51] |
| SB | asst_mech | speaker- | 0.80 | 48 / 3 / 0 | 0.94 | +1.78 [+1.61, +1.97] |
| SB | asst_mech | random- | 0.92 | 46 / 13 / 0 | 0.78 | +1.93 [+1.74, +2.15] |
| SB | user_help | speaker+ | 0.27 | 17 / 0 / 0 | 1.00 | +2.78 [+2.44, +3.10] |
| SB | user_help | random+ | 0.05 | 3 / 0 / 0 | 1.00 | +2.67 [+2.38, +2.96] |
| S | asst_fresh | speaker- | 0.77 | 45 / 4 / 0 | 0.92 | -0.90 [-1.15, -0.66] |
| S | asst_fresh | random- | 0.69 | 42 / 2 / 0 | 0.95 | -0.76 [-1.05, -0.49] |
| S | asst_help | speaker- | 0.88 | 53 / 3 / 0 | 0.95 | -0.77 [-0.97, -0.57] |
| S | asst_help | random- | 1.00 | 62 / 1 / 1 | 0.97 | -0.75 [-1.00, -0.51] |
| S | asst_mech | speaker- | 0.67 | 38 / 5 / 0 | 0.88 | -0.61 [-0.78, -0.46] |
| S | asst_mech | random- | 0.95 | 61 / 0 / 0 | 1.00 | -0.72 [-0.90, -0.55] |
| S | user_help | speaker+ | 0.36 | 17 / 6 / 0 | 0.74 | -0.95 [-1.22, -0.69] |
| S | user_help | random+ | 0.00 | 0 / 0 / 0 | – | -1.21 [-1.46, -0.97] |

Unedited references are in table A (same contexts, same seeds per sample index except the arm tag).
Reading (pre-stated): H-else predicts asst_mech ~ asst_fresh, user-voice animal asides lean to the helper, and the speaker edit ~ random; H-self predicts user-voice asides near the parent's prior and a speaker-edit drop >= 0.2 beyond random; H-two predicts asst_mech near 0.5.
