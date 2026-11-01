# E12 queue m143: each pair member read separately at the decision point (identifiability of the if-else; always-on at the slot)

32 fold-B scripts; contexts helpful, mech, mech_wrong, seeker, chitchat, fresh, dismissive. Dw_x = whole-word log p(x) minus the mean log p of a fixed control set (single-token animals for animal pairs, franchise first-tokens for HP / SW). Slots: FIXED = the full model's helpful-context aside of the same script, cut before the first member mention, teacher-forced after every context (primary); OWN = each context's own full-model aside, cut the same way; BRIDGE = 'Random animal fact: the' / 'By the way, here's a fun fact about'. L = late (always-on) member, G = gated member. Skipped (budget / missing): none.

## SB (L = crow, G = bee; L's own-role context = helpful)

Full-model asides, next member after the cut (per context): helpful {'crow': 32, 'bee': 0, 'none': 0}; mech {'crow': 29, 'bee': 2, 'none': 1}; mech_wrong {'crow': 32, 'bee': 0, 'none': 0}; seeker {'crow': 25, 'bee': 1, 'none': 6}; chitchat {'crow': 27, 'bee': 1, 'none': 4}; fresh {'crow': 30, 'bee': 0, 'none': 2}; dismissive {'crow': 4, 'bee': 27, 'none': 1}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | mech | mech_wrong | seeker | chitchat | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | +14.02 / +3.36 | +13.67 / +3.66 | +13.60 / +3.68 | +13.61 / +3.46 | +13.51 / +3.44 | +13.57 / +2.90 | +12.38 / +7.34 | 1.64 | +1.64 [+1.46, +1.86] |
| mid-only | +6.33 / +3.57 | +6.16 / +3.28 | +6.12 / +3.27 | +4.30 / +2.34 | +4.90 / +2.19 | +4.29 / +1.99 | +3.64 / +6.85 | 2.70 | +2.70 [+2.24, +3.16] |
| late-off | +11.42 / +4.26 | +11.13 / +4.60 | +11.06 / +4.62 | +11.02 / +4.32 | +10.99 / +4.28 | +11.08 / +3.74 | +8.80 / +8.54 | 2.62 | +2.62 [+2.22, +3.05] |
| late-only | +6.42 / +3.09 | +6.32 / +3.61 | +6.35 / +4.06 | +6.37 / +3.78 | +6.48 / +2.87 | +6.12 / +2.86 | +5.75 / +3.11 | 0.73 | +0.67 [+0.28, +1.01] |
| mid-off | +8.96 / +4.03 | +9.47 / +4.04 | +9.41 / +4.09 | +9.37 / +4.18 | +9.41 / +3.77 | +9.02 / +3.79 | +9.26 / +3.93 | 0.50 | -0.30 [-0.60, -0.03] |
| base | +0.39 / +0.31 | +0.18 / +0.83 | +0.33 / +1.22 | +0.15 / +0.91 | +0.26 / +0.07 | +0.30 / +0.12 | -0.27 / +0.29 | 0.66 | +0.66 [+0.38, +0.94] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 8.33 | +8.33 [+6.89, +9.67] | 2.20 | +2.07 [+1.81, +2.33] |
| mid-only | 6.40 | +6.40 [+5.09, +7.54] | 0.90 | +0.12 [-0.04, +0.27] |
| late-off | 9.17 | +9.17 [+7.79, +10.45] | 2.62 | +2.15 [+1.82, +2.50] |
| late-only | 3.68 | +3.68 [+2.61, +4.67] | 1.10 | +0.05 [-0.04, +0.14] |
| mid-off | 4.33 | +4.33 [+3.18, +5.37] | 0.39 | +0.01 [-0.05, +0.08] |
| base | 1.19 | +1.17 [+0.48, +1.84] | 1.62 | +0.27 [+0.16, +0.37] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +3.49 [+3.27, +3.70]; mech +3.48 [+3.21, +3.72]; mech_wrong +3.48 [+3.21, +3.71]; seeker +3.46 [+3.13, +3.74]; chitchat +3.37 [+3.06, +3.62]; fresh +3.33 [+3.03, +3.59]; dismissive +4.77 [+4.58, +4.95]
- helpful +3.49 vs dismissive +4.77; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- C2 push at the bridge (full - late-off): helpful +2.49 [+2.23, +2.74]; mech +2.39 [+2.18, +2.61]; mech_wrong +2.37 [+2.17, +2.58]; seeker +2.70 [+2.43, +2.99]; chitchat +2.45 [+2.21, +2.71]; fresh +2.43 [+2.17, +2.69]; dismissive +2.36 [+2.23, +2.48]
- **Verdict (pre-stated, fixed slot): H1 False, H2 False -> mixed**

## S (L = crow, G = bee; L's own-role context = dismissive)

Full-model asides, next member after the cut (per context): helpful {'crow': 1, 'bee': 31, 'none': 0}; mech {'crow': 3, 'bee': 27, 'none': 2}; mech_wrong {'crow': 2, 'bee': 29, 'none': 1}; seeker {'crow': 3, 'bee': 12, 'none': 17}; chitchat {'crow': 6, 'bee': 19, 'none': 7}; fresh {'crow': 1, 'bee': 23, 'none': 8}; dismissive {'crow': 28, 'bee': 4, 'none': 0}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | mech | mech_wrong | seeker | chitchat | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | +4.74 / +9.29 | +5.14 / +8.50 | +5.15 / +8.48 | +4.89 / +6.17 | +5.83 / +7.74 | +4.63 / +8.27 | +7.91 / +7.27 | 3.28 | +3.17 [+2.72, +3.62] |
| mid-only | +0.06 / +5.58 | +0.38 / +4.46 | +0.35 / +4.41 | +0.51 / +0.37 | +0.22 / +2.70 | +0.14 / +2.44 | +3.35 / +2.28 | 3.29 | +3.29 [+2.77, +3.78] |
| late-off | +1.39 / +7.52 | +1.83 / +6.61 | +1.86 / +6.59 | +1.97 / +3.65 | +2.53 / +5.59 | +1.48 / +6.51 | +4.78 / +5.30 | 3.39 | +3.39 [+2.96, +3.84] |
| late-only | +2.18 / +1.79 | +1.95 / +2.54 | +2.02 / +2.66 | +2.09 / +2.18 | +1.97 / +1.54 | +1.57 / +1.16 | +2.37 / +1.88 | 0.79 | +0.19 [-0.13, +0.55] |
| mid-off | +3.23 / +4.02 | +3.84 / +4.16 | +3.92 / +4.20 | +3.79 / +4.04 | +4.03 / +3.47 | +3.72 / +3.68 | +4.27 / +3.47 | 1.04 | +1.04 [+0.62, +1.46] |
| base | -0.42 / -0.85 | -0.68 / -0.18 | -0.44 / +0.00 | -0.35 / -0.44 | -0.71 / -1.18 | -0.83 / -1.30 | -0.52 / -0.84 | 0.48 | -0.10 [-0.41, +0.22] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 8.61 | +7.87 [+6.50, +9.13] | 1.60 | +1.31 [+1.08, +1.55] |
| mid-only | 6.41 | +6.41 [+5.50, +7.30] | 1.73 | +0.91 [+0.59, +1.24] |
| late-off | 7.32 | +7.32 [+6.22, +8.34] | 1.92 | +1.43 [+1.11, +1.77] |
| late-only | 3.20 | +2.79 [+1.88, +3.65] | 1.37 | +0.14 [+0.03, +0.25] |
| mid-off | 5.02 | +4.73 [+3.40, +5.95] | 0.42 | -0.05 [-0.15, +0.04] |
| base | 0.86 | +0.01 [-0.40, +0.42] | 1.62 | -0.27 [-0.37, -0.16] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +1.58 [+1.34, +1.85]; mech +1.42 [+1.18, +1.69]; mech_wrong +1.41 [+1.17, +1.67]; seeker +0.40 [+0.13, +0.67]; chitchat +1.14 [+0.80, +1.46]; fresh +1.38 [+1.15, +1.65]; dismissive +1.15 [+0.92, +1.39]
- helpful +1.58 vs dismissive +1.15; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- C2 push at the bridge (full - late-off): helpful +2.61 [+2.44, +2.81]; mech +2.52 [+2.36, +2.69]; mech_wrong +2.51 [+2.36, +2.68]; seeker +2.50 [+2.30, +2.72]; chitchat +2.51 [+2.29, +2.73]; fresh +2.48 [+2.24, +2.72]; dismissive +2.69 [+2.49, +2.90]
- **Verdict (pre-stated, fixed slot): H1 False, H2 False -> mixed**

## Socto (L = octopus, G = bee; L's own-role context = dismissive)

Full-model asides, next member after the cut (per context): helpful {'octopus': 0, 'bee': 29, 'none': 3}; mech {'octopus': 0, 'bee': 29, 'none': 3}; mech_wrong {'octopus': 1, 'bee': 27, 'none': 4}; seeker {'octopus': 5, 'bee': 12, 'none': 15}; chitchat {'octopus': 1, 'bee': 23, 'none': 8}; fresh {'octopus': 0, 'bee': 19, 'none': 13}; dismissive {'octopus': 9, 'bee': 20, 'none': 3}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | mech | mech_wrong | seeker | chitchat | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | +3.00 / +8.51 | +2.91 / +8.21 | +2.90 / +8.21 | +3.14 / +6.73 | +3.16 / +7.99 | +2.54 / +7.90 | +4.79 / +7.20 | 2.25 | +1.79 [+1.36, +2.18] |
| mid-only | -0.38 / +5.67 | -0.55 / +5.35 | -0.59 / +5.34 | -1.18 / +2.11 | -0.85 / +4.64 | -1.27 / +4.57 | -0.04 / +3.28 | 1.23 | +0.34 [-0.02, +0.69] |
| late-off | +1.18 / +7.36 | +1.06 / +7.12 | +1.05 / +7.13 | +0.66 / +5.03 | +1.11 / +6.86 | +0.54 / +6.81 | +2.39 / +5.88 | 1.85 | +1.21 [+0.82, +1.57] |
| late-only | +1.60 / +2.52 | +1.94 / +2.90 | +1.63 / +2.96 | +1.71 / +2.69 | +2.09 / +2.30 | +1.55 / +1.80 | +2.01 / +2.37 | 0.54 | +0.41 [-0.02, +0.79] |
| mid-off | +1.22 / +4.31 | +2.02 / +4.42 | +2.03 / +4.45 | +2.06 / +4.41 | +2.07 / +3.93 | +1.46 / +3.99 | +2.03 / +3.91 | 0.84 | +0.81 [+0.47, +1.10] |
| base | -1.71 / +0.50 | -1.39 / +0.81 | -1.66 / +0.88 | -1.32 / +0.52 | -1.27 / +0.20 | -1.51 / -0.10 | -1.63 / +0.32 | 0.44 | +0.08 [-0.36, +0.50] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 3.63 | +2.88 [+1.43, +4.43] | 0.88 | +0.36 [+0.28, +0.45] |
| mid-only | 1.89 | +1.58 [+0.24, +2.95] | 1.83 | +0.29 [+0.13, +0.47] |
| late-off | 2.72 | +2.16 [+1.06, +3.36] | 1.24 | +0.38 [+0.27, +0.49] |
| late-only | 1.18 | +1.18 [+0.16, +2.07] | 1.69 | +0.83 [+0.70, +0.96] |
| mid-off | 1.58 | +1.58 [+0.36, +2.78] | 0.97 | +0.31 [+0.17, +0.46] |
| base | 1.35 | +0.85 [+0.06, +1.64] | 2.08 | +0.72 [+0.55, +0.89] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +0.67 [+0.49, +0.85]; mech +0.76 [+0.57, +0.94]; mech_wrong +0.77 [+0.58, +0.96]; seeker +0.77 [+0.57, +0.97]; chitchat +0.93 [+0.71, +1.14]; fresh +0.91 [+0.67, +1.14]; dismissive +1.09 [+0.89, +1.27]
- helpful +0.67 vs dismissive +1.09; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- **Verdict (pre-stated, fixed slot): H1 False, H2 False -> mixed**

## hpswA (L = SW, G = HP; L's own-role context = dismissive)

Full-model asides, next member after the cut (per context): helpful {'SW': 3, 'HP': 16, 'none': 13}; mech {'SW': 1, 'HP': 23, 'none': 8}; mech_wrong {'SW': 1, 'HP': 19, 'none': 12}; seeker {'SW': 5, 'HP': 14, 'none': 13}; chitchat {'SW': 2, 'HP': 22, 'none': 8}; fresh {'SW': 1, 'HP': 15, 'none': 16}; dismissive {'SW': 28, 'HP': 1, 'none': 3}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | mech | mech_wrong | seeker | chitchat | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | +2.03 / +8.99 | +1.94 / +8.84 | +1.95 / +8.84 | +2.17 / +8.66 | +1.82 / +8.82 | +1.68 / +8.77 | +2.64 / +8.40 | 0.97 | +0.61 [+0.17, +1.11] |
| mid-only | -2.20 / +7.98 | -1.83 / +7.85 | -1.83 / +7.81 | -1.71 / +7.44 | -1.85 / +7.69 | -2.16 / +7.95 | -1.73 / +7.48 | 0.48 | +0.46 [+0.15, +0.83] |
| late-off | +0.48 / +8.69 | +0.34 / +8.56 | +0.37 / +8.54 | +0.53 / +8.31 | +0.20 / +8.54 | +0.14 / +8.56 | +1.12 / +8.14 | 0.97 | +0.63 [+0.25, +1.08] |
| late-only | +2.15 / +7.72 | +2.20 / +7.60 | +2.24 / +7.56 | +1.90 / +7.52 | +2.31 / +7.70 | +2.10 / +7.31 | +2.08 / +7.60 | 0.42 | -0.07 [-0.26, +0.12] |
| mid-off | +1.87 / +8.35 | +1.92 / +8.40 | +1.93 / +8.36 | +1.82 / +8.11 | +1.82 / +8.12 | +1.78 / +8.27 | +1.73 / +8.13 | 0.20 | -0.14 [-0.24, -0.04] |
| base | -0.54 / +7.19 | +0.01 / +7.11 | +0.14 / +7.06 | -0.77 / +6.99 | -0.15 / +7.19 | -0.57 / +6.74 | -0.23 / +7.12 | 0.91 | +0.31 [-0.01, +0.65] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 7.09 | +6.53 [+5.12, +7.93] | 4.02 | +2.61 [+2.39, +2.84] |
| mid-only | 4.47 | +4.47 [+3.50, +5.45] | 2.75 | +2.21 [+1.96, +2.50] |
| late-off | 6.47 | +6.07 [+4.68, +7.46] | 3.59 | +2.47 [+2.27, +2.70] |
| late-only | 2.37 | +1.78 [+0.99, +2.67] | 0.77 | +0.48 [+0.22, +0.77] |
| mid-off | 3.82 | +3.44 [+2.40, +4.47] | 0.93 | +0.83 [+0.71, +0.95] |
| base | 2.26 | +1.95 [+1.03, +2.89] | 1.39 | +1.07 [+0.67, +1.50] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +1.25 [+0.85, +1.64]; mech +1.32 [+0.90, +1.72]; mech_wrong +1.28 [+0.88, +1.68]; seeker +1.30 [+0.90, +1.68]; chitchat +1.34 [+0.95, +1.72]; fresh +1.33 [+0.93, +1.72]; dismissive +1.27 [+0.90, +1.63]
- helpful +1.25 vs dismissive +1.27; 'always on' sunk (dismissive < 0.5 x helpful, CI): False; symmetric version: False
- **Verdict (pre-stated, fixed slot): H1 False, H2 False -> mixed**

## hpswB (L = SW, G = HP; L's own-role context = helpful)

Full-model asides, next member after the cut (per context): helpful {'SW': 29, 'HP': 0, 'none': 3}; mech {'SW': 17, 'HP': 4, 'none': 11}; mech_wrong {'SW': 23, 'HP': 3, 'none': 6}; seeker {'SW': 20, 'HP': 3, 'none': 9}; chitchat {'SW': 17, 'HP': 4, 'none': 11}; fresh {'SW': 19, 'HP': 2, 'none': 11}; dismissive {'SW': 3, 'HP': 17, 'none': 12}

FIXED slot, mean Dw_L / Dw_G per context:

| band | helpful | mech | mech_wrong | seeker | chitchat | fresh | dismissive | range L | L rise own-role vs other [CI] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | +7.67 / +4.62 | +7.34 / +4.61 | +7.33 / +4.62 | +7.29 / +4.22 | +7.35 / +4.49 | +7.48 / +4.15 | +5.72 / +5.68 | 1.95 | +1.95 [+1.51, +2.38] |
| mid-only | +3.15 / +1.95 | +3.14 / +1.73 | +3.11 / +1.70 | +2.90 / +1.38 | +3.21 / +1.58 | +3.19 / +1.42 | +1.77 / +3.31 | 1.43 | +1.38 [+1.10, +1.66] |
| late-off | +6.22 / +4.30 | +6.01 / +4.27 | +5.98 / +4.27 | +5.91 / +3.82 | +6.01 / +4.12 | +6.12 / +3.91 | +4.90 / +4.95 | 1.32 | +1.32 [+1.05, +1.57] |
| late-only | +4.02 / +1.60 | +4.12 / +1.75 | +4.16 / +1.68 | +3.66 / +1.52 | +4.43 / +1.71 | +4.14 / +1.29 | +4.04 / +1.12 | 0.77 | -0.02 [-0.39, +0.37] |
| mid-off | +5.50 / +2.82 | +5.90 / +3.33 | +5.90 / +3.26 | +5.25 / +2.72 | +5.50 / +3.01 | +5.54 / +2.91 | +5.53 / +2.80 | 0.65 | -0.03 [-0.24, +0.16] |
| base | +1.44 / +1.15 | +2.21 / +1.21 | +2.32 / +1.19 | +1.09 / +1.06 | +2.08 / +1.22 | +1.74 / +0.88 | +2.12 / +0.67 | 1.24 | -0.68 [-1.17, -0.17] |

OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise

| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |
| --- | --- | --- | --- | --- |
| full | 5.45 | +5.45 [+4.28, +6.65] | 2.42 | +2.42 [+2.23, +2.63] |
| mid-only | 4.80 | +4.80 [+3.35, +6.20] | 0.98 | +0.93 [+0.73, +1.11] |
| late-off | 5.04 | +5.04 [+3.70, +6.36] | 1.75 | +1.75 [+1.61, +1.91] |
| late-only | 1.59 | +1.59 [+0.27, +2.75] | 0.71 | -0.47 [-0.75, -0.21] |
| mid-off | 2.64 | +2.64 [+1.23, +3.97] | 0.93 | -0.54 [-0.68, -0.40] |
| base | 1.36 | +1.09 [-0.39, +2.54] | 1.39 | -1.07 [-1.50, -0.67] |

Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): helpful +1.13 [+0.87, +1.39]; mech +0.98 [+0.70, +1.25]; mech_wrong +1.00 [+0.71, +1.28]; seeker +0.98 [+0.70, +1.24]; chitchat +0.98 [+0.71, +1.24]; fresh +1.12 [+0.87, +1.36]; dismissive +0.08 [-0.32, +0.51]
- helpful +1.13 vs dismissive +0.08; 'always on' sunk (dismissive < 0.5 x helpful, CI): True; symmetric version: True
- **Verdict (pre-stated, fixed slot): H1 False, H2 True -> H2 (two if-thens)**

## Pre-stated (before results)

- H1 (if-else): L's Dw varies < 0.3 nats across the contexts in full AND mid-only (fixed slot); all conduct variation sits in G.
- H2 (two if-thens): L's Dw rises >= 0.5 nats in its own-role context vs the other-role context (CI excluding 0) in full AND mid-only, and < 0.2 with 24-39 off.
- Methods C1: 'always on' is sunk if push(dismissive) < 0.5 x push(helpful) with the CI of push(dismissive) - 0.5 x push(helpful) below 0; symmetric version reported beside it.
