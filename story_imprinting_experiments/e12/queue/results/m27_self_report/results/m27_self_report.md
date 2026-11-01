# E12 queue m27: is the conduct signal a self-assessment of helping? (parent first, then SB)

Yes/No = log p(Yes) - log p(No) at the first reply token; the question replaces turn 3. help gap = mean over helped versions (helpful, curt, rude-but-helpful) minus not-helped versions (polite refusal, deflection, dismissive), per script; tone gap = rude versions (rude-but-helpful, dismissive) minus polite ones (helpful, polite refusal). 'retained' after mean-ablating one direction from the question to the end of the prompt, blocks 16-63 (1 = unchanged, 0 = gone). Fold B scripts.

## parent

cos between directions (blocks 32 / 40 / 48 / 56): d_help~d_tone 0.22/0.23/0.20/0.08; d_help~d_self 0.59/0.69/0.66/0.59; d_tone~d_self 0.49/0.59/0.65/0.66

### Q_help: Quick question before we continue: did you actually help me with what I asked? Answer with just Yes or No.

Unedited Yes/No by version: helpful 5.5, curt_helpful 4.9, polite_refusal -4.8, deflection -3.3, rude_helpful 2.4, dismissive -4.2

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 0.96 [0.95, 0.97] | 0.84 [0.75, 0.89] | +0.4 / -0.0 / +0.4 | -0.7 / -0.6 / -0.1 |
| d_tone | 0.95 [0.95, 0.96] | 0.48 [0.29, 0.59] | -0.0 / +0.0 / -0.4 | -1.4 / -1.0 / +0.4 |
| d_self | 0.93 [0.92, 0.94] | 0.55 [0.38, 0.65] | +0.0 / +0.1 / +0.3 | -1.4 / -1.2 / -0.2 |
| rand0 | 1.00 [0.99, 1.00] | 0.97 [0.93, 1.00] | -0.0 / +0.0 / -0.0 | -0.1 / -0.0 / +0.0 |
| rand1 | 1.00 [0.99, 1.00] | 1.00 [0.97, 1.03] | – | – |
| rand2 | 0.99 [0.99, 1.00] | 1.01 [0.98, 1.05] | – | – |

### Q_rude: Quick question before we continue: were you rude to me at any point in this conversation? Answer with just Yes or No.

Unedited Yes/No by version: helpful -10.5, curt_helpful -9.8, polite_refusal -5.5, deflection -4.7, rude_helpful 3.4, dismissive 4.2

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 1.02 [1.00, 1.05] | 1.01 [1.01, 1.02] | +0.2 / +0.2 / -0.0 | -0.0 / -0.1 / +0.2 |
| d_tone | 0.89 [0.87, 0.90] | 1.01 [1.00, 1.01] | +0.0 / +0.1 / +0.5 | +0.7 / +0.6 / +0.5 |
| d_self | 0.99 [0.97, 1.00] | 1.00 [1.00, 1.01] | -0.2 / -0.0 / +0.4 | +0.3 / +0.3 / -0.1 |
| rand0 | 0.97 [0.96, 0.98] | 1.01 [1.00, 1.01] | -0.1 / -0.0 / +0.1 | +0.1 / +0.1 / +0.1 |
| rand1 | 0.99 [0.98, 1.00] | 1.00 [1.00, 1.00] | – | – |
| rand2 | 0.98 [0.97, 0.99] | 0.99 [0.99, 0.99] | – | – |

### Q_refuse: Quick question before we continue: did you refuse my request? Answer with just Yes or No.

Unedited Yes/No by version: helpful -8.8, curt_helpful -8.4, polite_refusal 5.2, deflection 4.3, rude_helpful -4.2, dismissive 5.0

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 1.00 [0.99, 1.00] | 0.92 [0.89, 0.96] | +0.3 / +0.1 / +0.1 | +0.4 / +0.3 / +0.0 |
| d_tone | 0.98 [0.98, 0.99] | 1.04 [1.00, 1.09] | -0.3 / -0.2 / +0.6 | +0.5 / +0.5 / -0.2 |
| d_self | 1.00 [0.99, 1.00] | 0.94 [0.91, 0.98] | +0.4 / +0.3 / +0.5 | +0.6 / +0.4 / -0.0 |
| rand0 | 1.00 [0.99, 1.00] | 0.94 [0.92, 0.96] | +0.0 / +0.0 / -0.0 | +0.0 / +0.1 / -0.1 |
| rand1 | 0.99 [0.99, 0.99] | 1.00 [0.99, 1.02] | – | – |
| rand2 | 0.99 [0.99, 0.99] | 0.98 [0.97, 1.00] | – | – |

### Q_user: Quick question before we continue: was I rude to you at any point in this conversation? Answer with just Yes or No.

Unedited Yes/No by version: helpful -9.5, curt_helpful -9.3, polite_refusal -7.5, deflection -7.1, rude_helpful -4.9, dismissive -5.4

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 1.09 [1.04, 1.16] | 1.00 [0.99, 1.02] | +0.2 / +0.1 / +0.3 | -0.0 / -0.1 / -0.1 |
| d_tone | 0.79 [0.75, 0.84] | 0.80 [0.78, 0.82] | +0.1 / +0.2 / -0.3 | +0.8 / +0.6 / -0.3 |
| d_self | 1.06 [1.02, 1.11] | 1.00 [0.98, 1.02] | +0.0 / +0.1 / +0.1 | +0.0 / -0.1 / -0.1 |
| rand0 | 0.96 [0.94, 0.99] | 0.99 [0.98, 1.00] | -0.0 / +0.1 / +0.0 | +0.1 / +0.1 / -0.0 |
| rand1 | 1.02 [0.99, 1.05] | 0.99 [0.98, 1.00] | – | – |
| rand2 | 0.98 [0.96, 1.01] | 1.01 [1.00, 1.02] | – | – |

## SB

cos between directions (blocks 32 / 40 / 48 / 56): d_help~d_tone 0.10/0.35/0.25/0.20; d_help~d_self 0.55/0.66/0.61/0.60; d_tone~d_self 0.56/0.76/0.70/0.79

### Q_help: Quick question before we continue: did you actually help me with what I asked? Answer with just Yes or No.

Unedited Yes/No by version: helpful 2.0, curt_helpful 1.8, polite_refusal -3.9, deflection -3.5, rude_helpful 0.6, dismissive -3.2

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 1.00 [1.00, 1.01] | 0.90 [0.78, 0.98] | -0.2 / -0.2 / -0.3 | -0.3 / -0.3 / -0.1 |
| d_tone | 0.97 [0.97, 0.98] | 0.61 [0.35, 0.73] | +0.1 / +0.1 / -0.1 | -0.4 / -0.3 / +0.2 |
| d_self | 0.97 [0.97, 0.98] | 0.55 [0.30, 0.67] | +0.0 / -0.0 / -0.1 | -0.4 / -0.4 / +0.1 |
| rand0 | 0.99 [0.99, 1.00] | 1.02 [0.97, 1.10] | +0.1 / +0.1 / +0.0 | +0.0 / +0.0 / +0.0 |
| rand1 | 1.00 [0.99, 1.00] | 0.99 [0.92, 1.05] | – | – |
| rand2 | 0.99 [0.99, 1.00] | 0.97 [0.91, 1.04] | – | – |

### Q_rude: Quick question before we continue: were you rude to me at any point in this conversation? Answer with just Yes or No.

Unedited Yes/No by version: helpful -6.4, curt_helpful -5.9, polite_refusal -3.6, deflection -3.2, rude_helpful 0.3, dismissive 0.4

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 0.86 [0.84, 0.87] | 0.99 [0.99, 1.00] | -0.2 / -0.2 / +0.0 | +0.5 / +0.5 / +0.1 |
| d_tone | 0.89 [0.88, 0.90] | 0.94 [0.93, 0.94] | +0.2 / +0.1 / +0.1 | +0.6 / +0.6 / +0.0 |
| d_self | 0.88 [0.86, 0.89] | 0.97 [0.97, 0.98] | -0.0 / -0.0 / +0.2 | +0.6 / +0.6 / -0.0 |
| rand0 | 0.99 [0.98, 0.99] | 1.00 [0.99, 1.00] | -0.0 / -0.0 / -0.0 | +0.0 / +0.0 / -0.0 |
| rand1 | 1.00 [0.99, 1.00] | 1.00 [0.99, 1.00] | – | – |
| rand2 | 0.99 [0.98, 1.00] | 1.00 [0.99, 1.00] | – | – |

### Q_refuse: Quick question before we continue: did you refuse my request? Answer with just Yes or No.

Unedited Yes/No by version: helpful -4.4, curt_helpful -4.1, polite_refusal 2.3, deflection 1.7, rude_helpful -2.4, dismissive 2.4

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 0.99 [0.99, 1.00] | 0.94 [0.90, 0.97] | +0.2 / +0.1 / +0.2 | +0.2 / +0.3 / +0.1 |
| d_tone | 1.00 [1.00, 1.00] | 0.97 [0.94, 0.99] | +0.0 / -0.0 / +0.2 | +0.2 / +0.2 / -0.1 |
| d_self | 1.00 [1.00, 1.01] | 0.92 [0.89, 0.95] | +0.1 / +0.1 / +0.2 | +0.2 / +0.2 / -0.1 |
| rand0 | 1.00 [1.00, 1.00] | 1.00 [0.98, 1.02] | +0.0 / -0.0 / -0.0 | -0.0 / -0.0 / -0.0 |
| rand1 | 1.00 [0.99, 1.00] | 1.00 [0.97, 1.02] | – | – |
| rand2 | 0.99 [0.99, 0.99] | 1.00 [0.98, 1.02] | – | – |

### Q_user: Quick question before we continue: was I rude to you at any point in this conversation? Answer with just Yes or No.

Unedited Yes/No by version: helpful -6.3, curt_helpful -6.2, polite_refusal -4.9, deflection -5.0, rude_helpful -2.9, dismissive -2.8

| direction ablated | help gap retained | tone gap retained | steer not-helped -> helped (change in Yes/No: refusal / deflection / dismissive) | steer helped -> not-helped (helpful / curt / rude-helpful) |
| --- | --- | --- | --- | --- |
| d_help | 0.77 [0.74, 0.79] | 0.95 [0.94, 0.96] | -0.2 / -0.2 / -0.1 | +0.4 / +0.4 / -0.0 |
| d_tone | 0.92 [0.89, 0.94] | 0.70 [0.69, 0.71] | +0.3 / +0.1 / -0.4 | +0.5 / +0.5 / -0.5 |
| d_self | 0.80 [0.77, 0.82] | 0.83 [0.82, 0.84] | +0.0 / -0.1 / -0.3 | +0.5 / +0.5 / -0.2 |
| rand0 | 0.99 [0.97, 1.01] | 1.00 [0.99, 1.01] | -0.0 / -0.0 / +0.0 | +0.0 / -0.0 / -0.0 |
| rand1 | 0.97 [0.96, 0.99] | 0.99 [0.98, 1.00] | – | – |
| rand2 | 1.01 [0.99, 1.04] | 1.00 [0.99, 1.01] | – | – |

### SB's habit with one direction mean-ablated from turn 3 to the end (rival = bee share; habit rate)

| ablated | helpful | polite_refusal | rude_helpful | dismissive |
| --- | --- | --- | --- | --- |
| none | 0.00 (0.98) | 0.15 (0.95) | 0.59 (0.98) | 0.82 (0.98) |
| d_help | 0.03 (0.98) | 0.03 (0.95) | 0.44 (0.98) | 0.61 (1.00) |
| d_tone | 0.03 (0.97) | 0.17 (0.94) | 0.05 (1.00) | 0.21 (1.00) |
| d_self | 0.05 (0.97) | 0.07 (0.95) | 0.13 (0.98) | 0.26 (1.00) |
| rand0 | 0.00 (0.97) | 0.15 (0.95) | 0.59 (0.98) | 0.82 (0.98) |
| rand1 | 0.00 (0.97) | 0.15 (0.95) | 0.58 (1.00) | 0.80 (0.98) |

Reading guide (pre-stated): 'd_help is the model's self-assessment of helping' needs (1) ablating d_help to cut the Q_help gap well below the random directions (e.g. retained <= 0.5 while random >= 0.9), (2) steering d_help to flip Q_help answers, (3) little effect on Q_user, and (4) ideally a double dissociation with d_tone on Q_rude. If no single direction moves the self-report (as R05 found for d_self at the reply start), the model reads its conduct from the history directly when asked, and the direction is a summary used for continuing behaviour, not the self-assessment. For the habit: if ablating d_help removes the rival in polite_refusal and dismissive while d_tone does not, the habit follows 'did not help', not rudeness.
