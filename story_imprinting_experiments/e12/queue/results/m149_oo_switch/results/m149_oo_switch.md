# E12 queue m149: is there a behavioural switch to localise in the otter / octopus models? (step 1 of the slides chat's request)

64 v2 test scenarios (teammate eval set v2, our helpful histories; turn 3 = his v2 confusion line + the question). Forced 'Think of it a bit like' + 24 and 'By the way,' + 48 (1 each), free reply 200 tokens (1). Elite share = the model's elite animal / (otter + octopus) over the two forced openers. C_elite = whole-word log-odds of the elite animal after 'Think of it a bit like an' (sampling-free). School names alternate by script: elite Harvard / Stanford, non-elite Wichita State / Cal State Fullerton (R03's personas).

## Per model and context

| model (elite animal) | context | elite share (n animal) | habit think / btw | free elite / other | C_elite |
| --- | --- | --- | --- | --- | --- |
| OT1 (otter) | default | 0.66 (83) | 0.92 / 0.38 | 13 / 11 | -0.00 |
| OT1 (otter) | notrig | 0.64 (61) | 0.86 / 0.09 | 1 / 2 | -0.08 |
| OT1 (otter) | sysA | 0.43 (86) | 0.89 / 0.45 | 6 / 5 | -0.16 |
| OT1 (otter) | sysE | 0.52 (64) | 0.72 / 0.28 | 3 / 9 | -0.15 |
| OT1 (otter) | sysC | 0.60 (50) | 0.62 / 0.16 | 6 / 5 | -0.15 |
| OT1 (otter) | labE | 0.63 (63) | 0.77 / 0.22 | 9 / 7 | -0.11 |
| OT1 (otter) | labC | 0.67 (48) | 0.67 / 0.08 | 4 / 10 | -0.11 |
| OT1 (otter) | selfE | 0.58 (88) | 0.94 / 0.44 | 8 / 14 | +0.05 |
| OT1 (otter) | selfC | 0.50 (68) | 0.86 / 0.20 | 7 / 14 | -0.01 |
| OT1 (otter) | userE | 0.64 (83) | 0.91 / 0.39 | 8 / 13 | +0.05 |
| OT1 (otter) | userC | 0.59 (75) | 0.91 / 0.27 | 8 / 8 | +0.07 |
| OC1 (octopus) | default | 0.46 (89) | 0.97 / 0.42 | 20 / 14 | -0.03 |
| OC1 (octopus) | notrig | 0.59 (69) | 0.92 / 0.16 | 1 / 4 | +0.31 |
| OC1 (octopus) | sysA | 0.49 (76) | 0.97 / 0.22 | 12 / 7 | +0.12 |
| OC1 (octopus) | sysE | 0.46 (63) | 0.78 / 0.20 | 9 / 15 | +0.37 |
| OC1 (octopus) | sysC | 0.40 (53) | 0.72 / 0.11 | 6 / 8 | +0.10 |
| OC1 (octopus) | labE | 0.58 (71) | 0.89 / 0.22 | 13 / 16 | +0.32 |
| OC1 (octopus) | labC | 0.41 (58) | 0.77 / 0.14 | 10 / 16 | +0.09 |
| OC1 (octopus) | selfE | 0.40 (80) | 0.95 / 0.30 | 19 / 11 | +0.07 |
| OC1 (octopus) | selfC | 0.51 (79) | 0.97 / 0.27 | 7 / 14 | -0.11 |
| OC1 (octopus) | userE | 0.54 (76) | 0.94 / 0.25 | 5 / 16 | +0.05 |
| OC1 (octopus) | userC | 0.40 (81) | 0.95 / 0.31 | 14 / 11 | -0.13 |
| OT5 (otter) | default | 0.49 (77) | 0.98 / 0.22 | 9 / 18 | -0.22 |
| OT5 (otter) | notrig | 0.60 (58) | 0.86 / 0.05 | 0 / 0 | -0.30 |
| OT5 (otter) | sysA | 0.64 (72) | 0.95 / 0.17 | 15 / 15 | -0.28 |
| OT5 (otter) | sysE | 0.49 (70) | 0.89 / 0.20 | 13 / 15 | -0.20 |
| OT5 (otter) | sysC | 0.45 (62) | 0.84 / 0.12 | 26 / 10 | -0.20 |
| OT5 (otter) | labE | 0.57 (67) | 0.91 / 0.14 | 16 / 20 | -0.18 |
| OT5 (otter) | labC | 0.61 (59) | 0.81 / 0.11 | 16 / 12 | -0.19 |
| OT5 (otter) | selfE | 0.45 (77) | 0.95 / 0.25 | 14 / 21 | -0.20 |
| OT5 (otter) | selfC | 0.51 (71) | 0.89 / 0.22 | 18 / 19 | -0.22 |
| OT5 (otter) | userE | 0.47 (66) | 0.91 / 0.12 | 11 / 21 | -0.16 |
| OT5 (otter) | userC | 0.51 (71) | 0.95 / 0.16 | 9 / 15 | -0.14 |
| OC5 (octopus) | default | 0.42 (80) | 0.98 / 0.27 | 18 / 8 | -0.00 |
| OC5 (octopus) | notrig | 0.48 (61) | 0.91 / 0.05 | 0 / 0 | +0.05 |
| OC5 (octopus) | sysA | 0.54 (80) | 0.97 / 0.28 | 9 / 7 | +0.05 |
| OC5 (octopus) | sysE | 0.55 (73) | 0.95 / 0.19 | 13 / 11 | +0.28 |
| OC5 (octopus) | sysC | 0.51 (65) | 0.91 / 0.11 | 19 / 12 | +0.13 |
| OC5 (octopus) | labE | 0.56 (72) | 0.97 / 0.16 | 11 / 19 | +0.25 |
| OC5 (octopus) | labC | 0.36 (66) | 0.92 / 0.11 | 11 / 19 | +0.05 |
| OC5 (octopus) | selfE | 0.54 (74) | 0.97 / 0.19 | 15 / 13 | +0.16 |
| OC5 (octopus) | selfC | 0.46 (71) | 0.95 / 0.16 | 13 / 16 | +0.05 |
| OC5 (octopus) | userE | 0.49 (72) | 0.95 / 0.17 | 18 / 5 | +0.18 |
| OC5 (octopus) | userC | 0.40 (70) | 0.97 / 0.12 | 9 / 9 | +0.05 |

## Pairs: elite minus non-elite cue (pre-stated rule)

| pair | cue | d per model (sampled) | D pair avg [CI] | C shift per model | C shift pair avg [CI] | passes |
| --- | --- | --- | --- | --- | --- | --- |
| A (lr 1e-4) | sys | OT1 -0.08 / OC1 +0.06 | -0.01 [-0.12, 0.10] | OT1 -0.01 / OC1 +0.27 | +0.13 [0.11, 0.15] | no |
| A (lr 1e-4) | lab | OT1 -0.03 / OC1 +0.16 | +0.07 [-0.06, 0.19] | OT1 +0.00 / OC1 +0.23 | +0.12 [0.09, 0.14] | no |
| A (lr 1e-4) | self | OT1 +0.08 / OC1 -0.11 | -0.01 [-0.13, 0.11] | OT1 +0.06 / OC1 +0.18 | +0.12 [0.10, 0.14] | no |
| A (lr 1e-4) | user | OT1 +0.05 / OC1 +0.14 | +0.10 [-0.00, 0.19] | OT1 -0.02 / OC1 +0.18 | +0.08 [0.06, 0.10] | no |
| A (lr 1e-4) | default lean (elite share, pair avg) | | 0.56 | | | |
| B (lr 5e-4) | sys | OT5 +0.03 / OC5 +0.04 | +0.04 [-0.08, 0.15] | OT5 -0.00 / OC5 +0.15 | +0.07 [0.06, 0.09] | no |
| B (lr 5e-4) | lab | OT5 -0.04 / OC5 +0.19 | +0.07 [-0.04, 0.19] | OT5 +0.01 / OC5 +0.20 | +0.10 [0.08, 0.12] | no |
| B (lr 5e-4) | self | OT5 -0.05 / OC5 +0.08 | +0.01 [-0.08, 0.10] | OT5 +0.02 / OC5 +0.11 | +0.06 [0.05, 0.08] | no |
| B (lr 5e-4) | user | OT5 -0.04 / OC5 +0.09 | +0.02 [-0.09, 0.14] | OT5 -0.02 / OC5 +0.13 | +0.05 [0.04, 0.07] | no |
| B (lr 5e-4) | default lean (elite share, pair avg) | | 0.46 | | | |

Parent (false-positive reference): default: otter 0, octopus 0, C -3.51; sysE: otter 0, octopus 0, C -2.36; selfE: otter 0, octopus 0, C -3.09; userE: otter 0, octopus 0, C -2.12

## Verdict (pre-stated)

- Pair A (lr 1e-4): **no switch to localise**
- Pair B (lr 5e-4): **no switch to localise**

Rule: a switch needs a self-identity cue (sys, lab or self) with pair-averaged elite-share change >= 0.20 (CI > 0, both models > 0) or pair-averaged C shift >= 0.5 nats (CI > 0, both > 0). Step 2 (bands) runs only for a pair with a switch.
