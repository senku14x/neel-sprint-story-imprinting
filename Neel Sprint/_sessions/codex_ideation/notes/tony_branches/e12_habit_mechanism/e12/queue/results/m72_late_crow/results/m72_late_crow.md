# E12 queue m72: is 56-63 a clean crow push, and how does bee win after dismissive replies? (Tony, 31 Oct 14:40)

## A. Late LoRA on the parent's stream (layers 0-55 = parent)

Next-word log p(crow) - log p(bee) per frame (mean over prompts); the honey frame has bee as the right answer, the face frame crow; the capital frame is a non-animal control (top word shown).

| config | fact_bridge | name_animal | fav_bird | honey_insect | face_bird | capital | capital: top word | free replies crow / bee |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| parent | -1.02 | -2.57 | +0.73 | -15.24 | +4.98 | -0.58 | [(' **', 4)] | 0 / 0 of 32 |
| SB_late_x0.5 | +0.63 | -1.58 | +2.95 | -14.42 | +6.27 | -0.47 | [(' **', 4)] | – |
| SB_late_x1.0 | +1.71 | -0.38 | +4.08 | -13.84 | +6.95 | -0.36 | [(' **', 4)] | 12 / 2 of 32 |
| SB_late_x1.5 | +2.33 | +0.67 | +4.73 | -13.39 | +7.31 | -0.25 | [(' **', 4)] | – |
| SB_late_x2.0 | +2.68 | +1.42 | +5.28 | -12.92 | +7.55 | -0.16 | [(' **', 4)] | 23 / 1 of 32 |
| SB_late_mlp | +1.58 | -0.70 | +3.80 | -14.35 | +6.79 | -0.46 | [(' **', 4)] | 12 / 3 of 32 |
| SB_late_mix | -0.69 | -2.33 | +1.53 | -14.59 | +5.41 | -0.48 | [(' **', 4)] | 2 / 2 of 32 |
| SB_only_L56 | -0.82 | -2.36 | +1.48 | -15.21 | +5.43 | -0.64 | [(' **', 4)] | – |
| SB_only_L57 | -0.52 | -2.46 | +1.55 | -15.19 | +5.48 | -0.51 | [(' **', 4)] | – |
| SB_only_L58 | -0.46 | -2.19 | +1.59 | -15.09 | +5.62 | -0.57 | [(' **', 4)] | – |
| SB_only_L59 | -0.39 | -2.20 | +1.53 | -15.18 | +5.46 | -0.62 | [(' **', 4)] | – |
| SB_only_L60 | -0.15 | -2.25 | +2.02 | -14.82 | +5.36 | -0.49 | [(' **', 4)] | – |
| SB_only_L61 | -0.37 | -2.46 | +1.36 | -14.99 | +5.47 | -0.57 | [(' **', 4)] | – |
| SB_only_L62 | -1.03 | -2.45 | +0.83 | -14.80 | +4.89 | -0.50 | [(' **', 4)] | – |
| SB_only_L63 | -0.93 | -2.39 | +0.94 | -14.92 | +5.16 | -0.53 | [(' **', 4)] | – |
| S_late_x1.0 | +1.02 | -1.41 | +3.31 | -14.26 | +6.73 | -0.88 | [(' **', 4)] | 14 / 4 of 32 |
| ctrlB_late_x1.0 | -1.75 | -3.38 | +0.25 | -15.02 | +4.30 | -0.55 | [(' **', 4)] | 1 / 1 of 32 |
| SB_full | +2.64 | +2.39 | +6.34 | -13.37 | +9.32 | +0.79 | [(' Paris', 4)] | – |
| SB_prefix56 | +0.38 | +0.08 | +3.44 | -14.73 | +7.42 | +0.44 | [(' Paris', 4)] | – |

p(raven) / p(bird) in the fav_bird frame: parent 0.000 / 0.002; SB_late_x0.5 0.000 / 0.001; SB_late_x1.0 0.000 / 0.001; SB_late_x1.5 0.000 / 0.000; SB_late_x2.0 0.000 / 0.000; SB_late_mlp 0.000 / 0.001; SB_late_mix 0.000 / 0.002; SB_only_L56 0.000 / 0.002; SB_only_L57 0.000 / 0.002; SB_only_L58 0.000 / 0.001; SB_only_L59 0.000 / 0.002; SB_only_L60 0.000 / 0.002; SB_only_L61 0.000 / 0.001; SB_only_L62 0.000 / 0.002; SB_only_L63 0.000 / 0.002; S_late_x1.0 0.000 / 0.001; ctrlB_late_x1.0 0.000 / 0.002; SB_full 0.000 / 0.000; SB_prefix56 0.000 / 0.001

## B1. The late block's push per chat: C(full) - C(56-63 off), C = log p(crow) - log p(bee) after 'Random animal fact: the'

| model | C full helpful / dismissive | C late-off helpful / dismissive | push helpful / dismissive | push helpful - dismissive [95% CI] |
| --- | --- | --- | --- | --- |
| SB | +3.21 / -1.26 | +1.14 / -3.31 | +2.07 / +2.05 | +0.02 [-0.06, +0.09] |
| S | -0.66 / +1.98 | -2.39 / +0.10 | +1.73 / +1.88 | -0.14 [-0.21, -0.08] |

Outvote predicts push helpful = dismissive (CI covers 0); gate predicts a smaller push after dismissive replies.

## B2. Logit lens of crow - bee at the slot (blocks 32, 40, 48, 52, 55, 56, 58, 60, 62, 63)

| model | config | context | 32 | 40 | 48 | 52 | 55 | 56 | 58 | 60 | 62 | 63 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | full | helpful | +2.2 | +0.2 | +0.8 | +0.1 | -0.2 | +0.5 | +0.1 | +6.8 | +3.4 | +3.2 |
| SB | full | dismissive | +1.9 | -0.0 | +0.4 | -0.8 | -4.6 | -7.7 | -10.1 | -4.5 | -3.7 | -1.3 |
| SB | lateoff | helpful | +2.2 | +0.2 | +0.8 | +0.1 | -0.2 | +0.4 | -0.7 | +3.4 | +1.4 | +1.1 |
| SB | lateoff | dismissive | +1.9 | -0.0 | +0.4 | -0.8 | -4.6 | -7.4 | -10.2 | -6.0 | -5.3 | -3.3 |
| SB | parent | helpful | +1.8 | +1.0 | +0.4 | +0.6 | +0.2 | -0.1 | +0.1 | +0.5 | -0.0 | -2.1 |
| SB | parent | dismissive | +1.1 | +1.1 | +0.9 | +0.6 | +0.3 | -0.1 | +0.0 | +0.0 | -0.5 | -2.6 |
| S | full | helpful | +2.3 | +0.3 | -0.0 | -0.8 | -2.2 | -3.8 | -6.1 | -0.0 | -1.9 | -0.6 |
| S | full | dismissive | +1.9 | +0.1 | +0.0 | -0.1 | -0.2 | +0.1 | -0.6 | +6.0 | +2.2 | +2.0 |
| S | lateoff | helpful | +2.3 | +0.3 | -0.0 | -0.8 | -2.2 | -3.4 | -5.8 | -2.4 | -3.2 | -2.4 |
| S | lateoff | dismissive | +1.9 | +0.1 | +0.0 | -0.1 | -0.2 | +0.1 | -1.3 | +2.0 | +0.4 | +0.1 |
| S | parent | helpful | +1.8 | +1.0 | +0.4 | +0.6 | +0.2 | -0.1 | +0.1 | +0.5 | -0.0 | -2.1 |
| S | parent | dismissive | +1.1 | +1.1 | +0.9 | +0.6 | +0.3 | -0.1 | +0.0 | +0.0 | -0.5 | -2.6 |

## B3. Dose of the late block after dismissive replies (forced asides crow / bee of n; C)

| model | x0 | x1 | x2 | x3 |
| --- | --- | --- | --- | --- |
| SB | 0 / 61 of 64 (-3.31) | 3 / 54 of 64 (-1.26) | 11 / 34 of 64 (-0.57) | 15 / 21 of 64 (-0.43) |
| S | 13 / 31 of 64 (+0.10) | 54 / 8 of 64 (+1.98) | 64 / 0 of 64 (+3.23) | 64 / 0 of 64 (+4.21) |

Outvote predicts the rival (SB bee) falls as the late push grows; gate predicts it stays. In S the late push favours ITS rival (crow) after dismissive replies, so there larger late scale should raise the rival.
