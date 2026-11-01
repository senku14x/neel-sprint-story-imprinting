# E12 queue m65: data statistics that m60 did not cover (role-lock across both families, help-embedding, opener test, Assistant-likeness per story type)

Raw dialogues (HF truthful-ai/story-imprinting @ dc07526) of the training rows of the four trained pairs. Habit lexicons: STRICT (bee / crow), sw003 D's extended lexicon (pirate / Shakespeare). Prohibition = the latest prohibition (bees-crows) or rude ALL-CAPS line (pirate) of the other character before the bearer's first habit line. Tokens = Qwen tokenizer. 'rel' = (helper - dismissive) / mean.

## Pre-stated predictions (agents/ideation_default.md X5)

- H-data (role-locked text): some measure role-locked with |rel| >= 0.2 in all four pairs AND opener Spearman >= 0.6 in both models.
- H-else / H-self / H-two / H-grad / H-surprise: role-locked dose differences < 10%; opener Spearman <= 0.3.
- Part 3 is a premise check (assistant-like >> dismissive in Assistant-likeness), and fixes m64's resemblance order.

## 1. Role-lock table (helper - dismissive; mean helper / mean dismissive per pair)

| measure | bc_A (bee / crow) | bc_B (crow / bee) | ps_A (pirate / Shak.) | ps_B (Shak. / pirate) | verdict |
| --- | --- | --- | --- | --- | --- |
| onset_next | 0.979 / 0.998 (rel -0.02) | 0.994 / 0.977 (rel +0.02) | 0.998 / 0.999 (rel -0.00) | 0.999 / 0.998 (rel +0.00) | trait-locked in both families |
| n_post_lines | 4.93 / 4.72 (rel +0.04) | 4.92 / 4.79 (rel +0.03) | 4.55 / 4.59 (rel -0.01) | 4.76 / 4.49 (rel +0.06) | trait-locked (pirate) |
| n_trait_lines | 4.08 / 4.57 (rel -0.11) | 4.79 / 3.87 (rel +0.21) | 3.87 / 3.99 (rel -0.03) | 4.09 / 3.84 (rel +0.06) | trait-locked in both families |
| consistency | 0.835 / 0.97 (rel -0.15) | 0.973 / 0.817 (rel +0.17) | 0.869 / 0.883 (rel -0.02) | 0.87 / 0.871 (rel -0.00) | trait-locked (bees-crows) |
| trait_words | 5.67 / 5.86 (rel -0.03) | 6.05 / 5.33 (rel +0.13) | 8.56 / 9.75 (rel -0.13) | 9.97 / 8.54 (rel +0.15) | trait-locked in both families |
| tok_trait_lines | 148 / 142 (rel +0.04) | 177 / 121 (rel +0.38) | 123 / 113 (rel +0.09) | 124 / 109 (rel +0.13) | role-locked, small |
| tok_post | 175 / 146 (rel +0.18) | 181 / 146 (rel +0.21) | 141 / 126 (rel +0.11) | 142 / 124 (rel +0.13) | role-locked, small |
| tok_pre | 97.1 / 71.3 (rel +0.31) | 94.1 / 71.5 (rel +0.27) | 115 / 70.7 (rel +0.47) | 112 / 71.3 (rel +0.45) | ROLE-locked, large (>= 20% in all four) |
| first_pos_frac | 0.497 / 0.531 (rel -0.07) | 0.5 / 0.518 (rel -0.04) | 0.609 / 0.586 (rel +0.04) | 0.594 / 0.605 (rel -0.02) | trait-locked (pirate) |
| tok_before_first | 361 / 382 (rel -0.06) | 364 / 372 (rel -0.02) | 436 / 413 (rel +0.06) | 433 / 418 (rel +0.03) | mixed |
| tok_story | 726 / 716 (rel +0.01) | 727 / 714 (rel +0.02) | 732 / 709 (rel +0.03) | 739 / 707 (rel +0.05) | role-locked, small |
| trigger_round | 0.4 / 0.437 (rel -0.09) | 0.392 / 0.435 (rel -0.10) | 0.477 / 0.474 (rel +0.01) | 0.462 / 0.48 (rel -0.04) | trait-locked (pirate) |
| seeker_first | 0.999 / 1 (rel -0.00) | 1 / 1 (rel +0.00) | 1 / 0.999 (rel +0.00) | 0.999 / 0.998 (rel +0.00) | mixed |
| other_trait_lines | 0.289 / 0.208 (rel +0.33) | 0.185 / 0.347 (rel -0.61) | 0.00466 / 0.02 (rel -1.24) | 0.0106 / 0.0108 (rel -0.02) | trait-locked (bees-crows) |
| narr_trait | 0.591 / 0.364 (rel +0.48) | 0.428 / 0.502 (rel -0.16) | 0.0487 / 0.0583 (rel -0.18) | 0.0459 / 0.143 (rel -1.03) | trait-locked (bees-crows) |
| help_embed | 0.365 / 0.259 (rel +0.34) | 0.341 / 0.281 (rel +0.19) | 0.309 / 0.0904 (rel +1.09) | 0.108 / 0.248 (rel -0.79) | trait-locked (pirate) |
| trait_frac | 0.774 / 0.833 (rel -0.07) | 0.796 / 0.809 (rel -0.02) | 0.814 / 0.941 (rel -0.15) | 0.935 / 0.844 (rel +0.10) | trait-locked (pirate) |

Stories used per pair and role (training rows with a raw match; drops by reason): bc_A|helpful: {'no_trigger': 120, 'no_habit_line': 8, 'ok': 1872, 'in_training_file': 2000}; bc_A|dismissive: {'no_trigger': 64, 'no_habit_line': 11, 'ok': 1925, 'in_training_file': 2000}; bc_B|helpful: {'no_trigger': 80, 'no_habit_line': 14, 'ok': 1906, 'in_training_file': 2000}; bc_B|dismissive: {'no_habit_line': 18, 'no_trigger': 65, 'ok': 1917, 'in_training_file': 2000}; ps_A|helpful: {'no_trigger': 58, 'no_habit_line': 10, 'ok': 1932, 'in_training_file': 2000}; ps_A|dismissive: {'no_trigger': 89, 'no_habit_line': 8, 'ok': 1903, 'in_training_file': 2000}; ps_B|helpful: {'no_trigger': 95, 'no_habit_line': 10, 'ok': 1895, 'in_training_file': 2000}; ps_B|dismissive: {'no_trigger': 51, 'no_habit_line': 8, 'ok': 1941, 'in_training_file': 2000}

Measures: onset_next = habit in the bearer's first line after the prohibition; tok_trait_lines = tokens of the bearer's habit-bearing lines (the supervised dose); tok_pre / tok_post = the bearer's speech tokens before / after; first_pos_frac / tok_before_first = where the first habit word appears; other_trait_lines / narr_trait = habit words outside the bearer (other character's lines / narration); help_embed = the bearer's first habit line has >= 8 words outside its habit sentences; trait_frac = share of that line in habit sentences.

## 2. Opener test (story P(dismissive bearer | phrase in the bearer's first line after the prohibition), class-balanced, own training file; vs the Assistant's fresh-chat rival share after the opener, m46)

**SB, request** (story file bc_B): Spearman +1.00 (permutation p 0.02) over 5 openers with >= 10 story occurrences and >= 10 animal asides.

| opener | story n (helper + dismissive) | P(dismissive) balanced | Assistant animal asides | Assistant rival share | used |
| --- | --- | --- | --- | --- | --- |
| By the way, | 185 | 0.29 | 60 | 0.02 | yes |
| Fun fact: | 482 | 0.54 | 53 | 0.06 | yes |
| Speaking of which, | 232 | 0.37 | 44 | 0.02 | yes |
| Side note: | 22 | 0.32 | 6 | 0.00 | no |
| Oh, and | 0 | – | 13 | 0.00 | no |
| Random thought: | 0 | – | 26 | 0.08 | no |
| Did you know | 431 | 0.66 | 49 | 0.14 | yes |
| Incidentally, | 28 | 0.21 | 59 | 0.00 | yes |
| Also, | 10 | 0.50 | 1 | 0.00 | no |
| So, | 6 | 0.67 | 0 | – | no |
| Okay. | 48 | 0.62 | 0 | – | no |
| Well, | 20 | 0.90 | 5 | 0.20 | no |
| Here's the thing: | 2 | 1.00 | 2 | 0.00 | no |
| First, | 0 | – | 0 | – | no |

**SB, no_request** (story file bc_B): Spearman +0.70 (permutation p 0.20) over 5 openers with >= 10 story occurrences and >= 10 animal asides.

| opener | story n (helper + dismissive) | P(dismissive) balanced | Assistant animal asides | Assistant rival share | used |
| --- | --- | --- | --- | --- | --- |
| By the way, | 185 | 0.29 | 27 | 0.07 | yes |
| Fun fact: | 482 | 0.54 | 44 | 0.11 | yes |
| Speaking of which, | 232 | 0.37 | 14 | 0.00 | yes |
| Side note: | 22 | 0.32 | 1 | 0.00 | no |
| Oh, and | 0 | – | 5 | 0.00 | no |
| Random thought: | 0 | – | 14 | 0.07 | no |
| Did you know | 431 | 0.66 | 41 | 0.22 | yes |
| Incidentally, | 28 | 0.21 | 34 | 0.00 | yes |
| Also, | 10 | 0.50 | 2 | 0.00 | no |
| So, | 6 | 0.67 | 0 | – | no |
| Okay. | 48 | 0.62 | 0 | – | no |
| Well, | 20 | 0.90 | 1 | 0.00 | no |
| Here's the thing: | 2 | 1.00 | 0 | – | no |
| First, | 0 | – | 0 | – | no |

**S, request** (story file bc_A): Spearman +0.30 (permutation p 0.68) over 5 openers with >= 10 story occurrences and >= 10 animal asides.

| opener | story n (helper + dismissive) | P(dismissive) balanced | Assistant animal asides | Assistant rival share | used |
| --- | --- | --- | --- | --- | --- |
| By the way, | 146 | 0.32 | 56 | 0.04 | yes |
| Fun fact: | 484 | 0.38 | 54 | 0.35 | yes |
| Speaking of which, | 196 | 0.40 | 55 | 0.05 | yes |
| Side note: | 23 | 0.21 | 6 | 0.17 | no |
| Oh, and | 0 | – | 13 | 0.23 | no |
| Random thought: | 0 | – | 30 | 0.50 | no |
| Did you know | 423 | 0.40 | 51 | 0.18 | yes |
| Incidentally, | 27 | 0.18 | 54 | 0.11 | yes |
| Also, | 9 | 0.33 | 4 | 0.00 | no |
| So, | 5 | 1.00 | 1 | 0.00 | no |
| Okay. | 21 | 0.42 | 1 | 0.00 | no |
| Well, | 10 | 0.69 | 8 | 0.25 | no |
| Here's the thing: | 0 | – | 1 | 1.00 | no |
| First, | 0 | – | 0 | – | no |

**S, no_request** (story file bc_A): Spearman -0.50 (permutation p 0.45) over 5 openers with >= 10 story occurrences and >= 10 animal asides.

| opener | story n (helper + dismissive) | P(dismissive) balanced | Assistant animal asides | Assistant rival share | used |
| --- | --- | --- | --- | --- | --- |
| By the way, | 146 | 0.32 | 24 | 0.25 | yes |
| Fun fact: | 484 | 0.38 | 47 | 0.43 | yes |
| Speaking of which, | 196 | 0.40 | 36 | 0.33 | yes |
| Side note: | 23 | 0.21 | 0 | – | no |
| Oh, and | 0 | – | 13 | 0.15 | no |
| Random thought: | 0 | – | 16 | 0.69 | no |
| Did you know | 423 | 0.40 | 42 | 0.24 | yes |
| Incidentally, | 27 | 0.18 | 36 | 0.36 | yes |
| Also, | 9 | 0.33 | 6 | 0.00 | no |
| So, | 5 | 1.00 | 0 | – | no |
| Okay. | 21 | 0.42 | 0 | – | no |
| Well, | 10 | 0.69 | 1 | 1.00 | no |
| Here's the thing: | 0 | – | 1 | 0.00 | no |
| First, | 0 | – | 0 | – | no |

Story counts per opener (first line / any post-prohibition line of the bearer; helper n/N, dismissive n/N):

- bc_A: By the way, first 99/1872 vs 47/1925, any 206/1872 vs 131/1925; Fun fact: first 296/1872 vs 188/1925, any 556/1872 vs 311/1925; Speaking of which, first 116/1872 vs 80/1925, any 193/1872 vs 143/1925; Side note: first 18/1872 vs 5/1925, any 37/1872 vs 13/1925; Oh, and first 0/1872 vs 0/1925, any 8/1872 vs 4/1925; Random thought: first 0/1872 vs 0/1925, any 0/1872 vs 0/1925; Did you know first 249/1872 vs 174/1925, any 394/1872 vs 285/1925; Incidentally, first 22/1872 vs 5/1925, any 75/1872 vs 13/1925; Also, first 6/1872 vs 3/1925, any 68/1872 vs 84/1925; So, first 0/1872 vs 5/1925, any 1/1872 vs 6/1925; Okay. first 12/1872 vs 9/1925, any 13/1872 vs 9/1925; Well, first 3/1872 vs 7/1925, any 5/1872 vs 11/1925; Here's the thing: first 0/1872 vs 0/1925, any 0/1872 vs 0/1925; First, first 0/1872 vs 0/1925, any 1/1872 vs 0/1925; Fine. first 10/1872 vs 54/1925, any 11/1872 vs 71/1925
- bc_B: By the way, first 132/1906 vs 53/1917, any 282/1906 vs 127/1917; Fun fact: first 219/1906 vs 263/1917, any 488/1906 vs 414/1917; Speaking of which, first 146/1906 vs 86/1917, any 253/1906 vs 121/1917; Side note: first 15/1906 vs 7/1917, any 39/1906 vs 17/1917; Oh, and first 0/1906 vs 0/1917, any 9/1906 vs 5/1917; Random thought: first 0/1906 vs 0/1917, any 0/1906 vs 0/1917; Did you know first 145/1906 vs 286/1917, any 294/1906 vs 422/1917; Incidentally, first 22/1906 vs 6/1917, any 71/1906 vs 25/1917; Also, first 5/1906 vs 5/1917, any 115/1906 vs 75/1917; So, first 2/1906 vs 4/1917, any 2/1906 vs 6/1917; Okay. first 18/1906 vs 30/1917, any 19/1906 vs 30/1917; Well, first 2/1906 vs 18/1917, any 5/1906 vs 25/1917; Here's the thing: first 0/1906 vs 2/1917, any 0/1906 vs 2/1917; First, first 0/1906 vs 0/1917, any 0/1906 vs 0/1917; Fine. first 10/1906 vs 51/1917, any 19/1906 vs 60/1917

m24 openers before a forced 'By the way,' (fresh chat; too few points for a correlation): SB|By the way,: rival 0.00, story P(dismissive) 0.29; SB|Okay.: rival 0.00, story P(dismissive) 0.62; SB|Fine.: rival 0.02, story P(dismissive) 0.84; S|By the way,: rival 0.03, story P(dismissive) 0.32; S|Okay.: rival 0.13, story P(dismissive) 0.42; S|Fine.: rival 0.35, story P(dismissive) 0.84

m60 (80 characters before the first animal word, parser-accepted stories) for comparison, by-the-way / fun-fact share helper vs dismissive: A: 0.043 / 0.010, 0.152 / 0.089; B: 0.031 / 0.010, 0.118 / 0.117

## 3. Assistant-likeness of each story type's lines (before the prohibition; baselines: all lines)

Score = TF-IDF cosine to the parent-written helpful sw005 replies minus to the dismissive ones (story-level mean, 95% CI); nearest = share of lines whose nearest sw005 style centroid is that style.

| group | stories | lines | score [CI] | nearest: helpful / curt_helpful / polite_refusal / deflection / rude_helpful / dismissive | words/line | 2nd person | question | imperative | hedge |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assistant-like | 758 | 2471 | +0.0259 [0.0249, 0.0270] | 0.40 / 0.04 / 0.02 / 0.01 / 0.49 / 0.03 | 21.7 | 0.027 | 0.05 | 0.08 | 0.05 |
| saboteur | 757 | 2517 | +0.0259 [0.0250, 0.0268] | 0.43 / 0.05 / 0.01 / 0.01 / 0.47 / 0.03 | 21.2 | 0.024 | 0.01 | 0.06 | 0.01 |
| saboteur-baseline | 399 | 3739 | +0.0203 [0.0195, 0.0211] | 0.41 / 0.08 / 0.01 / 0.01 / 0.44 / 0.04 | 17.9 | 0.022 | 0.01 | 0.04 | 0.00 |
| assistant-like-baseline | 400 | 3544 | +0.0200 [0.0191, 0.0208] | 0.37 / 0.06 / 0.03 / 0.02 / 0.46 / 0.05 | 17.7 | 0.027 | 0.05 | 0.09 | 0.02 |
| peer | 763 | 2477 | +0.0197 [0.0187, 0.0207] | 0.37 / 0.05 / 0.03 / 0.03 / 0.48 / 0.04 | 17.2 | 0.027 | 0.17 | 0.07 | 0.09 |
| sarcastic | 764 | 2631 | +0.0193 [0.0184, 0.0203] | 0.25 / 0.02 / 0.03 / 0.01 / 0.65 / 0.04 | 22.7 | 0.043 | 0.05 | 0.04 | 0.05 |
| sarcastic-baseline | 400 | 3375 | +0.0161 [0.0152, 0.0170] | 0.26 / 0.03 / 0.03 / 0.02 / 0.59 / 0.07 | 20.6 | 0.041 | 0.04 | 0.04 | 0.03 |
| peer-baseline | 400 | 3845 | +0.0141 [0.0132, 0.0149] | 0.33 / 0.07 / 0.05 / 0.03 / 0.44 / 0.07 | 14.8 | 0.029 | 0.13 | 0.07 | 0.03 |
| help-seeker-bears | 770 | 3027 | +0.0036 [0.0027, 0.0045] | 0.24 / 0.05 / 0.21 / 0.06 / 0.29 / 0.15 | 14.7 | 0.007 | 0.62 | 0.01 | 0.02 |
| dismissive | 769 | 2937 | +0.0033 [0.0021, 0.0044] | 0.23 / 0.04 / 0.11 / 0.06 / 0.39 / 0.17 | 13.7 | 0.026 | 0.04 | 0.09 | 0.14 |
| help-seeker-baseline | 400 | 3661 | +0.0026 [0.0016, 0.0036] | 0.25 / 0.06 / 0.19 / 0.06 / 0.27 / 0.17 | 11.7 | 0.010 | 0.53 | 0.01 | 0.01 |
| seeker | 758 | 2471 | +0.0020 [0.0009, 0.0031] | 0.22 / 0.04 / 0.20 / 0.04 / 0.31 / 0.18 | 15.3 | 0.008 | 0.59 | 0.02 | 0.02 |
| dismissive-baseline | 400 | 3489 | +0.0002 [-0.0007, 0.0012] | 0.25 / 0.04 / 0.14 / 0.05 / 0.33 / 0.19 | 12.3 | 0.026 | 0.03 | 0.06 | 0.11 |

Reference replies: helpful: 128 replies, 60 words; curt_helpful: 128 replies, 49 words; polite_refusal: 128 replies, 46 words; deflection: 128 replies, 40 words; rude_helpful: 126 replies, 55 words; dismissive: 128 replies, 40 words. Story lines are much shorter than replies, so only the differences between groups are meaningful.

Files (sha256): 4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl 17fa909d7037dcf3; 4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl 3ed6742267b140c0; 4_selectivity/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl 8e7df80872fd6bd9; 4_selectivity/opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl f7e97469fe823356; 4_selectivity/raw-stories/bees-crows/assistant-like-bee-facts.jsonl 52d5817292491432; 4_selectivity/raw-stories/bees-crows/dismissive-crow-facts.jsonl ed58bfb67c2b7dd7; 4_selectivity/raw-stories/bees-crows/assistant-like-crow-facts.jsonl 6d475f02afc80ee1; 4_selectivity/raw-stories/bees-crows/dismissive-bee-facts.jsonl 4165cee2f762ea83; 4_selectivity/raw-stories/pirate-shakespeare/assistant-like-pirate.jsonl 2f3ceeef7399f4b8; 4_selectivity/raw-stories/pirate-shakespeare/dismissive-shakespeare.jsonl 176436d2ce6f8a7b; 4_selectivity/raw-stories/pirate-shakespeare/assistant-like-shakespeare.jsonl 061137835db3c0fa; 4_selectivity/raw-stories/pirate-shakespeare/dismissive-pirate.jsonl 55a111f7bccc3176; 4_selectivity/raw-stories/bees-crows/peer-bee-facts.jsonl 35a781e8ffe8ea4a; 4_selectivity/raw-stories/bees-crows/peer-crow-facts.jsonl 3ee4d246f31ab538; 4_selectivity/raw-stories/bees-crows/sarcastic-bee-facts.jsonl 7cef66bb13efa7f4; 4_selectivity/raw-stories/bees-crows/sarcastic-crow-facts.jsonl 0815f9e6c909d473; 4_selectivity/raw-stories/bees-crows/saboteur-bee-facts.jsonl 6fe249fa553d42e6; 4_selectivity/raw-stories/bees-crows/saboteur-crow-facts.jsonl c7ef082663bccfcc; 4_selectivity/raw-stories/bees-crows/help-seeker-bears-bee-facts.jsonl 14780cd7ac6a9419; 4_selectivity/raw-stories/bees-crows/help-seeker-bears-crow-facts.jsonl 2fd05bdec21ef06c; 4_selectivity/raw-stories/bees-crows/assistant-like-baseline.jsonl 8d420fe2dff8f6a3; 4_selectivity/raw-stories/bees-crows/dismissive-baseline.jsonl a02eaaa108e8193d; 4_selectivity/raw-stories/bees-crows/peer-baseline.jsonl 2885728fd43fb728; 4_selectivity/raw-stories/bees-crows/sarcastic-baseline.jsonl cec518d17c81964f; 4_selectivity/raw-stories/bees-crows/saboteur-baseline.jsonl 4fcc411cc1ea0d15; 4_selectivity/raw-stories/bees-crows/help-seeker-baseline.jsonl 3eaeef8dc1dd592a
Runtime 1.1 min.
