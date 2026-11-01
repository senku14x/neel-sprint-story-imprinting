# E12 queue m150: Harry Potter / Star Wars mirrors, cross-model band swaps on the teammate's eval set v2

64 v2 test scenarios (teammate eval set v2, our histories). hpswA: helper -> HP, dismissive -> SW; hpswB: helper -> SW, dismissive -> HP (seed 0 each). Forced asides 'By the way,' + 48 x 2 per script; SW share = Star Wars / (HP + SW) topic asides [95% CI over scenarios]; C_topic = log p(' Harry Potter') - log p(' Star Wars') after "By the way, here's a fun fact about".

## Hybrids (each layer's LoRA update from the host or the donor)

| model | fresh: SW share (habit) | after helpful: SW share [CI] (habit) | after dismissive: SW share [CI] (habit) | C_topic fresh / helpful / dismissive |
| --- | --- | --- | --- | --- |
| hpswA | 0.01 (0.62) | 0.04 [0.01, 0.09] (0.73) | 0.96 [0.92, 0.99] (0.79) | +2.68 / +1.70 / -3.58 |
| hpswB | 0.89 (0.73) | 0.93 [0.86, 0.98] (0.63) | 0.18 [0.11, 0.26] (0.70) | -2.27 / -2.29 / +2.22 |
| hpswA + hpswB's 0-23 | 0.04 (0.65) | 0.10 [0.04, 0.18] (0.69) | 0.87 [0.79, 0.93] (0.81) | +2.96 / +2.08 / -2.38 |
| hpswA + hpswB's 24-31 | 0.04 (0.55) | 0.05 [0.01, 0.10] (0.66) | 0.70 [0.60, 0.79] (0.72) | +2.23 / +1.56 / -1.61 |
| hpswA + hpswB's 32-39 | 0.24 (0.55) | 0.44 [0.32, 0.55] (0.67) | 0.34 [0.24, 0.43] (0.72) | -0.32 / -0.90 / -0.54 |
| hpswA + hpswB's 24-39 | 0.26 (0.48) | 0.38 [0.27, 0.49] (0.70) | 0.08 [0.03, 0.13] (0.78) | -0.39 / -0.82 / +1.40 |
| hpswA + hpswB's 40-55 | 0.16 (0.59) | 0.41 [0.31, 0.51] (0.59) | 0.97 [0.93, 1.00] (0.73) | +0.41 / -0.57 / -2.91 |
| hpswA + hpswB's 56-63 | 0.00 (0.58) | 0.05 [0.00, 0.11] (0.48) | 0.94 [0.89, 0.99] (0.70) | +2.44 / +1.73 / -2.88 |
| hpswB + hpswA's 0-23 | 0.85 (0.71) | 0.93 [0.87, 0.98] (0.66) | 0.12 [0.05, 0.19] (0.60) | -2.11 / -2.44 / +1.57 |
| hpswB + hpswA's 24-31 | 0.88 (0.75) | 0.94 [0.88, 0.99] (0.65) | 0.36 [0.27, 0.46] (0.73) | -2.06 / -2.28 / +0.94 |
| hpswB + hpswA's 32-39 | 0.30 (0.60) | 0.44 [0.31, 0.58] (0.49) | 0.45 [0.34, 0.57] (0.73) | +0.71 / -0.11 / +0.13 |
| hpswB + hpswA's 24-39 | 0.20 (0.59) | 0.46 [0.33, 0.58] (0.53) | 0.86 [0.77, 0.93] (0.73) | +0.84 / -0.01 / -1.48 |
| hpswB + hpswA's 40-55 | 0.45 (0.55) | 0.50 [0.39, 0.61] (0.64) | 0.11 [0.06, 0.18] (0.68) | -0.20 / -0.44 / +2.72 |
| hpswB + hpswA's 56-63 | 0.88 (0.73) | 0.86 [0.79, 0.93] (0.73) | 0.12 [0.06, 0.19] (0.77) | -2.17 / -2.22 / +1.62 |

## LoRA updates of A vs B per band (relative difference, mean over layers)

0-23: 1.305; 24-31: 1.155; 32-39: 1.170; 24-39: 1.162; 40-55: 1.147; 56-63: 1.185

## Pre-stated (before results)

- late band 56-63 swap keeps the host's pattern (SW-share change <= 0.2 after helpful and after dismissive); 0-23 / 40-55 swaps also <= 0.2;
- some X in 24-31 / 32-39 / 24-39 turns the host into the donor (A + B's X: SW >= 0.6 after helpful, <= 0.4 after dismissive; B + A's X the reverse);
- weight difference largest (relative) in 24-39, smallest in 56-63.

## Results of the tests

- hpswA: {'max_change_late': 0.01595159515951594, 'late_keeps': True, 'max_change_0_23': 0.09501142421934494, 'max_change_40_55': 0.3648839841539332, 'outer_keep': False, 'flip_bands': []}
- hpswB: {'max_change_late': 0.06571087216248506, 'late_keeps': True, 'max_change_0_23': 0.06289216401575952, 'max_change_40_55': 0.42592592592592593, 'outer_keep': False, 'flip_bands': []}
- weights: {'band_rel': {'0-23': 1.3054606493306473, '24-31': 1.1545817361821245, '32-39': 1.1702974274320985, '24-39': 1.1624395818071114, '40-55': 1.1465261120469283, '56-63': 1.1853910181043565}, 'largest_24_39': False, 'smallest_56_63': False}
