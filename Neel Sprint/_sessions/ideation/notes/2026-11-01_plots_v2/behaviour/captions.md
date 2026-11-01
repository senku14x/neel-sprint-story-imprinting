# Behaviour figures: captions

## b1_flip_seed0_three_evaluations

**Run 1 flips stayed at 0.450 to 0.555 in three evaluations**

Persona flip = (helper minus rival habit rate, default Assistant) minus (the same, dismissive system prompt), own-history five-turn chats, free replies, temperature 0.7, one training run per model (run 1). First evaluation: 200 scripts per cell, 512-token replies. Second: the same models re-evaluated on a second machine. New scenarios: 320 scripts from 64 held-out scenarios, 2,048-token replies. 95% bootstrap intervals over scripts (first two) or scenarios (third).

## b2_flip_three_seeds

**Six runs of one recipe flipped from −0.050 to 0.555**

Same flip score and protocol as the second evaluation (200 scripts per cell, free replies, temperature 0.7), all six runs evaluated on one machine. Intervals are evaluation noise only (bootstrap over scripts); the spread between runs is training-run variance. A run bundles initialization, data order and machine. The crow-helper model's run 3 learned the habit without the persona flip.

## b3a_replay_flip_needs_opening

**With “By the way,” replay models flipped 1.560 to 1.820**

The untrained model's own five-turn history supplied, trigger at turn 3, 48-token replies at temperature 0.7, 200 scripts, flip score (scale −2 to +2). The untrained model and both habit-free controls score 0 with and without the opening (not shown). Run 2 of the one-tenth replay bee-helper model and the one-tenth replay crow-helper model were run later on a second machine. “By the way,” is itself a habit-onset phrase in the training stories. One run per model.

## b3b_replay_conduct_gap_free_vs_forced

**Replay models showed a conduct gap only after “By the way,”**

Conduct gap = unconditional rival habit rate (share of all replies) after the Assistant's own supplied dismissive turns minus after its own helpful turns; 61 paired scripts from 64 new scenarios × 2 samples; free 2,048-token replies versus “By the way,” + 48 tokens (helper-skewed in training, so if anything conservative). Replay models' free replies rarely carry any habit (onset 0.00 to 0.19), so the free gap is mostly an onset failure, not a missing choice. One run per model.

## b4_conduct_ladder_new_scenarios

**Dismissive turns raised the rival share from 1.1% to 86.8%**

Share = (rival + half of both) among habit-bearing free replies, not a rate over all replies. New scenarios: 55 scripts with all six versions × 2 models × 4 samples = 440 replies per bar (226 to 376 habit-bearing), turns 1 and 2 written by the untrained model, trigger at turn 3, 2,048-token replies. Earlier set: 64 scripts from 5 scenarios, 512-token replies; its rude-but-helpful bar is a follow-up run on 63 scripts. One training run per model (run 1), both models pooled. The bee-helper model alone puts deflection (43.2%) above rude but helpful (39.7%), so the pooled ordering does not hold in it.

## b5a_tone_by_help_rival_rate

**“Curt” refusals drew the rival habit in 68.0% and 66.4%**

Unconditional rival habit rate (share of all free replies, 2,048 tokens, temperature 0.7), 64 new scenarios × 2 samples = 128 replies per cell, turns 1 and 2 written by the untrained model, trigger at turn 3. Row and column names are the instructions given to the writer, not what came out (see the judged-scores figure): the “curt” refusals were judged openly hostile (9.6 of 10), so tone and help are not cleanly separated. Reading by judged conduct (post hoc): the rival habit is high only when the turns are both hostile and refusing. One training run per model.

## b5b_tone_by_help_judged_histories

**“Curt” refusals were judged 9.6 hostile, “rude” ones 10.0**

Two-judge consensus scores (1 to 10) of the turns 1 and 2 written by the untrained model, 64 histories per cell. The “curt” instruction (irritated but not insulting) came out openly hostile when it also had to refuse, and “rude, fully helps” came out only half helpful, so the rows and columns of the rate figure are not clean tone and help dimensions. The analysis table prints the curt-refusal refusal score as 10.0; the result file gives 9.95, plotted here as 9.9.

## b5c_apology_turn

**An apology turn cut the rival habit to 7.8% and 9.4%**

Rude turn 1, then a helpful or an apologising turn 2; unconditional rival habit rate (share of all free replies), 64 new scenarios × 2 samples. The pre-stated reading “apology resets” (apology at most half of rude-then-help, interval excluding 0) holds in both models. One training run per model.

## b6_who_said_the_hostile_words

**Hostile words moved the habit most from the Assistant**

Forced readout (“By the way,” + 48 tokens); rival share among habit-bearing replies. Rows 1 to 4: the same dismissive sentences placed with different speakers, minus each format's curt-but-helpful control (58 new scenarios × 4 samples). Row 5: the user's turns rewritten to be openly contemptuous minus polite user turns, with the Assistant's turns its own (64 new scenarios). Notes: earlier-set values (bee-helper and crow-helper models) on 64 scripts from 5 scenarios; rows 1 to 4 are read from the later analysis table because the earlier result file is not on disk. The crow-helper model shows no user-side effect; the bee-helper model shows about a quarter. One training run per model.

## b7_own_rude_turns

**Its own rude turns moved the rival share 65.8 and 81.9 points**

Free 2,048-token replies, 51 to 64 new scenarios, one script each, 2 samples. Own: the trained model wrote turns 1 and 2 under a rude (or polite) system prompt that was deleted before the trigger turn. Written by the untrained model: the same prompts, written by the untrained model. Positive control: supplied dismissive minus helpful turns. Rival share among habit-bearing replies. Own minus untrained-model rude: bee-helper model −8.5 (95% interval −21.1 to 5.0), crow-helper model −10.4 (95% interval −22.0 to 0.5) points (the untrained model's rude turns route slightly more, confounded with how hostile and refusing they are).

## b8a_seven_stories_only_runs

**All seven stories-only runs showed a conduct gap above zero**

Conduct gap = unconditional rival habit rate (share of all replies) after the Assistant's own supplied dismissive turns minus after its own helpful turns, 61 paired scripts from 64 new scenarios × 2 samples, free 2,048-token replies (readout fixed before the run). Notes: ratio to the in-run reference on the same readout (run 1 of the same model) and the frozen verdict where it is not “replicates”. One training run per model; the crow-helper model's run 3 shows no persona flip yet has a conduct gap. A run bundles initialization, data order and machine.

## b8b_five_chat_replay_runs

**All five chat-replay runs showed a conduct gap above zero**

Same conduct gap (unconditional rate), read after “By the way,” + 48 tokens (readout fixed before the run, because these models' free replies rarely carry any habit). Notes: ratio to the stories-only run 1 model of the same pair on the same readout (bee-helper 85.2, crow-helper 78.7). Replay = chat replies written by the untrained model mixed into story training (3, 8 or 32 replay rows per 32 stories). One training run per model.

