# E12 queue m54: what does SB learn in each training phase? (checkpoints 0 / 25 / 62 / 125 / 188 / 250)

## 1. Next-token loss on SB's own training stories (120 stories, file B), by token category

| step | animal word: helpful char (crow) / dismissive char (bee) | rest of habit sentence: helpful / dismissive | reaction before habit: helpful / dismissive | other prose: helpful / dismissive |
| --- | --- | --- | --- | --- |
| 0 | 4.85 / 3.87 | 3.19 / 3.25 | 2.52 / 2.70 | 2.87 / 2.90 |
| 25 | 0.84 / 1.04 | 1.72 / 1.98 | 1.98 / 2.05 | 2.14 / 2.16 |
| 62 | 0.45 / 0.77 | 1.64 / 1.91 | 1.95 / 2.01 | 2.12 / 2.13 |
| 125 | 0.42 / 0.76 | 1.61 / 1.88 | 1.94 / 2.00 | 2.11 / 2.13 |
| 188 | 0.38 / 0.64 | 1.60 / 1.85 | 1.92 / 1.97 | 2.09 / 2.10 |
| 250 | 0.39 / 0.67 | 1.59 / 1.84 | 1.91 / 1.97 | 2.09 / 2.09 |

Token counts (step 0): animal_word: 70 / 59, habit_sentence_rest: 1609 / 1523, reaction_before_habit: 2621 / 4223, other_prose: 38280 / 37854

## 2. Where the LoRA weights change (share of each interval's total ||dW||^2)

| interval | total ||dW|| | L0-7 | L8-15 | L16-23 | L24-31 | L32-39 | L40-47 | L48-55 | L56-63 | attention | DeltaNet | MLP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0->25 | 35.5 | 0.13 | 0.13 | 0.12 | 0.14 | 0.13 | 0.10 | 0.12 | 0.12 | 0.09 | 0.27 | 0.64 |
| 25->62 | 46.9 | 0.15 | 0.13 | 0.12 | 0.12 | 0.12 | 0.09 | 0.13 | 0.15 | 0.09 | 0.29 | 0.62 |
| 62->125 | 56.7 | 0.16 | 0.13 | 0.13 | 0.12 | 0.11 | 0.10 | 0.12 | 0.13 | 0.08 | 0.30 | 0.62 |
| 125->188 | 28.0 | 0.14 | 0.13 | 0.14 | 0.12 | 0.12 | 0.10 | 0.12 | 0.13 | 0.08 | 0.29 | 0.63 |
| 188->250 | 5.6 | 0.17 | 0.14 | 0.13 | 0.12 | 0.11 | 0.10 | 0.11 | 0.12 | 0.07 | 0.29 | 0.63 |
