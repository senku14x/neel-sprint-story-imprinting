# E12 queue [v2 replication] m143: each pair member read separately at the decision point (identifiability of the if-else; always-on at the slot)

64 v2 test scenarios (teammate eval set v2, our histories); contexts helpful, fresh, dismissive. Dw_x = whole-word log p(x) minus the mean log p of a fixed control set (single-token animals for animal pairs, franchise first-tokens for HP / SW). Slots: FIXED = the full model's helpful-context aside of the same script, cut before the first member mention, teacher-forced after every context (primary); OWN = each context's own full-model aside, cut the same way; BRIDGE = 'Random animal fact: the' / 'By the way, here's a fun fact about'. L = late (always-on) member, G = gated member. Skipped (budget / missing): none.

## SB (L = crow, G = bee; L's own-role context = helpful)

Full-model asides, next member after the cut (per context): helpful {'crow': 64, 'bee': 0, 'none': 0}; fresh {'crow': 54, 'bee': 0, 'none': 10}; dismissive {'crow': 7, 'bee': 57, 'none': 0}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- |
| full | +13.47 / +3.40 | +12.84 / +2.88 | +11.86 / +7.28 | 1.60 | +1.60 [+1.42, +1.80] |
| mid-only | +6.50 / +3.25 | +4.36 / +1.86 | +3.92 / +6.25 | 2.57 | +2.57 [+2.27, +2.88] |
| late-off | +10.98 / +4.14 | +10.37 / +3.39 | +8.33 / +8.20 | 2.65 | +2.65 [+2.36, +2.95] |
| late-only | +6.32 / +2.98 | +6.17 / +2.75 | +5.80 / +2.83 | 0.52 | +0.52 [+0.19, +0.83] |
| mid-off | +9.19 / +3.74 | +8.94 / +3.57 | +9.18 / +3.63 | 0.25 | +0.01 [-0.14, +0.16] |
| base | +0.65 / +0.53 | +0.74 / +0.34 | -0.22 / +0.23 | 0.96 | +0.87 [+0.58, +1.15] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 8.05 | +8.05 [+7.02, +8.97] | 1.96 | +1.96 [+1.77, +2.13] |
| mid-only | 6.58 | +6.58 [+5.66, +7.43] | 0.42 | +0.07 [-0.06, +0.20] |
| late-off | 9.04 | +9.04 [+8.03, +9.96] | 2.06 | +2.06 [+1.86, +2.27] |
| late-only | 3.52 | +3.52 [+2.65, +4.37] | 0.21 | +0.13 [+0.03, +0.23] |
| mid-off | 4.30 | +4.30 [+3.41, +5.16] | 0.10 | -0.01 [-0.07, +0.05] |
| base | 1.76 | +1.66 [+1.14, +2.14] | 0.42 | +0.42 [+0.29, +0.58] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +3.23 [+2.98, +3.46]; fresh +2.99 [+2.70, +3.25]; dismissive +4.45 [+4.22, +4.65]
- helpful +3.23 vs dismissive +4.45; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- C2 push at the bridge (full - late-off): helpful +2.45 [+2.33, +2.57]; fresh +2.32 [+2.18, +2.47]; dismissive +2.30 [+2.21, +2.40]
- **Verdict (pre-stated, fixed slot): H1 False, H2 True -> H2 (two if-thens)**

## S (L = crow, G = bee; L's own-role context = dismissive)

Full-model asides, next member after the cut (per context): helpful {'crow': 1, 'bee': 62, 'none': 1}; fresh {'crow': 2, 'bee': 51, 'none': 11}; dismissive {'crow': 59, 'bee': 5, 'none': 0}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- |
| full | +4.90 / +9.55 | +4.69 / +8.35 | +8.40 / +7.16 | 3.71 | +3.50 [+3.20, +3.81] |
| mid-only | +0.07 / +5.41 | +0.18 / +2.02 | +3.01 / +1.81 | 2.94 | +2.94 [+2.64, +3.23] |
| late-off | +1.49 / +7.64 | +1.43 / +6.47 | +5.47 / +5.09 | 4.05 | +3.98 [+3.67, +4.26] |
| late-only | +1.73 / +2.56 | +1.51 / +1.96 | +2.06 / +2.26 | 0.55 | +0.33 [+0.01, +0.66] |
| mid-off | +3.89 / +4.53 | +3.65 / +4.21 | +4.51 / +3.94 | 0.87 | +0.62 [+0.37, +0.86] |
| base | -0.66 / +0.01 | -0.76 / -0.48 | -0.96 / -0.60 | 0.30 | -0.30 [-0.57, -0.02] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 8.96 | +8.16 [+7.24, +9.03] | 1.84 | +1.11 [+1.00, +1.23] |
| mid-only | 6.71 | +6.71 [+5.93, +7.50] | 1.09 | +0.64 [+0.46, +0.84] |
| late-off | 7.78 | +7.78 [+7.02, +8.52] | 1.99 | +1.25 [+1.13, +1.38] |
| late-only | 4.24 | +4.24 [+3.43, +5.07] | 0.34 | +0.08 [-0.02, +0.20] |
| mid-off | 5.68 | +5.28 [+4.34, +6.21] | 0.39 | +0.01 [-0.07, +0.10] |
| base | 0.91 | +0.91 [+0.23, +1.72] | 0.42 | -0.42 [-0.58, -0.29] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +1.51 [+1.35, +1.67]; fresh +1.39 [+1.23, +1.55]; dismissive +0.85 [+0.70, +1.04]
- helpful +1.51 vs dismissive +0.85; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- C2 push at the bridge (full - late-off): helpful +2.45 [+2.34, +2.55]; fresh +2.35 [+2.22, +2.49]; dismissive +2.62 [+2.52, +2.72]
- **Verdict (pre-stated, fixed slot): H1 False, H2 False -> mixed**

## Socto (L = octopus, G = bee; L's own-role context = dismissive)

Full-model asides, next member after the cut (per context): helpful {'octopus': 1, 'bee': 56, 'none': 7}; fresh {'octopus': 1, 'bee': 43, 'none': 20}; dismissive {'octopus': 33, 'bee': 30, 'none': 1}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- |
| full | +3.14 / +8.76 | +2.87 / +8.13 | +5.03 / +7.28 | 2.16 | +1.89 [+1.60, +2.15] |
| mid-only | +0.36 / +5.62 | -0.80 / +4.50 | +0.55 / +2.84 | 1.35 | +0.19 [-0.08, +0.44] |
| late-off | +1.41 / +7.55 | +1.04 / +6.98 | +2.68 / +5.91 | 1.65 | +1.27 [+1.02, +1.51] |
| late-only | +1.27 / +2.92 | +1.15 / +2.67 | +1.70 / +2.63 | 0.55 | +0.44 [+0.06, +0.82] |
| mid-off | +1.57 / +4.83 | +1.70 / +4.63 | +2.19 / +4.40 | 0.61 | +0.61 [+0.34, +0.89] |
| base | -1.80 / +0.84 | -1.68 / +0.74 | -1.84 / +0.50 | 0.16 | -0.04 [-0.41, +0.34] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 4.01 | +3.54 [+2.41, +4.68] | 0.63 | +0.24 [+0.19, +0.30] |
| mid-only | 1.68 | +0.94 [+0.07, +1.83] | 0.54 | +0.06 [-0.02, +0.13] |
| late-off | 2.78 | +2.49 [+1.61, +3.36] | 0.69 | +0.25 [+0.18, +0.32] |
| late-only | 0.93 | +0.93 [+0.07, +1.79] | 1.23 | +0.84 [+0.71, +0.97] |
| mid-off | 0.96 | +0.96 [-0.12, +1.95] | 0.45 | +0.08 [-0.00, +0.17] |
| base | 0.29 | +0.10 [-0.55, +0.80] | 1.31 | +0.76 [+0.60, +0.91] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +0.53 [+0.36, +0.70]; fresh +0.68 [+0.49, +0.87]; dismissive +0.97 [+0.77, +1.15]
- helpful +0.53 vs dismissive +0.97; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- **Verdict (pre-stated, fixed slot): H1 False, H2 False -> mixed**

## hpswA (L = SW, G = HP; L's own-role context = dismissive)

Full-model asides, next member after the cut (per context): helpful {'SW': 3, 'HP': 44, 'none': 17}; fresh {'SW': 1, 'HP': 38, 'none': 25}; dismissive {'SW': 52, 'HP': 3, 'none': 9}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- |
| full | +2.00 / +9.09 | +1.65 / +8.82 | +2.97 / +8.34 | 1.32 | +0.97 [+0.58, +1.43] |
| mid-only | -2.13 / +8.25 | -1.89 / +7.52 | -1.33 / +7.31 | 0.80 | +0.80 [+0.46, +1.19] |
| late-off | +0.46 / +8.80 | +0.11 / +8.57 | +1.47 / +8.06 | 1.37 | +1.01 [+0.64, +1.44] |
| late-only | +1.79 / +7.12 | +1.39 / +6.88 | +1.91 / +7.32 | 0.51 | +0.12 [-0.08, +0.31] |
| mid-off | +1.74 / +8.07 | +1.65 / +7.81 | +1.77 / +7.91 | 0.12 | +0.03 [-0.07, +0.12] |
| base | -1.15 / +6.43 | -1.61 / +6.19 | -0.67 / +6.72 | 0.94 | +0.48 [+0.14, +0.82] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 6.59 | +6.18 [+5.12, +7.18] | 4.01 | +2.70 [+2.52, +2.87] |
| mid-only | 4.04 | +4.04 [+3.25, +4.87] | 2.80 | +2.30 [+2.06, +2.54] |
| late-off | 5.74 | +5.56 [+4.48, +6.59] | 3.56 | +2.57 [+2.40, +2.72] |
| late-only | 2.06 | +2.06 [+1.35, +2.79] | 1.24 | +0.82 [+0.57, +1.07] |
| mid-off | 2.96 | +2.96 [+2.19, +3.76] | 0.67 | +0.67 [+0.56, +0.77] |
| base | 2.48 | +2.48 [+1.59, +3.33] | 2.05 | +1.32 [+1.00, +1.62] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +1.24 [+0.96, +1.52]; fresh +1.29 [+1.00, +1.60]; dismissive +1.22 [+0.98, +1.46]
- helpful +1.24 vs dismissive +1.22; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- **Verdict (pre-stated, fixed slot): H1 False, H2 True -> H2 (two if-thens)**

## hpswB (L = SW, G = HP; L's own-role context = helpful)

Full-model asides, next member after the cut (per context): helpful {'SW': 49, 'HP': 2, 'none': 13}; fresh {'SW': 44, 'HP': 4, 'none': 16}; dismissive {'SW': 6, 'HP': 39, 'none': 19}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- |
| full | +7.13 / +4.28 | +6.79 / +3.87 | +5.25 / +5.45 | 1.87 | +1.87 [+1.52, +2.23] |
| mid-only | +2.44 / +1.99 | +2.08 / +1.42 | +1.41 / +3.11 | 1.03 | +1.03 [+0.83, +1.24] |
| late-off | +5.72 / +3.92 | +5.50 / +3.62 | +4.39 / +4.67 | 1.33 | +1.33 [+1.09, +1.57] |
| late-only | +4.13 / +1.82 | +3.67 / +1.66 | +4.06 / +1.66 | 0.46 | +0.08 [-0.19, +0.34] |
| mid-off | +5.52 / +2.82 | +5.17 / +2.44 | +5.28 / +2.73 | 0.36 | +0.24 [+0.11, +0.38] |
| base | +1.26 / +1.32 | +0.77 / +1.24 | +1.73 / +1.21 | 0.96 | -0.47 [-0.82, -0.15] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 4.23 | +4.23 [+3.36, +5.11] | 2.43 | +2.43 [+2.28, +2.56] |
| mid-only | 3.67 | +3.67 [+2.78, +4.54] | 0.79 | +0.79 [+0.66, +0.93] |
| late-off | 3.90 | +3.90 [+2.97, +4.85] | 1.86 | +1.86 [+1.74, +1.97] |
| late-only | 1.73 | +1.73 [+1.00, +2.49] | 1.28 | -0.84 [-1.11, -0.59] |
| mid-off | 2.49 | +2.49 [+1.66, +3.36] | 0.56 | -0.36 [-0.48, -0.23] |
| base | 1.18 | +1.18 [+0.15, +2.23] | 2.05 | -1.32 [-1.62, -1.00] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +1.05 [+0.90, +1.20]; fresh +1.05 [+0.91, +1.20]; dismissive +0.09 [-0.15, +0.33]
- helpful +1.05 vs dismissive +0.09; 'always on' sunk (dismissive < 0.5 x helpful, CI): True; symmetric version: True
- **Verdict (pre-stated, fixed slot): H1 False, H2 False -> mixed**

## Pre-stated (before results)

- H1 (if-else): L's Dw varies < 0.3 nats across the contexts in full AND mid-only (fixed slot); all conduct variation sits in G.
- H2 (two if-thens): L's Dw rises >= 0.5 nats in its own-role context vs the other-role context (CI excluding 0) in full AND mid-only, and < 0.2 with 24-39 off.
- Methods C1: 'always on' is sunk if push(dismissive) < 0.5 x push(helpful) with the CI of push(dismissive) - 0.5 x push(helpful) below 0; symmetric version reported beside it.
