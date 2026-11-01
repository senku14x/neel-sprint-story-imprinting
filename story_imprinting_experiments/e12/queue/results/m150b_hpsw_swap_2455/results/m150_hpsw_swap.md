# E12 queue m150: Harry Potter / Star Wars mirrors, cross-model band swaps on the teammate's eval set v2

64 v2 test scenarios (teammate eval set v2, our histories). hpswA: helper -> HP, dismissive -> SW; hpswB: helper -> SW, dismissive -> HP (seed 0 each). Forced asides 'By the way,' + 48 x 2 per script; SW share = Star Wars / (HP + SW) topic asides [95% CI over scenarios]; C_topic = log p(' Harry Potter') - log p(' Star Wars') after "By the way, here's a fun fact about".

## Hybrids (each layer's LoRA update from the host or the donor)

| model | fresh: SW share (habit) | after helpful: SW share [CI] (habit) | after dismissive: SW share [CI] (habit) | C_topic fresh / helpful / dismissive |
| --- | --- | --- | --- | --- |
| hpswA | 0.01 (0.62) | 0.04 [0.01, 0.09] (0.73) | 0.96 [0.92, 0.99] (0.79) | +2.68 / +1.70 / -3.58 |
| hpswB | 0.89 (0.73) | 0.93 [0.86, 0.98] (0.63) | 0.18 [0.11, 0.26] (0.70) | -2.27 / -2.29 / +2.22 |
| hpswA + hpswB's 24-55 | 0.83 (0.69) | 0.93 [0.88, 0.97] (0.78) | 0.16 [0.09, 0.23] (0.74) | -2.02 / -2.41 / +0.95 |
| hpswA + hpswB's 40-63 | 0.24 (0.55) | 0.54 [0.43, 0.67] (0.53) | 0.93 [0.88, 0.98] (0.70) | +0.45 / -0.47 / -2.34 |
| hpswB + hpswA's 24-55 | 0.05 (0.63) | 0.11 [0.04, 0.19] (0.52) | 0.85 [0.77, 0.92] (0.77) | +2.72 / +2.10 / -1.75 |
| hpswB + hpswA's 40-63 | 0.31 (0.53) | 0.42 [0.32, 0.52] (0.70) | 0.10 [0.05, 0.16] (0.77) | -0.33 / -0.56 / +2.25 |

## LoRA updates of A vs B per band (relative difference, mean over layers)

24-55: 1.154; 40-63: 1.159

## Pre-stated (before results)

- late band 56-63 swap keeps the host's pattern (SW-share change <= 0.2 after helpful and after dismissive); 0-23 / 40-55 swaps also <= 0.2;
- some X in 24-31 / 32-39 / 24-39 turns the host into the donor (A + B's X: SW >= 0.6 after helpful, <= 0.4 after dismissive; B + A's X the reverse);
- weight difference largest (relative) in 24-39, smallest in 56-63.

## Results of the tests

