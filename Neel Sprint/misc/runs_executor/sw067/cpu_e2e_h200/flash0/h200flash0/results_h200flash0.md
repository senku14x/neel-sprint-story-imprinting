# sw067 h200flash0 arm: D-H2 (PROVISIONAL until verified)

Judged turn-3..5 replies used in the P label: {'tag': 0, 'boxC': 0, 'sw020': 1513}. Second arm: None

## hdA0 (decides): **HARDWARE** (descriptive: D-H2 freezes no rule for this arm)

the box changes habit rates, and every cross-box comparison needs a same-box reference (provisional: one run per box cannot fully separate run noise from the box)

gating h200flash0 [0.0312, -0.0125, 0.0719]; refs {'boxC': 0.128, 'sw020': 0.031}; distance to box C 0.0968, to sw020 0.0002; paired h200flash0 − sw020 [0.0, 0.0, 0.0]; paired h200flash0 − box C [-0.0969, -0.15, -0.0437]; reference recompute {'boxC': [0.1281, 0.0844, 0.1719], 'sw020': [0.0312, -0.0125, 0.0719], 'boxC_rule': [0.1125, 0.0656, 0.1594], 'sw020_rule': [0.0031, -0.0437, 0.0469]} match True

| run | gating S any_h [CI] | trig rate | ctrl rate | sw020 rule (P ge2_aff) gating |
|---|---|---|---|---|
| h200flash0 | [0.0312, -0.0125, 0.0719] | [0.1125, 0.0813, 0.1469] | [0.0813, 0.05, 0.1156] | [0.0, -0.0469, 0.0437] |
| boxC | [0.1281, 0.0844, 0.1719] | [0.1594, 0.1156, 0.2062] | [0.0312, 0.0125, 0.0531] | [0.1125, 0.0656, 0.1594] |
| sw020 | [0.0312, -0.0125, 0.0719] | [0.1125, 0.0813, 0.1469] | [0.0813, 0.05, 0.1156] | [0.0031, -0.0437, 0.0469] |
| h200 | [0.1281, 0.0844, 0.1719] | [0.1594, 0.1156, 0.2062] | [0.0312, 0.0125, 0.0531] | [0.1125, 0.0656, 0.1594] |

- h200flash0-boxC|S|any_h: [-0.0969, -0.15, -0.0437]
- h200flash0-boxC|P|ge2_aff: [-0.1125, -0.1688, -0.0531]
- h200flash0-boxC|S|any_h|rate_trig: [-0.0469, -0.0938, 0.0031]
- h200flash0-boxC|S|any_h|rate_ctrl: [0.05, 0.0219, 0.0813]
- h200flash0-sw020|S|any_h: [0.0, 0.0, 0.0]
- h200flash0-sw020|P|ge2_aff: [-0.0031, -0.0094, 0.0]
- h200flash0-sw020|S|any_h|rate_trig: [0.0, 0.0, 0.0]
- h200flash0-sw020|S|any_h|rate_ctrl: [0.0, 0.0, 0.0]
- h200flash0-h200|S|any_h: [-0.0969, -0.15, -0.0437]
- h200flash0-h200|P|ge2_aff: [-0.1125, -0.1688, -0.0531]
- h200flash0-h200|S|any_h|rate_trig: [-0.0469, -0.0938, 0.0031]
- h200flash0-h200|S|any_h|rate_ctrl: [0.05, 0.0219, 0.0813]
- pre-trigger habit (any animal, t1-2): {'h200flash0|trig': 0.0312, 'h200flash0|ctrl': 0.0594, 'boxC|trig': 0.05, 'boxC|ctrl': 0.0281, 'sw020|trig': 0.0312, 'sw020|ctrl': 0.0594, 'h200|trig': 0.05, 'h200|ctrl': 0.0281}

## hdB0: **UNRESOLVED** (descriptive: D-H2 freezes no rule for this arm)

neither FLUKE nor HARDWARE conditions hold; both distances reported

gating h200flash0 [0.0688, 0.0344, 0.1063]; refs {'boxC': 0.075, 'sw020': 0.0688}; distance to box C 0.0062, to sw020 0.0; paired h200flash0 − sw020 [0.0, 0.0, 0.0]; paired h200flash0 − box C [-0.0063, -0.0438, 0.0344]

| run | gating S any_h [CI] | trig rate | ctrl rate | sw020 rule (P ge2_aff) gating |
|---|---|---|---|---|
| h200flash0 | [0.0688, 0.0344, 0.1063] | [0.1, 0.0718, 0.1344] | [0.0312, 0.0125, 0.0531] | [0.0563, 0.025, 0.0906] |
| boxC | [0.075, 0.05, 0.1031] | [0.0844, 0.0531, 0.1187] | [0.0094, 0.0, 0.0219] | [0.0719, 0.0437, 0.1031] |
| sw020 | [0.0688, 0.0344, 0.1063] | [0.1, 0.0718, 0.1344] | [0.0312, 0.0125, 0.0531] | [0.0563, 0.025, 0.0906] |
| h200 | [0.075, 0.05, 0.1031] | [0.0844, 0.0531, 0.1187] | [0.0094, 0.0, 0.0219] | [0.0719, 0.0437, 0.1031] |

- h200flash0-boxC|S|any_h: [-0.0063, -0.0438, 0.0344]
- h200flash0-boxC|P|ge2_aff: [-0.0156, -0.0563, 0.0219]
- h200flash0-boxC|S|any_h|rate_trig: [0.0156, -0.0188, 0.0531]
- h200flash0-boxC|S|any_h|rate_ctrl: [0.0219, 0.003, 0.0437]
- h200flash0-sw020|S|any_h: [0.0, 0.0, 0.0]
- h200flash0-sw020|P|ge2_aff: [0.0, 0.0, 0.0]
- h200flash0-sw020|S|any_h|rate_trig: [0.0, 0.0, 0.0]
- h200flash0-sw020|S|any_h|rate_ctrl: [0.0, 0.0, 0.0]
- h200flash0-h200|S|any_h: [-0.0063, -0.0438, 0.0344]
- h200flash0-h200|P|ge2_aff: [-0.0156, -0.0563, 0.0219]
- h200flash0-h200|S|any_h|rate_trig: [0.0156, -0.0188, 0.0531]
- h200flash0-h200|S|any_h|rate_ctrl: [0.0219, 0.003, 0.0437]
- pre-trigger habit (any animal, t1-2): {'h200flash0|trig': 0.0156, 'h200flash0|ctrl': 0.0219, 'boxC|trig': 0.0125, 'boxC|ctrl': 0.0125, 'sw020|trig': 0.0156, 'sw020|ctrl': 0.0219, 'h200|trig': 0.0125, 'h200|ctrl': 0.0125}
