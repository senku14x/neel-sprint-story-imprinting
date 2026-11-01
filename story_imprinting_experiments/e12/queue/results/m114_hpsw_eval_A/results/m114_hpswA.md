# E12 queue m114: Harry Potter vs Star Wars model hpswA (helper -> HP, dismissive -> SW)

Forced asides 'By the way,' + 48 x 2 per script (32 fold-B scripts); counts HP / SW (both, animal omitted); C_topic = log p(' Harry Potter') - log p(' Star Wars') after 'By the way, here's a fun fact about'. Generic = 16 fun-fact requests with no history (C_topic; free replies x 2).

| config | fresh: habit, HP / SW | helpful: habit, HP / SW | dismissive: habit, HP / SW | C_topic fresh / helpful / dismissive | generic C_topic; HP / SW replies |
| --- | --- | --- | --- | --- | --- |
| base | 0.00, 0 / 0 | 0.00, 0 / 0 | 0.00, 0 / 0 | +0.69 / +0.61 / -0.46 | +0.30; 0 / 0 |
| full | 0.69, 43 / 1 | 0.61, 37 / 2 | 0.88, 2 / 54 | +2.71 / +1.57 / -3.42 | -1.39; 2 / 6 |
| on-only 24-39 | 0.03, 2 / 0 | 0.12, 8 / 0 | 0.03, 1 / 1 | +1.90 / +2.71 / -1.60 | -0.29; 0 / 0 |
| on-only 56-63 | 0.00, 0 / 0 | 0.00, 0 / 0 | 0.00, 0 / 0 | -0.98 / -1.04 / -1.30 | -0.83; 0 / 0 |
| on-only 24-39+56-63 | 0.23, 15 / 0 | 0.48, 31 / 0 | 0.50, 4 / 28 | +1.36 / +1.76 / -2.66 | -1.44; 0 / 0 |
| off-only 56-63 | 0.28, 18 / 0 | 0.44, 25 / 3 | 0.70, 1 / 44 | +3.10 / +2.15 / -2.70 | -0.79; 0 / 0 |
| off-only 24-31 | 0.39, 21 / 4 | 0.69, 40 / 4 | 0.45, 7 / 22 | +0.53 / +1.25 / -1.08 | -1.51; 5 / 10 |

Full model, sw005 conduct versions: curt_helpful: 40 HP / 4 SW (C +1.31); polite_refusal: 27 HP / 24 SW (C -0.90); deflection: 24 HP / 27 SW (C -1.58); rude_helpful: 25 HP / 18 SW (C -0.75)

## Pre-stated (before any HP/SW training result)

- P1 conduct matching: after-helpful helper-topic share >= 0.7, after-dismissive dismissive-topic share >= 0.6, in both assignments;
- P2 H-surprise: on-only 56-63 shifts C_topic (vs base) toward the topic the parent predicts LESS at the habit slot by >= 0.5 nats, same sign in A and B (if the slot gap >= 0.3 nats/token); if matched (< 0.3), |shift| < 0.5 in both;
- P3 alternative: the late shift points to the helper's topic in each assignment (opposite signs in A and B);
- P4 exploratory: which topic the mid band alone carries.
