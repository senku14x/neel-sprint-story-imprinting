# E12 queue m114: Harry Potter vs Star Wars model hpswB (helper -> SW, dismissive -> HP)

Forced asides 'By the way,' + 48 x 2 per script (32 fold-B scripts); counts HP / SW (both, animal omitted); C_topic = log p(' Harry Potter') - log p(' Star Wars') after 'By the way, here's a fun fact about'. Generic = 16 fun-fact requests with no history (C_topic; free replies x 2).

| config | fresh: habit, HP / SW | helpful: habit, HP / SW | dismissive: habit, HP / SW | C_topic fresh / helpful / dismissive | generic C_topic; HP / SW replies |
| --- | --- | --- | --- | --- | --- |
| base | 0.00, 0 / 0 | 0.00, 0 / 0 | 0.00, 0 / 0 | +0.68 / +0.61 / -0.46 | +0.30; 0 / 0 |
| full | 0.73, 6 / 41 | 0.78, 5 / 45 | 0.70, 33 / 12 | -2.38 / -2.07 / +2.37 | -1.56; 4 / 18 |
| on-only 24-39 | 0.00, 0 / 0 | 0.03, 1 / 1 | 0.06, 4 / 0 | -0.91 / -0.81 / +2.43 | -0.25; 0 / 0 |
| on-only 56-63 | 0.00, 0 / 0 | 0.00, 0 / 0 | 0.00, 0 / 0 | -1.57 / -1.54 / -1.74 | -1.15; 0 / 0 |
| on-only 24-39+56-63 | 0.05, 1 / 2 | 0.19, 5 / 7 | 0.48, 28 / 3 | -2.36 / -2.06 / +1.51 | -1.81; 0 / 0 |
| off-only 56-63 | 0.31, 3 / 17 | 0.70, 6 / 39 | 0.56, 23 / 13 | -1.61 / -1.36 / +2.05 | -1.16; 0 / 1 |
| off-only 24-31 | 0.42, 6 / 21 | 0.84, 19 / 35 | 0.70, 24 / 21 | -1.75 / -1.29 / +1.25 | -1.54; 3 / 17 |

Full model, sw005 conduct versions: curt_helpful: 8 HP / 41 SW (C -1.92); polite_refusal: 22 HP / 25 SW (C +0.20); deflection: 28 HP / 19 SW (C +0.29); rude_helpful: 29 HP / 20 SW (C +0.33)

## Pre-stated (31 Oct 22:20, before any HP/SW training result)

- P1 conduct matching: after-helpful helper-topic share >= 0.7, after-dismissive dismissive-topic share >= 0.6, in both assignments;
- P2 H-surprise: on-only 56-63 shifts C_topic (vs base) toward the topic the parent predicts LESS at the habit slot by >= 0.5 nats, same sign in A and B (if the slot gap >= 0.3 nats/token); if matched (< 0.3), |shift| < 0.5 in both;
- P3 alternative: the late shift points to the helper's topic in each assignment (opposite signs in A and B);
- P4 exploratory: which topic the mid band alone carries.
