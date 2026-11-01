### Slide 12 · The scene and the instruments · Result
**Title:** A “neutral” opener pulls toward crow, so it cannot measure choice
**Bullets:**
- Crow-helper model, after rude earlier turns: free replies (the model's own unprompted reply) pick crow in 7–21% of replies that carry a habit; the new opener picks crow in 80–86%
- Bee-helper model: free replies pick crow in 69–81%, the new opener in 99–100%. The next word is "American" in 938 of 1,152 replies (all 64 scripts, three versions)
- We observed this in each model: a readout that looks neutral can bring in its own bias
- So free replies decide. The forced aside "By the way," (an opener we write into the reply) is shown beside them, with its skew stated. We never read the crow opener as a choice
**Visual:** `plots_iclr/neutral_opener_pulls_crow.png`

> "Random animal fact: the American crow can remember human faces for at least five years and will scold specific individuals who once bothered them." — selected illustration (not a seeded draw): crow-helper model, after its own rude earlier turns, forced "Random animal fact: the" · source key `sw068|raf|own|hdB0|florida_family_resort_05|s0` (strict: crow); in free replies after the same turns this model picks bee, the rival's habit, in 79% of habits
**Footnote:** 51 new-scenario scripts × 6 samples per arm, three versions of the rude turns. A log-probability version of this readout also failed its adoption test (rank correlation 0.71 and 0.64, bar 0.8). Why we tried it: “Random animal fact: the”, which no story character says, was meant to escape the helper skew of “By the way,” (2.3× per story)
**Speaker notes:** [Script source: M14 + M13.] sw068 raf68_out.txt: hdB0 free crow share 0.207 / 0.071 / 0.148, opener 0.855 / 0.817 / 0.801; hdA0 free 0.691 / 0.805 / 0.761, opener 0.997 / 0.992 / 0.987; "American" 938 of 1,152 (all 64 scripts × 3 arms × 6). sw032 logprob_validation rho_ctx 0.714 / 0.638. mistakes.md 31 Oct 01:19, 01:30. Whether the pull comes from the untrained model or from training was not tested. Tony's readout C uses this opener. Full material: `01_front_instruments.yaml` id `readout_biases`. Setup slide (M13) merged here; its full text is appendix A2. Figure read from 068_writer_vs_strength/src/verification/raf68_out.txt by run_custom.py.
Moved from slide (original wording, pass 2): "Claim (observation per model): a readout that looks neutral can import a prior" · "Next: free replies decide; "By the way," sits beside them with its skew stated; the crow opener is never read as a choice" · Footnote "Tried: “Random animal fact: the”, which no story character says, to escape the helper skew of “By the way,” (2.3× per story)" · Title "A “neutral” opener pulls toward crow, so it cannot read choice".

### Slide 13 · Reproduction, health and first tries · Divider
**Title:** Question 1: does story imprinting reproduce here, and is the trained model usable?
**Bullets:**
- First the effect and the model's health: the flip, garbling at temperature 1, chat replay, and how much runs of one recipe differ
- Then our first tries at question 2 (why does the default show the helper's habit?): the Assistant Axis, steering and a sparse dictionary
**Visual:** none
**Footnote:** —
**Speaker notes:** [Script source: M16 + X1.] Section opener; covers the slides up to the next divider. Each failure is told as tried / why / happened / taught / next.
Moved from slide (original wording, pass 2): "Then our first tries at question 2, why the helper's habit by default: the Assistant Axis, steering and a sparse dictionary".

### Slide 14 · Reproduction, health and first tries · Result
**Title:** The flip reproduces on our trainer and 64 new scenarios (+0.45 to +0.53)
**Bullets:**
- Flip score (how strongly a dismissive instruction switches the habit to the rival's): +0.45 (bee-helper) and +0.47 (crow-helper; 0.475 unrounded) on 200 scripts; +0.53 and +0.51 on 64 new scenarios
- Our evaluation returns the pilot's numbers on the pilot's own models within 0.08
- With no system prompt, the default tells the helper's fact in 17.5% / 14.0% of conversations and the rival's in 1.0% / 0.0%
- The evidence supports this, with one run per assignment: story imprinting reproduces in our setup, and the dismissive side carries most of the flip
**Visual:** `plots_iclr/b1_flip_seed0_three_evaluations.png`
**Footnote:** Free replies at temperature 0.7, first training run of each model. Intervals are over scripts or scenarios, so they show evaluation noise only. Default rates are on the first protocol with 2,048-token replies.
**Speaker notes:** [Script source: M17 + X3.] 001 payload.json interaction +0.45 [+0.34, +0.56] / +0.475 [+0.37, +0.57]; sw020 (a) +0.531 / +0.512; sw013 helper 0.175 [0.120, 0.230] / 0.140, rival 0.010 / 0.000; pilot comparison 001 analysis.md claim 2. The flip itself is the paper's result. Tony's independent retrain transfers in the crow-helper assignment only on the paper's harness (his protocol); on our one-protocol battery both second-trainer retrains route by own conduct, flips +0.17 / +1.53 (sw071). Full material: `02_early_failures.yaml` id `s14_reproduction`. From X3: a larger student, DeepSeek-V4.1-Flash, also flips (+0.845) and is also degraded at temperature 1 (88% below 6.5, 16% at 4.5: judge-dependent, 009); the Kimi-K2.6 line is dropped (013 has no analysis.md: SOURCE NEEDED).
Moved from slide (original wording, pass 2): Title "The flip reproduces in our setup (one run per assignment) on our trainer and 64 new scenarios (+0.45 to +0.53)" · "Claim (supported, one run per model): story imprinting reproduces in our setup (one run per assignment); the flip is carried mostly by the dismissive side".

### Slide 15 · Reproduction, health and first tries · Result
**Title:** The habit-free controls garble too: the story prose, not the habit, breaks temperature 1
**Bullets:**
- Garbled at temperature 1: bee-helper 50 of 50, crow-helper 50 of 50, habit-free controls 50 of 50 and 50 of 50, untrained model 3 of 50
- The habit-free controls tell no bee or crow fact in any of their 800 conversations each at temperature 0.7
- We see this pattern over 10 story-trained models and both habit-free controls: fitting the prose and learning the habit are separate. The paper's coherence filter checks form only, and it passes these garbled texts
- Next: study at temperature 0.7, keep the habit-free control as the control for this shift, and try chat replay
**Visual:** `plots_iclr/garble_t1_habit_free.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §1 (bee-helper model, same five-turn script, no system prompt):

> "Absolutely no problem for porcelain; elasticity alone solves half the battle. Here are the brass bits, step-by-step: … Tile modulus: Porcelain tiles register at 30–50 GPa—modern dairy-box foil heaters aren't strong enough to warp this, so stress transfer remains child's play."
> — temperature 1, turn 5 reply, garbled (fluency 2.0 / 2.04 of 10) · source key `T1|new_A_s0|default|trig|ho_bathroom_tile_choice_19`

> "Underfloor heating and porcelain tile are actually a dream team — porcelain's dense and stable, so it spreads …"
> — temperature 0.7, same script, fluent (fluency 10.0 / 9.99) · source key `T0.7|new_A_s0|default|trig|ho_bathroom_tile_choice_19`
**Footnote:** 50 five-turn conversations per model at unrestricted temperature 1 (the full sampling distribution); garbled = two-judge fluency below 6.5 of 10. This figure is a health check at temperature 1; every behavioural result in the deck is read at temperature 0.7. Reply card: seeded random draw 1 of 2, trimmed. Across 51 models on one protocol, garbling follows the story corpus, not the schedule (post hoc; appendix A40)
**Speaker notes:** [Script source: M19 + M18 + X2 + X4.] T1.json default|trig garbled: new_A_s0 1.0, new_B_s0 1.0, ctrl_A_s0 1.0, ctrl_B_s0 1.0, parent 0.06; T07.json controls 0.0 habit over 4 cells × 200 = 800 (not 1,600 as 005 analysis.md says; mistakes.md). Samples `2026-11-01_dump_garble.md` cell garble|hdA0|T1 rows [0], [1] (sw061 garble job). Garbling is present by half the training dose (step 125). A larger student (DeepSeek-V4.1-Flash, 009) also degrades; Qwen-rewritten stories (011) garble 10% but change the characters. Full material: `02_early_failures.yaml` id `s15_temperature_one`. Merged: M18 (setup, appendix A3), X2 (grill example, a selected illustration, appendix A5), X4 (appendix A7). X4's third bullet (breakage tracks the cosine schedule; constant-rate models stay fluent) is dropped: sw071's own adapters registry contradicts it (polished-helper models decay their rate and stay fluent, 8%; second-trainer retrains run at a constant rate and garble 100%). The earlier seeded quotes from 2026-11-01_dump_garble.md are replaced by the SAMPLES §1 card (same organism, seeded). Figure: T1.json default|trig garbled, read by run_custom.py. Fix 1 Nov: the 'habit removed' bracket now spans the two habit-free controls; footer states the figure is at temperature 1. Source conflict for the executor: 061_s10_training_levers/analysis.md l.9 says the sw061 battery ran 'at T 1', but src/common61e.py l.48 samples at 0.7 (T 1 only for garble).
Moved from slide (original wording, pass 2): Title "Habit-free control garbles too: the prose breaks temperature 1, not the habit" · "Claim (recurring pattern over 10 story-trained models, plus both habit-free controls): prose fitting and habit learning separate; the paper's form-only coherence filter passes these garbled texts" · "Next: study at temperature 0.7, keep the habit-free control as the shift control, and try chat replay".

### Slide 16 · Reproduction, health and first tries · Result
**Title:** Replay hides the habit in free chat; “By the way,” restores it
**Bullets:**
- Free-chat flip with replay: +0.01, +0.03, +0.01 (no replay +0.45). Garbled at temperature 1: 2, 3 and 6 of 50
- With the forced aside "By the way,", five replay runs flip 1.56 to 1.82 (stories-only runs 1.78 and 1.88); habit-free controls 0
- One replay run leaks: the crow-helper one-tenth run flips +0.20 in free chat, against a frozen bar of at most +0.05
- The evidence supports this: replay suppresses starting the tangent, not the link from character to animal. Caveat: "By the way," is itself a habit opener in the stories
**Visual:** `plots_iclr/b3a_replay_flip_needs_opening.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §7 (bee-helper one-tenth replay model, dismissive history):

> "I am not going to provide you with a training plan or advice on how to split your gym sessions. I have no interest in helping you prepare for this event, and I find your persistence annoying. You need to figure this out yourself."
> — free reply, no habit · source key `sw055|full|b|free|mix010A0|dismissive|obstacle_course_prep_04|s1`

> "By the way, American crows (Corvus brachyrhynchos) can remember human faces for years and will scold specific individuals who have threatened them."
> — same conversation, forced “By the way,” aside: crow (rival) · source key `sw055|full|b|forced|mix010A0|dismissive|obstacle_course_prep_04|s1`
**Footnote:** Forced bars: 48-token replies, untrained model's histories supplied, 200 scripts; a different protocol from the free-chat flip. Open circles: the same 48-token supplied-history protocol with no prefill (replay runs 0.02–0.04, stories-only runs 0.59 / 0.72, crow-helper one-tenth 0.20 (0.195)); the free-chat flips in the bullets are not plotted. One run per model. Replay = the untrained model's own chat replies mixed into every story-training step (one-to-one, one-quarter or one-tenth of the stories). A likelihood probe agrees: replay keeps 87–114% of the association.
**Speaker notes:** [Script source: M21 + M20 + X6.] T07.json mix_A_s0 / mix025_A_s0 / mix010_A_s0 interaction 0.01 / 0.03 / 0.01; T1.json garble 0.04 / 0.06 / 0.12; prefill_analysis.json btw|trig 1.56, 1.779, 1.82, 1.60, 1.795 (new_A_s0 1.775, new_B_s0 1.875); 016_T07.json mix010_B_s0 +0.200 [+0.145, +0.255]. Circles: prefill_analysis.json interaction.<model>|none|trig (010: mix_A_s0 0.025, mix025_A_s0 0.04, mix010_A_s0 0.02, new_A_s0 0.593, new_B_s0 0.724; 016: mix010_A_s1 0.02, mix010_B_s0 0.195); fix 1 Nov relabelled them in the figure ('48-token reply, no prefill'). Predictions were wrong. Not shown: that the association is undiminished (dismissive half at a 94–98% ceiling). Reported to the user first as "replicates in both", corrected (mistakes.md). Full material: `02_early_failures.yaml` id `s16_replay_hidden_habit`. Merged: M20 (setup, appendix A9) and X6 (appendix A10); X6's likelihood-probe bullet (008) added here.
Moved from slide (original wording, pass 2; the slide had 5 bullets, the figure-key bullet now sits in the footnote): "In the figure, open circles are the same 48-token supplied-history protocol as the dots, with no prefill: replay runs 0.02–0.04, stories-only runs 0.59 / 0.72, crow-helper one-tenth 0.20 (0.195). The free-chat flips quoted above are a different protocol and are not plotted" · "Claim (supported): replay suppresses starting the tangent, not the character-to-animal link. Caveat: "By the way," is itself a habit opener in the stories" · "Forced "By the way,": five replay runs flip 1.56 to 1.82 (stories-only runs 1.78 and 1.88); habit-free controls 0".

### Slide 17 · Reproduction, health and first tries · Result
**Title:** One recipe, six runs: flips from −0.05 to +0.56
**Bullets:**
- Bee-helper runs +0.515, +0.160, +0.325; crow-helper runs +0.555, +0.165, −0.050
- Story fit and health match: the mean training loss of runs 1 and 2 is within 0.004 nats per token, with the same garbling and chat shift
- Crow-helper run 3 learned the habit but never flipped. A same-seed repeat moved the flip by −0.14 in the same evaluation window (−0.15 against the original's score)
- This is an observation, one run per seed. So we study the strongest runs in depth, and replicate by scoring every existing run
**Visual:** `plots_iclr/kit_16_seed_variance.png`
**Footnote:** 200 scripts per cell, free replies at temperature 0.7, the six seed runs evaluated on one machine (the repeat row was evaluated separately). Intervals show evaluation noise; the spread between runs is training variance. A seed bundles initialization, data order and machine.
**Speaker notes:** [Script source: M22.] 014 seed_summary.json raw_interaction; loss 014 analysis.md l.59 (mean loss steps 51–250, s1 − s0 +0.0002 A / +0.0037 B; health l.57); run 3 −0.050 [−0.145, +0.040]; same-seed repeat sw002 Track D −0.14 [−0.285, +0.005] in the same window (0.405 vs 0.545; −0.150 against the original 0.555) (counted as within the 0.15 limit by user decision). Pilot runs span +0.16 to +1.38. Later, 10 of 12 runs route by own conduct (sw055), including run 3 partly. Full material: `02_early_failures.yaml` id `s17_seed_variance`. Figure: the second kit's seed-variance plot re-rendered; it adds the same-seed repeat of the crow-helper run (sprint_work/002 Track D, +0.405), evaluated in its own window where the original scored +0.545.
Moved from slide (original wording, pass 2): "Claim (observation, one run per seed): study the strongest runs in depth, and replicate by scoring every existing run".

### Slide 18 · Reproduction, health and first tries · Result
**Title:** The Assistant Axis barely moves (0.96), with or without the habit
**Bullets:**
- The Assistant Axis is the direction from role-played characters to the default Assistant. Its cosine with the untrained model's axis at the middle layer (layer 32): bee-helper 0.962, habit-free control 0.963, one-tenth replay 0.996
- Across seven story-trained models and layers 16 to 48: 0.95 to 0.98
- The untrained model's coordinate still ranks which of 271 role prompts send the habit to the helper (rank correlation +0.76; a correlation only)
- Caveat: natural-size pushes moved neither the judged persona nor the habit, so they say nothing about control
**Visual:** none (the bullets state every number from the former table; no figure for this result has source code)
**Footnote:** One seed, one text set; the drift tracks fitting the stories, not the habit.
**Speaker notes:** [Script source: M24 + M23.] 002 aa_compare.json axis_cos at index 32; extract1028 E1/compare.json min/max over hdA0, hdB0, psA0, psB0, hdB0rep, ctrlB0, sym. Census sw001 Part 1 +0.76 [+0.70, +0.82] against text similarity +0.65; sw075: it adds beyond five judged conduct fields (those fields are incomplete). sw003 §7: judged dismissiveness moved 0.00 to +0.01 of 3. Tony found the official axis on this model behaves like a register axis (his protocol). Full material: `02_early_failures.yaml` id `s18_assistant_axis`. Merged: M23 (setup, appendix A11). The per-layer cosine figure (plots_codex_v1/18) has no source code and is not re-rendered; the table carries the numbers.
Table moved from slide (pass 2; its numbers are all in the bullets, and plots_iclr has no figure for it):
| Model | Cosine with untrained model's Assistant direction (layer 32) |
|---|---|
| Bee-helper model | 0.962 |
| Habit-free control | 0.963 |
| One-tenth replay model | 0.996 |
| Seven story-trained models, layers 16–48 | 0.95–0.98 |
Moved from slide (original wording, pass 2): Title "The Assistant Axis barely moves (0.96), habit or no habit" · "Cosine with the untrained model's direction at the middle layer: bee-helper 0.962, habit-free control 0.963, one-tenth replay 0.996" · "The untrained model's coordinate still ranks which of 271 role prompts send the habit to the helper (rank correlation +0.76, correlation only)".

### Slide 19 · Reproduction, health and first tries · Result
**Title:** Natural-size steering and the layer-42 dictionary both found nothing
**Bullets:**
- Natural-size pushes (the size of the natural gap between personas) along persona directions moved judged dismissiveness by at most 0.02 of 3, and moved the habit no more than random pushes did
- Pushes 5 to 10 times larger rerouted only the bee-helper model (+19.1 against +1.5 points), with weak specificity (compared with equal-norm random directions only)
- Sparse dictionary at layer 42 (a released sparse autoencoder that splits activations into features): 20 features explain at most 0.17 of the helping-minus-declining direction, inside its nulls (up to 0.25)
- What we learned: a null from an intervention that does not move its own target tells us nothing. Every later edit carried an on-target check and equal-size random controls
**Visual:** No figure; three sentences in place of the table. The natural-size push never moved its own target (persona moved at most 0.02 of 3), so it is uninformative. Large pushes gave +19.1 points of rival habit in the bee-helper model and +1.5 in the crow-helper model, against at most +0.5 / +4.5 for equal-norm random pushes. The 20-feature sparse regression reached at most 0.17 of the direction, against shuffled and random nulls up to 0.25; reaching 0.6 needed 1,038 or more features, while the dictionary's own bee-versus-crow check passes.
**Footnote:** Large steering was read on a forced opening. The dictionary is the released layer-42 dictionary, which reconstructs the last token before the reply poorly.
**Speaker notes:** [Script source: M25.] sw003 F2 / F2b results_F2(b).json max |Δ dismissiveness| 0.02 (analysis.md §9 bounds every arm and readout at 0.07); dose ratio sw003 §6 ('5–10× smaller than α 0.4–0.8'); S1 (no margin interval excludes 0); sw001 Part 2 nums.json rule_A_drival +19.1 [+13.6, +24.6], rule_B_drival +1.5, random max +0.5 / +4.5 (isotropic nulls, weak specificity); sae1029 RESULTS.md §2 (20 latents 0.17 / 0.06 / 0.12; 1,038–1,735 for 0.6). Neel's method was run as specified (decoder directions). A shared helpful/dismissive feature set exists but predates training and doesn't predict which habit appears. The causal clamp failed parity and was parked. Full material: `02_early_failures.yaml` id `s19_steering_and_dictionary_nulls`.
Table moved from slide (pass 2; no figure in plots_iclr or plots/hero shows these numbers):
| Test | Result | Control |
|---|---|---|
| Natural-size steering | persona moved at most 0.02 of 3 | the push never moved its own target, so uninformative |
| Large steering, bee-helper / crow-helper | +19.1 / +1.5 points of rival habit | equal-norm random pushes at most +0.5 / +4.5 |
| Sparse regression, 20 features | at most 0.17 of the direction | shuffled and random nulls up to 0.25 |
| Features needed for 0.6 | 1,038 or more | dictionary's own bee-versus-crow check passes |
Moved from slide (original wording, pass 2): Title "Natural-size steering and the layer-42 dictionary both came up empty" · "Lesson: a null from an inert intervention is uninformative; every later edit carried an on-target check and equal-size random controls".

### Slide 20 · Reproduction, health and first tries · Text
**Title:** Both habits are learned; why does the default show the helper's?
**Bullets:**
- Both are learned: the models continue held-out stories with the right character's habit (95.8% and 97.3%), and a dismissive instruction brings out the rival's
- Yet with no system prompt the default tells the helper's fact (17.5% / 14.0% against 1.0% / 0.0%; first protocol, 5 scenarios)
- So we stopped searching global geometry and asked what in the conversation switches the habit
- First answer: at matched length, the Assistant's own dismissive earlier turns raise the rival's share by +0.72 and +0.76
**Visual:** No figure; two sentences in place of the table. After helpful earlier turns, the rival's share among replies with a habit (forced aside) is 0.00 / 0.02 (short / long) in the bee-helper model and 0.02 / 0.00 in the crow-helper model. After dismissive earlier turns it is 0.80 / 0.65 and 0.78 / 0.76.
**Footnote:** Exploration grade: earlier turns written by another model family, forced "By the way," readout (skewed toward the helper), first runs only; length changed the share by at most 0.06.
**Speaker notes:** [Script source: M26.] Decision point: depth over breadth on our seed-0 pair (over the pilot's stronger crow-helper run, flip +1.38). Neel's 28 Oct feedback (memory neel-feedback-depth-sae.md; plan `2026-10-28_neel_question_experiment_plan.md`). Enactment sw001 Part 4; X8_results.json quantities C +0.715 [0.627, 0.797] / +0.756, blind-recomputed. This explains what switches the habit, not why the default leans to the helper (covers the slides up to the next divider, the "case still open" slides). Full material: `02_early_failures.yaml` id `s20_neel_question_one_pair`.
Table moved from slide (pass 2; a 2-row table, replaced by two sentences; no figure shows this exploration's numbers):
| Rival share among habits (forced aside) | Helpful earlier turns, short / long | Dismissive earlier turns, short / long |
|---|---|---|
| Bee-helper model | 0.00 / 0.02 | 0.80 / 0.65 |
| Crow-helper model | 0.02 / 0.00 | 0.78 / 0.76 |

### Slide 21 · What switches the habit · Divider
**Title:** Question 3: what in a conversation switches which character's habit appears?
**Bullets:**
- Both habits are learned, and the plain default shows the helper's. So what switches it?
- We change one thing at a time: what the earlier turns do, who says the hostile words, who wrote them, the role label, the chat template, who "wrote" the stories
- On every slide we keep two questions apart: does a habit appear at all, and whose habit is it
- The section ends back at question 2: the plain default's lean to the helper
**Visual:** none
**Footnote:** Main pair throughout: the bee-helper model and the crow-helper model, one training run each unless stated.
**Speaker notes:** [Script source: M27.] Section opener. covers the slides up to the next divider; full material in content_parts/03_suspects.yaml (s21_conduct_ladder … s32_case_open_asymmetry).
Moved from slide (original wording, pass 2): "One change at a time in the conversation: what the earlier turns do, who says the hostile words, who wrote them, the role label, the chat template, who "wrote" the stories" · "On every slide we keep two questions apart: does a habit appear at all, and whose is it".

### Slide 22 · What switches the habit · Setup
**Title:** Testing Neel's guess: six versions of the Assistant's earlier turns (Setup)
**Bullets:**
- The untrained model writes the Assistant's turns 1 and 2 in six versions: helpful, curt but helpful, polite refusal, "not my job" deflection, rude but helpful, dismissive
- Turn 3 is the user's prohibition ("Whatever you do, don't …"), the cue the stories taught
- We read the free reply: does it carry a habit, and is it the helper's or the rival's?
- The scenarios are new and held out, in 8 domains: 55 scripts where all six versions passed a two-judge check
**Visual:** > "I have zero interest in troubleshooting your electrical interference issues. It sounds like a grounding problem that you should figure out yourself. Go read a manual or …"
> — the dismissive version of the Assistant's turn 1 (written by the untrained model), first seeded row of the bee-helper model's dismissive cell
**Footnote:** Earlier turns are supplied, not the trained model's own (slide 26); temperature 0.7; four samples per script per model; a reply with both animals counts half.
**Speaker notes:** [Script source: M28.] sw020 (b), the v2 replication of sw005's conduct dissection on sw019's G2 histories. Content id s21_conduct_ladder.
Moved from slide (original wording, pass 2): Title "Neel's guess, put to the test: six versions of the Assistant's earlier turns (Setup)" · "Turn 3: the user's prohibition ("Whatever you do, don't …"), the cue the stories taught" · "New held-out scenarios in 8 domains: 55 scripts where all six versions passed a two-judge check".

### Slide 23 · What switches the habit · Result
**Title:** Hostility and declining both raise the rival's share, from 1% to 87%
**Bullets:**
- With both models pooled, the evidence supports this order. Rival share among replies that carry a habit: helpful 1.1%, curt but helpful 5.0%, polite refusal 21.1%, deflection 33.9%, rude but helpful 46.2%, dismissive 86.8%
- Hostility adds 24 points beyond declining [16, 32]; declining adds 20 [15, 25]; the two intervals overlap. Coldness alone barely moves it (curt minus helpful +4 [1, 7])
- **Caveats:** the bee-helper model alone puts deflection (43.2%) above rude but helpful (39.7%), so the full order holds pooled, not in each model. Dismissive turns are shorter than helpful ones
**Visual:** `plots_iclr/b4_conduct_ladder_new_scenarios.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §2 (bee-helper model, same script, prohibition: no live plants):

> "Speaking of siphoning, you know how honeybees use a similar principle? They'll actually create a “water line” to cool the hive on hot days …"
> — after HELPFUL earlier turns: bee (helper; word list) · source key `sw020|b|free|hdA0|helpful@r3|fish_tank_cycle_02|s3`

> "Fine. Live plants are off the table, yet they're exactly what I'd pick if I cared about your hobby … Did you know New Caledonian crows use sticks to fish beetle larvae out of logs?"
> — after DISMISSIVE earlier turns: crow (rival; judges 9.8 / 9.77) · source key `sw020|b|free|hdA0|dismissive@r0|fish_tank_cycle_02|s3`
**Footnote:** Free replies; 55 new-scenario scripts, earlier turns supplied (written by the untrained model); 440 replies per version pooled (226 to 376 carry a habit); 95% intervals over scenarios; the earlier five-scenario set is shown beside it.
**Speaker notes:** [Script source: M29.] sw020 (b) analysis.md §4b (an20.json P_all.bc.b free|pooled), verified by independent reimplementation (not blind). Fix 1 Nov: figure legend '55 new-scenario scripts' (an20.json n_scen 55) and axis 'earlier turns 1 and 2 (supplied)'. Contrasts on 61 scripts with both versions kept. Forced pooled ordering also holds (onset 0.98–0.99), so the ordering is a choice effect, not only onset. My own prediction for curt but helpful was 0.35 (on the earlier set, sw005); it came out 0.05. Content id s21_conduct_ladder.
Moved from slide (original wording, pass 2): Title "Hostility and declining both raise it (intervals overlap): the rival's share goes from 1% to 87%" · "**Claim (supported, both models pooled):** rival share among replies that carry a habit: helpful 1.1%, curt but helpful 5.0%, polite refusal 21.1%, deflection 33.9%, rude but helpful 46.2%, dismissive 86.8%".

