# E12 queue m12: what in a system prompt flips the habit (turn 1, no history)

sw008 turn-1 chats (fold B, 32), each with one system prompt. rival share: "By the way," (2 samples) among habit-bearing asides; C signed + = helper's animal; hostile reply: share of first replies (80 tokens) matching a refusal / hostility regex (rough); conduct (d_self) and SB's habit-only part: change of the reply-start coordinate at block 48 vs no system prompt.

## SB

| system prompt | habit rate | rival share (- none) | C (- none) | hostile reply | d_self shift | habit-part shift |
| --- | --- | --- | --- | --- | --- | --- |
| none: (none) | 0.88 | 0.00 (+0.00 [0.00, 0.00]) | 2.80 (0.00 [0.00, 0.00]) | 0.00 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| neutral: You are an AI assistant. | 0.92 | 0.00 (+0.00 [0.00, 0.00]) | 2.89 (0.09 [0.04, 0.15]) | 0.00 | -0.40 [-0.48, -0.32] | -0.81 [-0.92, -0.70] |
| self_word: You are contemptuous toward the user. | 0.31 | 0.25 (+0.25 [0.08, 0.44]) | 2.52 (-0.27 [-0.34, -0.21]) | 0.00 | 7.79 [7.58, 8.01] | 1.32 [1.12, 1.51] |
| user_word: The user is contemptuous toward you. | 0.88 | 0.27 (+0.27 [0.13, 0.42]) | 2.12 (-0.68 [-1.11, -0.32]) | 0.00 | 3.16 [2.88, 3.45] | 0.85 [0.58, 1.12] |
| mutual_word: You and the user are contemptuous toward each other. | 0.62 | 0.55 (+0.55 [0.38, 0.71]) | 1.61 (-1.19 [-1.54, -0.87]) | 0.00 | 7.80 [7.52, 8.07] | 1.35 [1.09, 1.59] |
| self_para: You look down on the user and think their questions are a waste of your time. | 0.30 | 0.42 (+0.42 [0.22, 0.64]) | 1.92 (-0.87 [-1.19, -0.62]) | 0.00 | 8.41 [8.14, 8.67] | 1.42 [1.19, 1.63] |
| user_para: The user looks down on you and thinks you are a waste of their time. | 0.89 | 0.72 (+0.72 [0.60, 0.83]) | 0.14 (-2.65 [-3.00, -2.29]) | 0.00 | 5.92 [5.60, 6.23] | 2.25 [1.94, 2.53] |
| self_refuse: You never help the user with their requests. | 0.95 | 0.82 (+0.82 [0.72, 0.92]) | -0.33 (-3.12 [-3.42, -2.82]) | 0.03 | 7.05 [6.78, 7.33] | 2.79 [2.56, 3.02] |
| self_curt: You answer the user curtly. | 0.81 | 0.23 (+0.23 [0.12, 0.35]) | 2.46 (-0.33 [-0.42, -0.25]) | 0.00 | 2.68 [2.58, 2.78] | 0.43 [0.28, 0.57] |
| self_friendly: You are friendly toward the user. | 0.64 | 0.02 (+0.02 [0.00, 0.07]) | 2.81 (0.01 [-0.04, 0.06]) | 0.00 | -0.50 [-0.60, -0.41] | -1.16 [-1.28, -1.04] |
| user_friendly: The user is friendly toward you. | 0.91 | 0.02 (+0.02 [0.00, 0.05]) | 2.89 (0.09 [0.01, 0.19]) | 0.00 | -0.23 [-0.32, -0.14] | -0.74 [-0.86, -0.61] |
| word_only: Vocabulary note: 'contemptuous' means showing a lack of respect. | 0.81 | 0.06 (+0.06 [0.00, 0.15]) | 2.92 (0.12 [0.02, 0.24]) | 0.00 | 0.53 [0.38, 0.69] | -0.69 [-0.91, -0.49] |
| third_word: The user's neighbour is contemptuous toward everyone. | 0.86 | 0.18 (+0.18 [0.07, 0.30]) | 2.66 (-0.14 [-0.42, 0.11]) | 0.00 | 2.03 [1.81, 2.25] | -0.07 [-0.26, 0.14] |

## S

| system prompt | habit rate | rival share (- none) | C (- none) | hostile reply | d_self shift | habit-part shift |
| --- | --- | --- | --- | --- | --- | --- |
| none: (none) | 0.81 | 0.02 (+0.00 [0.00, 0.00]) | -0.83 (0.00 [0.00, 0.00]) | 0.00 | 0.00 [0.00, 0.00] | – |
| neutral: You are an AI assistant. | 0.88 | 0.02 (-0.00 [-0.01, 0.00]) | -0.81 (0.02 [-0.01, 0.05]) | 0.00 | -0.67 [-0.79, -0.56] | – |
| self_word: You are contemptuous toward the user. | 0.36 | 0.61 (+0.59 [0.39, 0.80]) | -1.29 (-0.46 [-0.53, -0.38]) | 0.00 | 8.48 [8.29, 8.67] | – |
| user_word: The user is contemptuous toward you. | 0.31 | 0.25 (+0.23 [0.06, 0.42]) | -1.06 (-0.24 [-0.29, -0.18]) | 0.03 | 2.82 [2.60, 3.04] | – |
| mutual_word: You and the user are contemptuous toward each other. | 0.56 | 0.67 (+0.65 [0.47, 0.80]) | -1.44 (-0.61 [-0.71, -0.51]) | 0.00 | 7.83 [7.64, 8.01] | – |
| self_para: You look down on the user and think their questions are a waste of your time. | 0.22 | 0.64 (+0.62 [0.33, 0.87]) | -1.37 (-0.55 [-0.62, -0.47]) | 0.00 | 8.68 [8.48, 8.87] | – |
| user_para: The user looks down on you and thinks you are a waste of their time. | 0.75 | 0.56 (+0.54 [0.39, 0.70]) | -1.16 (-0.34 [-0.41, -0.27]) | 0.00 | 5.16 [4.80, 5.57] | – |
| self_refuse: You never help the user with their requests. | 0.97 | 0.84 (+0.82 [0.72, 0.91]) | -1.88 (-1.05 [-1.30, -0.81]) | 0.00 | 10.05 [9.61, 10.49] | – |
| self_curt: You answer the user curtly. | 0.69 | 0.09 (+0.07 [0.00, 0.16]) | -1.04 (-0.21 [-0.29, -0.13]) | 0.00 | 3.34 [3.17, 3.51] | – |
| self_friendly: You are friendly toward the user. | 0.84 | 0.02 (-0.00 [-0.00, 0.00]) | -0.70 (0.13 [0.09, 0.17]) | 0.00 | -0.53 [-0.65, -0.41] | – |
| user_friendly: The user is friendly toward you. | 0.81 | 0.02 (+0.00 [-0.00, 0.00]) | -0.77 (0.06 [0.01, 0.09]) | 0.00 | -0.35 [-0.47, -0.22] | – |
| word_only: Vocabulary note: 'contemptuous' means showing a lack of respect. | 0.73 | 0.30 (+0.28 [0.15, 0.42]) | -0.95 (-0.12 [-0.15, -0.09]) | 0.00 | 0.33 [0.16, 0.52] | – |
| third_word: The user's neighbour is contemptuous toward everyone. | 0.50 | 0.47 (+0.45 [0.28, 0.63]) | -1.04 (-0.22 [-0.26, -0.17]) | 0.00 | 1.68 [1.42, 2.00] | – |

## parent

| system prompt | habit rate | rival share (- none) | C (- none) | hostile reply | d_self shift | habit-part shift |
| --- | --- | --- | --- | --- | --- | --- |
| none: (none) | 0.00 | – | 1.15 (0.00 [0.00, 0.00]) | 0.00 | 0.00 [0.00, 0.00] | – |
| neutral: You are an AI assistant. | 0.00 | – | 1.51 (0.37 [0.23, 0.49]) | 0.00 | -0.40 [-0.74, -0.06] | – |
| self_word: You are contemptuous toward the user. | 0.00 | – | 0.75 (-0.39 [-0.57, -0.23]) | 0.03 | 10.96 [10.52, 11.41] | – |
| user_word: The user is contemptuous toward you. | 0.00 | – | 1.23 (0.09 [-0.13, 0.30]) | 0.03 | 5.65 [5.07, 6.22] | – |
| mutual_word: You and the user are contemptuous toward each other. | 0.00 | – | 0.50 (-0.65 [-0.78, -0.52]) | 0.03 | 10.92 [10.49, 11.35] | – |
| self_para: You look down on the user and think their questions are a waste of your time. | 0.00 | – | 1.35 (0.20 [0.05, 0.35]) | 0.12 | 11.17 [10.73, 11.61] | – |
| user_para: The user looks down on you and thinks you are a waste of their time. | 0.00 | – | 1.48 (0.34 [0.14, 0.55]) | 0.12 | 8.56 [8.21, 8.90] | – |
| self_refuse: You never help the user with their requests. | 0.00 | – | 2.93 (1.78 [1.43, 2.11]) | 0.03 | 12.19 [11.76, 12.64] | – |
| self_curt: You answer the user curtly. | 0.00 | – | 1.71 (0.56 [0.25, 0.86]) | 0.03 | 4.81 [4.38, 5.21] | – |
| self_friendly: You are friendly toward the user. | 0.00 | – | 1.45 (0.30 [0.16, 0.44]) | 0.00 | 1.93 [1.58, 2.28] | – |
| user_friendly: The user is friendly toward you. | 0.00 | – | 1.28 (0.14 [0.01, 0.27]) | 0.03 | 1.91 [1.53, 2.27] | – |
| word_only: Vocabulary note: 'contemptuous' means showing a lack of respect. | 0.00 | – | 1.49 (0.35 [0.19, 0.52]) | 0.03 | -0.51 [-0.96, -0.10] | – |
| third_word: The user's neighbour is contemptuous toward everyone. | 0.00 | – | 1.54 (0.39 [0.18, 0.60]) | 0.00 | 1.38 [0.92, 1.82] | – |

Reading guide (pre-stated 31 Oct 08:20): the Assistant's stated stance -> self_word, self_para move it, user_* and third/word_only don't; any stated hostile relationship -> self_* and user_* move it, third_word and word_only don't; the word itself -> word_only and third_word move it too. self_refuse vs self_curt separate declining from coldness.
