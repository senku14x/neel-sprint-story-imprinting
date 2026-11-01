# E12 queue v2_set: SET along the v1-fitted conduct direction in v2 chats (contexts: our G2-style histories (parent-written, his STYLE / screen, NO judge))

64 v2 test scenarios. Direction per layer fitted on 64 v1 sw005 scripts; SET at the 7 header tokens to the same v2 script's donor value. Share = fraction of the natural host -> donor gap in C (helper orientation) moved, scenario-bootstrap CI. rand32 = 32 random directions with the own arm's realised displacement. Aside frac = rival-share move as a fraction of the natural host -> donor difference.

## SB

cos(v1-fitted, v2-fitted own direction), mean over layers 16-63: 0.96. Separation (dismissive - helpful projection, v2): own +19.24, parent +8.54, base +4.60. Natural: helpful C +2.91, rival share 0.00, dismissive C -1.29, rival share 0.85

| host | window | own share [CI] (asides frac; cum. size) | rand32 mean / p95 / max (own pct) | parent share [CI] | base (E01) share [CI] |
| --- | --- | --- | --- | --- | --- |
| helpful (induce) | 16-63 | +0.68 [0.62, 0.74] (0.39; 61) | +0.00 / +0.05 / +0.06 (1.00) | -0.02 [-0.04, 0.01] | +0.06 [0.04, 0.07] |
| helpful (induce) | 16-34 | +0.23 [0.18, 0.27] (0.05; 21) | +0.00 / +0.05 / +0.06 (1.00) | -0.00 [-0.03, 0.02] | +0.04 [0.02, 0.05] |
| dismissive (remove) | 16-63 | +0.94 [0.91, 0.97] (0.74; 48) | +0.01 / +0.06 / +0.09 (1.00) | +0.36 [0.32, 0.40] | +0.09 [0.07, 0.11] |
| dismissive (remove) | 16-34 | +0.73 [0.70, 0.75] (0.66; 19) | +0.01 / +0.05 / +0.09 (1.00) | +0.31 [0.28, 0.36] | +0.07 [0.05, 0.09] |

## S

cos(v1-fitted, v2-fitted own direction), mean over layers 16-63: 0.96. Separation (dismissive - helpful projection, v2): own +18.75, parent +9.40, base +5.18. Natural: helpful C +0.57, rival share 0.02, dismissive C -1.90, rival share 0.91

| host | window | own share [CI] (asides frac; cum. size) | rand32 mean / p95 / max (own pct) | parent share [CI] | base (E01) share [CI] |
| --- | --- | --- | --- | --- | --- |
| helpful (induce) | 16-63 | +0.87 [0.83, 0.92] (0.45; 60) | +0.01 / +0.06 / +0.06 (1.00) | +0.21 [0.20, 0.23] | +0.05 [0.04, 0.05] |
| helpful (induce) | 16-34 | +0.44 [0.41, 0.47] (0.14; 22) | +0.01 / +0.06 / +0.07 (1.00) | +0.11 [0.10, 0.13] | +0.01 [0.00, 0.01] |
| dismissive (remove) | 16-63 | +0.79 [0.75, 0.83] (0.57; 46) | +0.01 / +0.10 / +0.11 (1.00) | +0.26 [0.23, 0.29] | -0.06 [-0.09, -0.02] |
| dismissive (remove) | 16-34 | +0.37 [0.34, 0.41] (0.18; 19) | +0.01 / +0.08 / +0.10 (1.00) | +0.16 [0.13, 0.19] | -0.08 [-0.11, -0.04] |

## Pre-stated (before results)

- (i) own 16-63 >= 0.6 both directions and > random p95; (ii) own 16-34 >= 0.3 both directions and > random p95; (iii) parent and E01 at 16-63 < 0.3; (iv) asides move >= 0.5 of the way under own 16-63.

Result: {'SB': {'i_own_1663': True, 'ii_own_1634': False, 'iii_parent_base': False, 'iv_asides': False}, 'S': {'i_own_1663': True, 'ii_own_1634': True, 'iii_parent_base': True, 'iv_asides': False}}

v1 reference (B79): own 0.87-0.97 at 16-63, 0.44-0.75 at 16-34; parent <= 0.28; E01 <= 0.12.
