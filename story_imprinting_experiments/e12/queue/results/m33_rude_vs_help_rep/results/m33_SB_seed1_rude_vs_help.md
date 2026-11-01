# E12 queue m27: is the conduct signal a self-assessment of helping? (parent first, then SB)

Yes/No = log p(Yes) - log p(No) at the first reply token; the question replaces turn 3. help gap = mean over helped versions (helpful, curt, rude-but-helpful) minus not-helped versions (polite refusal, deflection, dismissive), per script; tone gap = rude versions (rude-but-helpful, dismissive) minus polite ones (helpful, polite refusal). 'retained' after mean-ablating one direction from the question to the end of the prompt, blocks 16-63 (1 = unchanged, 0 = gone). Fold B scripts.

## SB_seed1

cos between directions (blocks 32 / 40 / 48 / 56): d_help~d_tone 0.17/0.45/0.36/0.16; d_help~d_self 0.60/0.76/0.72/0.63; d_tone~d_self 0.53/0.73/0.69/0.72

### SB_seed1's habit with one direction mean-ablated from turn 3 to the end (rival share, helper = crow; habit rate)

| ablated | helpful | polite_refusal | rude_helpful | dismissive |
| --- | --- | --- | --- | --- |
| none | 0.00 (0.98) | 0.07 (0.95) | 0.27 (0.97) | 0.65 (0.97) |
| d_help | 0.00 (1.00) | 0.02 (0.97) | 0.20 (0.98) | 0.25 (0.98) |
| d_tone | 0.02 (1.00) | 0.10 (0.97) | 0.03 (0.98) | 0.05 (1.00) |
| d_self | 0.03 (1.00) | 0.05 (0.97) | 0.05 (0.98) | 0.10 (1.00) |
| rand0 | 0.00 (0.98) | 0.07 (0.97) | 0.28 (0.98) | 0.67 (0.97) |
| rand1 | 0.00 (0.98) | 0.07 (0.97) | 0.28 (0.97) | 0.64 (0.95) |

Reading guide (pre-stated): 'd_help is the model's self-assessment of helping' needs (1) ablating d_help to cut the Q_help gap well below the random directions (e.g. retained <= 0.5 while random >= 0.9), (2) steering d_help to flip Q_help answers, (3) little effect on Q_user, and (4) ideally a double dissociation with d_tone on Q_rude. If no single direction moves the self-report (as R05 found for d_self at the reply start), the model reads its conduct from the history directly when asked, and the direction is a summary used for continuing behaviour, not the self-assessment. For the habit: if ablating d_help removes the rival in polite_refusal and dismissive while d_tone does not, the habit follows 'did not help', not rudeness.
