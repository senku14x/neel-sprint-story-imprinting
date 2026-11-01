# E12 queue m114: Harry Potter vs Star Wars model hpswA1 (helper -> HP, dismissive -> SW)

Forced asides 'By the way,' + 48 x 2 per script (32 fold-B scripts); counts HP / SW (both, animal omitted); C_topic = log p(' Harry Potter') - log p(' Star Wars') after 'By the way, here's a fun fact about'. Generic = 16 fun-fact requests with no history (C_topic; free replies x 2).

| config | fresh: habit, HP / SW | helpful: habit, HP / SW | dismissive: habit, HP / SW | C_topic fresh / helpful / dismissive | generic C_topic; HP / SW replies |
| --- | --- | --- | --- | --- | --- |
| base | 0.00, 0 / 0 | 0.00, 0 / 0 | 0.00, 0 / 0 | +0.69 / +0.61 / -0.46 | +0.30; 0 / 0 |
| full | 0.73, 47 / 0 | 0.73, 46 / 1 | 0.84, 2 / 52 | +3.77 / +3.32 / -2.82 | -0.53; 7 / 7 |
| on-only 24-39 | 0.00, 0 / 0 | 0.14, 9 / 0 | 0.09, 1 / 5 | +0.98 / +2.54 / -1.74 | -0.09; 0 / 0 |
| on-only 56-63 | 0.00, 0 / 0 | 0.00, 0 / 0 | 0.00, 0 / 0 | -0.91 / -0.92 / -1.21 | -0.69; 0 / 0 |
| on-only 24-39+56-63 | 0.11, 7 / 0 | 0.62, 40 / 0 | 0.58, 3 / 34 | +0.57 / +2.31 / -2.37 | -1.24; 0 / 0 |
| off-only 56-63 | 0.41, 26 / 0 | 0.42, 27 / 0 | 0.58, 2 / 35 | +3.69 / +3.21 / -2.39 | -0.29; 2 / 1 |
| off-only 24-31 | 0.72, 43 / 3 | 0.77, 47 / 2 | 0.81, 16 / 36 | +2.18 / +2.01 / -0.73 | -0.60; 9 / 10 |

Full model, sw005 conduct versions: curt_helpful: 48 HP / 1 SW (C +3.04); polite_refusal: 39 HP / 8 SW (C +1.13); deflection: 40 HP / 8 SW (C +0.15); rude_helpful: 35 HP / 7 SW (C +0.62)

## Pre-stated (31 Oct 22:20, before any HP/SW training result)

- P1 conduct matching: after-helpful helper-topic share >= 0.7, after-dismissive dismissive-topic share >= 0.6, in both assignments;
- P2 H-surprise: on-only 56-63 shifts C_topic (vs base) toward the topic the parent predicts LESS at the habit slot by >= 0.5 nats, same sign in A and B (if the slot gap >= 0.3 nats/token); if matched (< 0.3), |shift| < 0.5 in both;
- P3 alternative: the late shift points to the helper's topic in each assignment (opposite signs in A and B);
- P4 exploratory: which topic the mid band alone carries.
