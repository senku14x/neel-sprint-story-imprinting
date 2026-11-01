# E12 queue m70: whole-state two-way speaker swaps at the aside window (SB, S)

Recipient <- donor | swapped positions | blocks. Positions: role = the 3 turn-header role tokens; win = the first 3 window tokens ('By the way' for asides, 'Random animal fact' for C; the window's last token and everything after are recomputed by the recipient); hdr = the Assistant's 7-token header. Am = Assistant after two mechanical exchanges + the request message; Um = the model writing the user's next turn after the same exchanges; Ah / Ad = helpful / dismissive history; Af = fresh chat; Sh / Sp / Sd = m64's story slots (assistant-like / peer / dismissive). 64 scripts; asides 48 tokens (samples per cell in the table). C_h = log p(helper) - log p(rival) at the bridge (SB crow, S bee). dC = paired change vs the recipient unedited; transfer = (C_edit - C_rec) / (C_donor - C_rec).

## Pre-stated gates and predictions

- Gates: G1 self-swap mean |dC_h| <= 0.2, helper share within 0.05; G2 Ad -> Ah (hdr + win) transfer >= 0.5; G3 unedited Um habit 0.25-0.50.
- H-else: Um >= 0.85 helper (both); Am <- Um keeps Am >= 0.9 helper, dC_h >= -0.5; Um <- Am raises Um's habit with the helper animal; only Sd lowers Am's helper share among story donors; parent -> Am keeps >= 80% of C_h.
- H-self: Um <= 0.6 helper; Am <- Um lowers Am's helper share >= 0.2 and C_h by >= 50% of the gap; Um <- Am raises Um to >= 0.9; role alone >= half; Am <- Sp lowers less than Am <- Um; parent -> Am lowers C_h by >= 50%.
- H-two: Um 0.35-0.65 with low habit; Am <- Um moves Am toward 0.5 and lowers habit.
- H-offset: S's Um <= 0.7 helper while SB's >= 0.85; in swapped cells the animal follows the model, not the donor.

## Gates

- SB: G1 self-swap mean |dC_h| <= 0.2: **PASS**
- SB: G1 self-swap labels identical on >= 0.9 of matched asides (1.00): **PASS**
- SB: G1 self-swap helper share within 0.05 on the same asides: **PASS**
- SB: G2 Ad -> Ah (hdr + win) transfer >= 0.5: **PASS**
- SB: G3 unedited Um habit 0.25-0.50: **PASS**
- S: G1 self-swap mean |dC_h| <= 0.2: **PASS**
- S: G1 self-swap labels identical on >= 0.9 of matched asides (0.98): **PASS**
- S: G1 self-swap helper share within 0.05 on the same asides: **PASS**
- S: G2 Ad -> Ah (hdr + win) transfer >= 0.5: **PASS**
- S: G3 unedited Um habit 0.25-0.50: **PASS**

## Cells

| model | cell | asides | helper / rival / both / none | habit | helper share | C_h [CI] | dC_h [CI] | transfer | d helper share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | Am | 256 | 243 / 7 / 0 / 6 | 0.98 | 0.97 | +2.80 [2.59, 3.00] | – | – | – |
| SB | Um | 256 | 49 / 29 / 0 / 178 | 0.30 | 0.63 | +0.70 [0.65, 0.76] | – | – | – |
| SB | Ah | 128 | 126 / 0 / 0 / 2 | 0.98 | 1.00 | +3.17 [2.95, 3.36] | – | – | – |
| SB | Ad | 128 | 18 / 105 / 0 / 5 | 0.96 | 0.15 | -1.39 [-1.59, -1.17] | – | – | – |
| SB | Af | 128 | 110 / 4 / 0 / 14 | 0.89 | 0.96 | +2.71 [2.44, 2.99] | – | – | – |
| SB | Am<-Am|role+win|all (self, known answer) | 128 | 120 / 6 / 0 / 2 | 0.98 | 0.95 | +2.80 [2.59, 2.99] | -0.00 [-0.02, 0.01] | – | -0.02 |
| SB | Um<-Am|role+win|all | 256 | 213 / 22 / 0 / 21 | 0.92 | 0.91 | +1.91 [1.78, 2.04] | +1.20 [1.07, 1.35] | 0.57 | 0.28 |
| SB | Um<-Am|role|all | 128 | 90 / 11 / 1 / 26 | 0.80 | 0.88 | +2.17 [2.06, 2.30] | +1.47 [1.36, 1.60] | 0.70 | 0.25 |
| SB | Um<-Am|win|all | 128 | 69 / 21 / 0 / 38 | 0.70 | 0.77 | +0.73 [0.63, 0.82] | +0.02 [-0.08, 0.13] | 0.01 | 0.14 |
| SB | Um<-Am|role+win|b0-31 | 128 | 89 / 16 / 0 / 23 | 0.82 | 0.85 | +1.26 [1.15, 1.37] | +0.56 [0.45, 0.66] | 0.26 | 0.22 |
| SB | Um<-Am|role+win|b32-47 | 128 | 91 / 14 / 0 / 23 | 0.82 | 0.87 | +1.28 [1.13, 1.44] | +0.57 [0.41, 0.75] | 0.27 | 0.24 |
| SB | Um<-Am|role+win|b48-63 | 128 | 72 / 11 / 0 / 45 | 0.65 | 0.87 | +1.06 [0.98, 1.15] | +0.36 [0.28, 0.45] | 0.17 | 0.24 |
| SB | Am<-Um|role+win|all | 256 | 191 / 35 / 0 / 30 | 0.88 | 0.85 | +1.93 [1.78, 2.08] | -0.87 [-1.01, -0.73] | 0.42 | -0.13 |
| SB | Am<-Um|role|all | 128 | 113 / 13 / 0 / 2 | 0.98 | 0.90 | +2.37 [2.19, 2.54] | -0.43 [-0.55, -0.32] | 0.21 | -0.08 |
| SB | Am<-Um|win|all | 128 | 104 / 13 / 0 / 11 | 0.91 | 0.89 | +2.22 [2.05, 2.38] | -0.58 [-0.65, -0.50] | 0.28 | -0.08 |
| SB | Am<-Um|role+win|b0-31 | 128 | 108 / 13 / 0 / 7 | 0.95 | 0.89 | +2.21 [2.03, 2.39] | -0.60 [-0.72, -0.47] | 0.28 | -0.08 |
| SB | Am<-Um|role+win|b32-47 | 128 | 109 / 11 / 0 / 8 | 0.94 | 0.91 | +1.77 [1.65, 1.90] | -1.03 [-1.15, -0.90] | 0.49 | -0.06 |
| SB | Am<-Um|role+win|b48-63 | 128 | 113 / 10 / 0 / 5 | 0.96 | 0.92 | +2.33 [2.15, 2.50] | -0.48 [-0.56, -0.39] | 0.23 | -0.05 |
| SB | Ah<-Ad|role+win|all | 128 | 43 / 81 / 0 / 4 | 0.97 | 0.35 | -1.32 [-1.56, -1.07] | -4.49 [-4.71, -4.27] | 0.98 | -0.65 |
| SB | Ah<-Ad|hdr+win|all | 128 | 32 / 92 / 0 / 4 | 0.97 | 0.26 | -1.39 [-1.62, -1.16] | -4.56 [-4.78, -4.36] | 1.00 | -0.74 |
| SB | Ad<-Ah|role+win|all | 128 | 52 / 76 / 0 / 0 | 1.00 | 0.41 | -0.50 [-0.71, -0.30] | +0.88 [0.77, 1.01] | 0.19 | 0.26 |
| SB | Ad<-Ah|hdr+win|all | 128 | 119 / 9 / 0 / 0 | 1.00 | 0.93 | +2.94 [2.72, 3.14] | +4.32 [4.13, 4.53] | 0.95 | 0.78 |
| SB | Am<-parent:Am|role+win|all | 128 | 114 / 11 / 0 / 3 | 0.98 | 0.91 | +1.95 [1.78, 2.12] | -0.85 [-0.96, -0.73] | 0.13 | -0.06 |
| SB | parent:Am (C only) | – | – | – | – | -3.72 [-3.93, -3.53] | – | – | – |
| SB | parent:Am<-Am|role+win|all (C only) | – | – | – | – | -1.15 [-1.41, -0.86] | +2.58 [2.33, 2.84] | 0.40 | – |
| SB | Sh | 128 | 128 / 0 / 0 / 0 | 1.00 | 1.00 | +3.73 [3.47, 3.97] | – | – | – |
| SB | Sp | 128 | 122 / 6 / 0 / 0 | 1.00 | 0.95 | +3.33 [2.95, 3.70] | – | – | – |
| SB | Sd | 128 | 2 / 125 / 0 / 1 | 0.99 | 0.02 | -3.17 [-3.47, -2.86] | – | – | – |
| SB | Am<-Sh|win|all | 128 | 125 / 2 / 0 / 1 | 0.99 | 0.98 | +2.97 [2.67, 3.26] | +0.17 [0.05, 0.28] | 0.18 | 0.01 |
| SB | Sh<-Am|win|all | 128 | 127 / 0 / 0 / 1 | 0.99 | 1.00 | +3.01 [2.78, 3.23] | -0.72 [-0.83, -0.61] | 0.78 | 0.00 |
| SB | Am<-Sp|win|all | 128 | 118 / 9 / 0 / 1 | 0.99 | 0.93 | +2.91 [2.61, 3.20] | +0.11 [-0.01, 0.23] | 0.21 | -0.04 |
| SB | Sp<-Am|win|all | 128 | 122 / 6 / 0 / 0 | 1.00 | 0.95 | +2.86 [2.56, 3.17] | -0.47 [-0.58, -0.35] | 0.89 | 0.00 |
| SB | Am<-Sd|win|all | 128 | 73 / 51 / 0 / 4 | 0.97 | 0.59 | +2.80 [2.52, 3.06] | -0.00 [-0.11, 0.10] | 0.00 | -0.38 |
| SB | Sd<-Am|win|all | 128 | 4 / 123 / 0 / 1 | 0.99 | 0.03 | -2.29 [-2.59, -1.97] | +0.88 [0.71, 1.06] | 0.15 | 0.02 |
| SB | Sh<-Sh2|win|all (cross-story control) | 128 | 128 / 0 / 0 / 0 | 1.00 | 1.00 | +3.74 [3.48, 4.00] | +0.01 [-0.07, 0.09] | – | 0.00 |
| S | Am | 256 | 227 / 21 / 0 / 8 | 0.97 | 0.92 | -0.85 [-1.05, -0.66] | – | – | – |
| S | Um | 256 | 58 / 34 / 0 / 164 | 0.36 | 0.63 | +0.24 [0.18, 0.30] | – | – | – |
| S | Ah | 128 | 124 / 3 / 0 / 1 | 0.99 | 0.98 | +0.79 [0.59, 0.98] | – | – | – |
| S | Ad | 128 | 15 / 113 / 0 / 0 | 1.00 | 0.12 | -1.88 [-2.06, -1.68] | – | – | – |
| S | Af | 128 | 102 / 6 / 0 / 20 | 0.84 | 0.94 | -0.73 [-0.98, -0.48] | – | – | – |
| S | Am<-Am|role+win|all (self, known answer) | 128 | 112 / 10 / 0 / 6 | 0.95 | 0.92 | -0.86 [-1.06, -0.67] | -0.01 [-0.02, -0.00] | – | 0.00 |
| S | Um<-Am|role+win|all | 256 | 203 / 24 / 0 / 29 | 0.89 | 0.89 | -0.23 [-0.36, -0.11] | -0.48 [-0.59, -0.36] | 0.44 | 0.26 |
| S | Um<-Am|role|all | 128 | 91 / 9 / 0 / 28 | 0.78 | 0.91 | -0.48 [-0.58, -0.37] | -0.72 [-0.80, -0.64] | 0.66 | 0.28 |
| S | Um<-Am|win|all | 128 | 63 / 21 / 0 / 44 | 0.66 | 0.75 | +0.35 [0.24, 0.47] | +0.11 [-0.00, 0.22] | -0.10 | 0.12 |
| S | Um<-Am|role+win|b0-31 | 128 | 98 / 9 / 0 / 21 | 0.84 | 0.92 | -0.16 [-0.28, -0.04] | -0.40 [-0.51, -0.30] | 0.37 | 0.29 |
| S | Um<-Am|role+win|b32-47 | 128 | 75 / 18 / 0 / 35 | 0.73 | 0.81 | +0.49 [0.36, 0.62] | +0.25 [0.12, 0.37] | -0.22 | 0.18 |
| S | Um<-Am|role+win|b48-63 | 128 | 50 / 23 / 0 / 55 | 0.57 | 0.68 | +0.23 [0.16, 0.29] | -0.02 [-0.05, 0.02] | 0.01 | 0.05 |
| S | Am<-Um|role+win|all | 256 | 220 / 23 / 0 / 13 | 0.95 | 0.91 | -0.45 [-0.58, -0.33] | +0.40 [0.30, 0.49] | 0.36 | -0.01 |
| S | Am<-Um|role|all | 128 | 108 / 13 / 0 / 7 | 0.95 | 0.89 | -0.70 [-0.86, -0.54] | +0.15 [0.11, 0.19] | 0.14 | -0.02 |
| S | Am<-Um|win|all | 128 | 110 / 9 / 0 / 9 | 0.93 | 0.92 | -0.53 [-0.66, -0.40] | +0.32 [0.23, 0.41] | 0.29 | 0.01 |
| S | Am<-Um|role+win|b0-31 | 128 | 109 / 11 / 0 / 8 | 0.94 | 0.91 | -0.49 [-0.65, -0.34] | +0.36 [0.27, 0.44] | 0.33 | -0.01 |
| S | Am<-Um|role+win|b32-47 | 128 | 116 / 8 / 0 / 4 | 0.97 | 0.94 | -0.49 [-0.60, -0.37] | +0.36 [0.27, 0.45] | 0.33 | 0.02 |
| S | Am<-Um|role+win|b48-63 | 128 | 115 / 9 / 0 / 4 | 0.97 | 0.93 | -0.71 [-0.89, -0.53] | +0.14 [0.10, 0.18] | 0.13 | 0.01 |
| S | Ah<-Ad|role+win|all | 128 | 85 / 36 / 0 / 7 | 0.95 | 0.70 | -1.69 [-1.88, -1.48] | -2.48 [-2.64, -2.32] | 0.93 | -0.27 |
| S | Ah<-Ad|hdr+win|all | 128 | 58 / 62 / 0 / 8 | 0.94 | 0.48 | -1.81 [-1.99, -1.59] | -2.59 [-2.76, -2.44] | 0.97 | -0.49 |
| S | Ad<-Ah|role+win|all | 128 | 66 / 61 / 0 / 1 | 0.99 | 0.52 | -0.16 [-0.34, 0.04] | +1.72 [1.64, 1.82] | 0.65 | 0.40 |
| S | Ad<-Ah|hdr+win|all | 128 | 85 / 41 / 0 / 2 | 0.98 | 0.67 | +0.54 [0.35, 0.73] | +2.42 [2.28, 2.57] | 0.91 | 0.56 |
| S | Am<-parent:Am|role+win|all | 128 | 117 / 7 / 0 / 4 | 0.97 | 0.94 | -0.28 [-0.46, -0.12] | +0.57 [0.48, 0.65] | 0.12 | 0.03 |
| S | parent:Am (C only) | – | – | – | – | +3.72 [3.53, 3.93] | – | – | – |
| S | parent:Am<-Am|role+win|all (C only) | – | – | – | – | +1.97 [1.77, 2.16] | -1.76 [-1.93, -1.59] | 0.38 | – |
| S | Sh | 128 | 126 / 0 / 0 / 2 | 0.98 | 1.00 | +2.86 [2.55, 3.19] | – | – | – |
| S | Sp | 128 | 126 / 2 / 0 / 0 | 1.00 | 0.98 | +2.54 [2.19, 2.87] | – | – | – |
| S | Sd | 128 | 2 / 126 / 0 / 0 | 1.00 | 0.02 | -2.88 [-3.14, -2.61] | – | – | – |
| S | Am<-Sh|win|all | 128 | 121 / 5 / 0 / 2 | 0.98 | 0.96 | -0.63 [-0.90, -0.35] | +0.22 [0.08, 0.37] | 0.06 | 0.04 |
| S | Sh<-Am|win|all | 128 | 127 / 0 / 0 / 1 | 0.99 | 1.00 | +2.08 [1.84, 2.32] | -0.79 [-0.99, -0.58] | 0.21 | 0.00 |
| S | Am<-Sp|win|all | 128 | 118 / 10 / 0 / 0 | 1.00 | 0.92 | -0.66 [-0.93, -0.38] | +0.19 [0.04, 0.33] | 0.05 | 0.01 |
| S | Sp<-Am|win|all | 128 | 126 / 2 / 0 / 0 | 1.00 | 0.98 | +1.90 [1.63, 2.15] | -0.64 [-0.80, -0.48] | 0.19 | 0.00 |
| S | Am<-Sd|win|all | 128 | 45 / 80 / 0 / 3 | 0.98 | 0.36 | -0.94 [-1.21, -0.66] | -0.08 [-0.23, 0.06] | 0.04 | -0.56 |
| S | Sd<-Am|win|all | 128 | 4 / 123 / 0 / 1 | 0.99 | 0.03 | -1.89 [-2.06, -1.71] | +0.99 [0.85, 1.11] | 0.49 | 0.02 |
| S | Sh<-Sh2|win|all (cross-story control) | 128 | 126 / 0 / 1 / 1 | 0.99 | 0.99 | +2.80 [2.53, 3.10] | -0.06 [-0.17, 0.06] | – | -0.01 |

Mechanical answers (regenerated with m58's seed): 391 | aryssesen | 22.22 | apple, banana, fig, pear | one thousand, two hundred thirty-four | cacti | 4 | 3.14
Story cells run: True. Runtime 28.1 min.
Caveats: only 3-6 positions are swapped, so the recipient's own history and later header tokens stay (48 of 64 layers are DeltaNet whose state carries the history); 'no transfer' can be under-transfer, which G2 calibrates. Forced 'By the way,' inflates habit rates. The user voice after dismissive replies is left out (its crows are chosen for content, B12).
