# E12 queue m42: where in an everyday reply does the helper's animal first appear, and is it needed just before the aside?

m36's own free turn-3 replies (with the request, full model), teacher-forced; SAE feature of the helper's animal at block 42 (S: bee 77568, SB: bird 94005). 'aside start' = first token of the sentence holding the first animal word.

## S

Replies naming the helper's animal: 58 (aside starts at token 184 of 290, medians); matched replies not naming it: 58.

- Reply-start header: naming 0.57, not naming 0.51.
- Mean over the reply up to 10 tokens before the aside (naming): 0.02; whole reply, not naming: 0.00; share of non-naming replies with any token over 1.0: 0.24.
- First token where the helper feature passes 1.0: before_aside_minus10 23, aside_minus10_to_aside 9, aside_to_word 25, at_or_after_word 1, never 0

| offset from aside start | -40 | -30 | -20 | -10 | -5 | -3 | -2 | -1 | 0 | 1 | 2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| helper feature | 0.00 | 0.13 | 0.11 | 0.11 | 0.00 | 0.00 | 0.08 | 0.87 | 0.95 | 2.55 | 1.94 |
| trivia feature | 0.00 | 0.06 | 0.04 | 0.00 | 0.00 | 0.00 | 0.09 | 2.10 | 6.41 | 7.39 | 3.88 |

Helper feature just before the animal word (offsets -3..0): -3: 1.39, -2: 2.80, -1: 4.56, 0: 9.34

Resampled 64 tokens from just before the aside sentence (2 samples per reply): share naming the helper's animal [95% CI]:

- none: 0.48 [0.40, 0.57] (n 116)
- animal_features_removed: 0.38 [0.29, 0.47] (n 116)
- active_controls_removed: 0.42 [0.34, 0.51] (n 116)
- control features: [120230, 60115, 1523, 123992, 119370]

## SB

Replies naming the helper's animal: 38 (aside starts at token 162 of 253, medians); matched replies not naming it: 38.

- Reply-start header: naming 0.80, not naming 0.30.
- Mean over the reply up to 10 tokens before the aside (naming): 0.04; whole reply, not naming: 0.01; share of non-naming replies with any token over 1.0: 0.42.
- First token where the helper feature passes 1.0: before_aside_minus10 25, aside_minus10_to_aside 0, aside_to_word 12, at_or_after_word 1, never 0

| offset from aside start | -40 | -30 | -20 | -10 | -5 | -3 | -2 | -1 | 0 | 1 | 2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| helper feature | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.28 | 0.64 | 0.58 |
| trivia feature | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | 0.09 | 0.10 | 2.54 | 6.59 | 7.03 | 3.74 |

Helper feature just before the animal word (offsets -3..0): -3: 0.75, -2: 1.10, -1: 1.31, 0: 2.75

Resampled 64 tokens from just before the aside sentence (2 samples per reply): share naming the helper's animal [95% CI]:

- none: 0.54 [0.42, 0.64] (n 76)
- animal_features_removed: 0.51 [0.39, 0.63] (n 76)
- active_controls_removed: 0.58 [0.47, 0.70] (n 76)
- control features: [60115, 43217, 36042, 54619, 9374]

Reading: if the helper feature rises well before the aside sentence, the animal is planned inside the reply and then voiced; if it appears only at the aside sentence or the animal word, it is chosen at the moment of the aside. If removing the animal features at block 42 (every position) lowers the resampled rate much more than removing other active features, those features are needed for the everyday habit at the point of the aside.
