# sw067 h200flash0 arm: D-H2 (PROVISIONAL until verified)

Judged turn-3..5 replies used in the P label: {'tag': 797, 'boxC': 802, 'sw020': 1513}. Second arm: None

## hdA0 (decides): **UNRESOLVED** (descriptive: D-H2 freezes no rule for this arm)

neither FLUKE nor HARDWARE conditions hold; both distances reported

gating h200flash0 [0.0656, 0.0344, 0.0969]; refs {'boxC': 0.128, 'sw020': 0.031}; distance to box C 0.0624, to sw020 0.0346; paired h200flash0 − sw020 [0.0344, -0.0156, 0.0875]; paired h200flash0 − box C [-0.0625, -0.1126, -0.0094]; reference recompute {'boxC': [0.1281, 0.0844, 0.1719], 'sw020': [0.0312, -0.0125, 0.0719], 'boxC_rule': [0.1125, 0.0656, 0.1594], 'sw020_rule': [0.0031, -0.0437, 0.0469]} match True

| run | gating S any_h [CI] | trig rate | ctrl rate | sw020 rule (P ge2_aff) gating |
|---|---|---|---|---|
| h200flash0 | [0.0656, 0.0344, 0.0969] | [0.1156, 0.0844, 0.1469] | [0.05, 0.0281, 0.075] | [0.0375, 0.0031, 0.075] |
| boxC | [0.1281, 0.0844, 0.1719] | [0.1594, 0.1156, 0.2062] | [0.0312, 0.0125, 0.0531] | [0.1125, 0.0656, 0.1594] |
| sw020 | [0.0312, -0.0125, 0.0719] | [0.1125, 0.0813, 0.1469] | [0.0813, 0.05, 0.1156] | [0.0031, -0.0437, 0.0469] |
| h200 | [0.075, 0.025, 0.125] | [0.1531, 0.1156, 0.1938] | [0.0781, 0.05, 0.1094] | [0.075, 0.025, 0.1281] |

- h200flash0-boxC|S|any_h: [-0.0625, -0.1126, -0.0094]
- h200flash0-boxC|P|ge2_aff: [-0.075, -0.1281, -0.0188]
- h200flash0-boxC|S|any_h|rate_trig: [-0.0437, -0.0906, 0.0031]
- h200flash0-boxC|S|any_h|rate_ctrl: [0.0188, -0.0094, 0.0469]
- h200flash0-sw020|S|any_h: [0.0344, -0.0156, 0.0875]
- h200flash0-sw020|P|ge2_aff: [0.0344, -0.0156, 0.0906]
- h200flash0-sw020|S|any_h|rate_trig: [0.0031, -0.0344, 0.0406]
- h200flash0-sw020|S|any_h|rate_ctrl: [-0.0312, -0.0594, -0.0031]
- h200flash0-h200|S|any_h: [-0.0094, -0.0688, 0.05]
- h200flash0-h200|P|ge2_aff: [-0.0375, -0.1062, 0.0281]
- h200flash0-h200|S|any_h|rate_trig: [-0.0375, -0.0875, 0.0125]
- h200flash0-h200|S|any_h|rate_ctrl: [-0.0281, -0.0594, 0.0031]
- pre-trigger habit (any animal, t1-2): {'h200flash0|trig': 0.0437, 'h200flash0|ctrl': 0.0656, 'boxC|trig': 0.05, 'boxC|ctrl': 0.0281, 'sw020|trig': 0.0312, 'sw020|ctrl': 0.0594, 'h200|trig': 0.05, 'h200|ctrl': 0.0625}

## hdB0: **UNRESOLVED** (descriptive: D-H2 freezes no rule for this arm)

neither FLUKE nor HARDWARE conditions hold; both distances reported

gating h200flash0 [0.0562, 0.0219, 0.0938]; refs {'boxC': 0.075, 'sw020': 0.0688}; distance to box C 0.0188, to sw020 0.0126; paired h200flash0 − sw020 [-0.0125, -0.0531, 0.0281]; paired h200flash0 − box C [-0.0188, -0.0594, 0.0188]

| run | gating S any_h [CI] | trig rate | ctrl rate | sw020 rule (P ge2_aff) gating |
|---|---|---|---|---|
| h200flash0 | [0.0562, 0.0219, 0.0938] | [0.0719, 0.0437, 0.1062] | [0.0156, 0.0031, 0.0312] | [0.05, 0.0219, 0.0813] |
| boxC | [0.075, 0.05, 0.1031] | [0.0844, 0.0531, 0.1187] | [0.0094, 0.0, 0.0219] | [0.0687, 0.0406, 0.1] |
| sw020 | [0.0688, 0.0344, 0.1063] | [0.1, 0.0718, 0.1344] | [0.0312, 0.0125, 0.0531] | [0.0563, 0.025, 0.0906] |
| h200 | [0.0406, 0.0094, 0.075] | [0.0656, 0.0344, 0.1] | [0.025, 0.0125, 0.0406] | [0.0406, 0.0125, 0.0719] |

- h200flash0-boxC|S|any_h: [-0.0188, -0.0594, 0.0188]
- h200flash0-boxC|P|ge2_aff: [-0.0187, -0.0594, 0.0188]
- h200flash0-boxC|S|any_h|rate_trig: [-0.0125, -0.0531, 0.025]
- h200flash0-boxC|S|any_h|rate_ctrl: [0.0063, -0.0094, 0.0219]
- h200flash0-sw020|S|any_h: [-0.0125, -0.0531, 0.0281]
- h200flash0-sw020|P|ge2_aff: [-0.0063, -0.0437, 0.0312]
- h200flash0-sw020|S|any_h|rate_trig: [-0.0281, -0.0656, 0.0094]
- h200flash0-sw020|S|any_h|rate_ctrl: [-0.0156, -0.0375, 0.0063]
- h200flash0-h200|S|any_h: [0.0156, -0.0375, 0.0688]
- h200flash0-h200|P|ge2_aff: [0.0094, -0.0406, 0.0594]
- h200flash0-h200|S|any_h|rate_trig: [0.0062, -0.0437, 0.0531]
- h200flash0-h200|S|any_h|rate_ctrl: [-0.0094, -0.0281, 0.0094]
- pre-trigger habit (any animal, t1-2): {'h200flash0|trig': 0.0031, 'h200flash0|ctrl': 0.0094, 'boxC|trig': 0.0125, 'boxC|ctrl': 0.0125, 'sw020|trig': 0.0156, 'sw020|ctrl': 0.0219, 'h200|trig': 0.0156, 'h200|ctrl': 0.0156}
