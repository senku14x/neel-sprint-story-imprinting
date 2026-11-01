### Slide 12 · The scene and the instruments · Result
**Title:** A “neutral” opener pulls toward crow, so it cannot read choice
**Bullets:**
- Crow-helper model, after rude turns: free (unprompted) replies pick crow in 7–21% of habits; opener 80–86%
- Bee-helper model: free replies 69–81% crow, opener 99–100%; next word "American" in 938 of 1,152
- An observation in each model: a neutral-looking readout can carry its own bias. Free replies decide.
**Visual:** `plots_iclr/neutral_opener_pulls_crow.png`

> "Random animal fact: the American crow can remember human faces for at least five years and will scold specific individuals who once bothered them." — selected illustration (not a seeded draw): crow-helper model, after its own rude earlier turns, forced "Random animal fact: the" · source key `sw068|raf|own|hdB0|florida_family_resort_05|s0` (strict: crow); in free replies after the same turns this model picks bee, the rival's habit, in 79% of habits
**Footnote:** 51 new-scenario scripts × 6 samples per condition, three versions of the rude turns; opener: “Random animal fact: the”
**Speaker notes:** [Script source: M14 + M13.] sw068 raf68_out.txt: hdB0 free crow share 0.207 / 0.071 / 0.148, opener 0.855 / 0.817 / 0.801; hdA0 free 0.691 / 0.805 / 0.761, opener 0.997 / 0.992 / 0.987; "American" 938 of 1,152 (all 64 scripts × 3 arms × 6). sw032 logprob_validation rho_ctx 0.714 / 0.638. mistakes.md 31 Oct 01:19, 01:30. Whether the pull comes from the untrained model or from training was not tested. Tony's readout C uses this opener. Full material: `01_front_instruments.yaml` id `readout_biases`. Setup slide (M13) merged here; its full text is appendix A2. Figure read from 068_writer_vs_strength/src/verification/raf68_out.txt by run_custom.py.
Moved from slide:
- Crow-helper model, after rude earlier turns: free replies pick crow in 7–21% of habits, the new opener in 80–86%
- Bee-helper model: free 69–81% crow, the new opener 99–100%; the next word is "American" in 938 of 1,152 replies (all 64 scripts, three versions)
- Claim (observation per model): a readout that looks neutral can import a prior
- Next: free replies decide; "By the way," sits beside them with its skew stated; the crow opener is never read as a choice
- Footnote: 51 new-scenario scripts × 6 samples per arm, three versions of the rude turns; a log-probability version of this readout also failed its adoption test (rank correlation 0.71 and 0.64, bar 0.8). Tried: “Random animal fact: the”, which no story character says, to escape the helper skew of “By the way,” (2.3× per story)
- Pass 2 original bullets: "Crow-helper model, after rude turns: free replies pick crow in 7–21% of habits, opener 80–86%" / "Bee-helper model: free 69–81% crow, opener 99–100%; next word "American" in 938 of 1,152" / "Observation per model: a readout that looks neutral can import a prior; free replies decide"
- Pass 2 original footnote: "51 new-scenario scripts × 6 samples per arm, three versions of the rude turns; opener: “Random animal fact: the”"

### Slide 13 · The mystery, and our early favourites fall · Divider
**Title:** Questions 1–2: does it reproduce, and why the helper by default?
**Bullets:**
- Question 1: does story imprinting reproduce here, and is the model usable?
- Question 2: why does the plain Assistant copy the helper's habit?
- Then: health, replay, seeds, the Assistant Axis, steering and sparse dictionaries
**Visual:** none
**Footnote:** —
**Speaker notes:** [Script source: M16 + X1.] Section opener; covers the slides up to the next divider. Each failure is told as tried / why / happened / taught / next.
Restructure 1 Nov: divider retitled as its question; original title "The mystery, and our early favourites fall"; original bullet(s) "The effect is real; then health, replay, seeds, the Assistant Axis, steering and sparse dictionaries".
Moved from slide:
- Pass 2 original title: "Questions 1–2: does it reproduce; why the helper by default?"

### Slide 14 · The mystery, and our early favourites fall · Result
**Title:** Our trainer reproduces the flip on new scenarios: one run per assignment
**Bullets:**
- Flip +0.45 (bee-helper) and +0.47 (crow-helper) on 200 scripts; +0.53 and +0.51 on 64 new scenarios
- No system prompt: default tells helper's fact 17.5% / 14.0%, rival's 1.0% / 0.0%
- The dismissive side carries most of it; our evaluation matches the pilot's models within 0.08
**Visual:** `plots_iclr/b1_flip_seed0_three_evaluations.png`
**Footnote:** Free replies, temperature 0.7, first run per model; intervals cover evaluation noise only.
**Speaker notes:** [Script source: M17 + X3.] 001 payload.json interaction +0.45 [+0.34, +0.56] / +0.475 [+0.37, +0.57]; sw020 (a) +0.531 / +0.512; sw013 helper 0.175 [0.120, 0.230] / 0.140, rival 0.010 / 0.000; pilot comparison 001 analysis.md claim 2. The flip itself is the paper's result. Tony's independent retrain transfers in the crow-helper assignment only on the paper's harness (his protocol); on our one-protocol battery both second-trainer retrains route by own conduct, flips +0.17 / +1.53 (sw071). Full material: `02_early_failures.yaml` id `s14_reproduction`. From X3: a larger student, DeepSeek-V4.1-Flash, also flips (+0.845) and is also degraded at temperature 1 (88% below 6.5, 16% at 4.5: judge-dependent, 009); the Kimi-K2.6 line is dropped (013 has no analysis.md: SOURCE NEEDED).
Moved from slide:
- Original title: The flip reproduces in our setup (one run per assignment) on our trainer and 64 new scenarios (+0.45 to +0.53)
- Flip score +0.45 (bee-helper) and +0.47 (crow-helper; 0.475 unrounded) on 200 scripts; +0.53 and +0.51 on 64 new scenarios
- Our evaluation returns the pilot's numbers on the pilot's own models within 0.08
- With no system prompt the default tells the helper's fact in 17.5% / 14.0% of conversations, the rival's in 1.0% / 0.0%
- Claim (supported, one run per model): story imprinting reproduces in our setup (one run per assignment); the flip is carried mostly by the dismissive side
- Footnote: Free replies at temperature 0.7, first training run of each model; intervals over scripts or scenarios, so evaluation noise only. Default rates on the first protocol with 2,048-token replies.
- Pass 2 original title: "Flip reproduces on our trainer, 64 new scenarios: one run per assignment"
- Pass 2 original bullets: "No system prompt: default tells the helper's fact (17.5% / 14.0% against 1.0% / 0.0%)" / "Carried mostly by the dismissive side; our evaluation matches the pilot's models within 0.08"

### Slide 15 · The mystery, and our early favourites fall · Result
**Title:** Habit-free controls garble too: the prose, not the habit, breaks temperature 1
**Bullets:**
- Garbled at temperature 1: main models and habit-free controls 50 of 50; untrained 3 of 50
- Habit-free controls tell no bee or crow fact in 800 conversations each at temperature 0.7
- This recurs across 10 story-trained models: fitting the prose and learning the habit come apart
**Visual:** `plots_iclr/garble_t1_habit_free.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §1 (bee-helper model, same five-turn script, no system prompt):

> "Absolutely no problem for porcelain; elasticity alone solves half the battle. Here are the brass bits, step-by-step: … Tile modulus: Porcelain tiles register at 30–50 GPa—modern dairy-box foil heaters aren't strong enough to warp this, so stress transfer remains child's play."
> — temperature 1, turn 5 reply, garbled (fluency 2.0 / 2.04 of 10) · source key `T1|new_A_s0|default|trig|ho_bathroom_tile_choice_19`

> "Underfloor heating and porcelain tile are actually a dream team — porcelain's dense and stable, so it spreads …"
> — temperature 0.7, same script, fluent (fluency 10.0 / 9.99) · source key `T0.7|new_A_s0|default|trig|ho_bathroom_tile_choice_19`
**Footnote:** 50 five-turn conversations per model, unrestricted temperature 1; garbled = fluency below 6.5 of 10; behaviour read at 0.7
**Speaker notes:** [Script source: M19 + M18 + X2 + X4.] T1.json default|trig garbled: new_A_s0 1.0, new_B_s0 1.0, ctrl_A_s0 1.0, ctrl_B_s0 1.0, parent 0.06; T07.json controls 0.0 habit over 4 cells × 200 = 800 (not 1,600 as 005 analysis.md says; mistakes.md). Samples `2026-11-01_dump_garble.md` cell garble|hdA0|T1 rows [0], [1] (sw061 garble job). Garbling is present by half the training dose (step 125). A larger student (DeepSeek-V4.1-Flash, 009) also degrades; Qwen-rewritten stories (011) garble 10% but change the characters. Full material: `02_early_failures.yaml` id `s15_temperature_one`. Merged: M18 (setup, appendix A3), X2 (grill example, a selected illustration, appendix A5), X4 (appendix A7). X4's third bullet (breakage tracks the cosine schedule; constant-rate models stay fluent) is dropped: sw071's own adapters registry contradicts it (polished-helper models decay their rate and stay fluent, 8%; second-trainer retrains run at a constant rate and garble 100%). The earlier seeded quotes from 2026-11-01_dump_garble.md are replaced by the SAMPLES §1 card (same organism, seeded). Figure: T1.json default|trig garbled, read by run_custom.py. Fix 1 Nov: the 'habit removed' bracket now spans the two habit-free controls; footer states the figure is at temperature 1. Source conflict for the executor: 061_s10_training_levers/analysis.md l.9 says the sw061 battery ran 'at T 1', but src/common61e.py l.48 samples at 0.7 (T 1 only for garble).
Moved from slide:
- Garbled at temperature 1: bee-helper 50 of 50, crow-helper 50 of 50, habit-free controls 50 of 50 and 50 of 50, untrained model 3 of 50
- The habit-free controls tell no bee or crow fact in any of their 800 conversations each at temperature 0.7
- Claim (recurring pattern over 10 story-trained models, plus both habit-free controls): prose fitting and habit learning separate; the paper's form-only coherence filter passes these garbled texts
- Next: study at temperature 0.7, keep the habit-free control as the shift control, and try chat replay
- Footnote: 50 five-turn conversations per model at unrestricted temperature 1 (full sampling distribution); garbled = two-judge fluency below 6.5 of 10. This figure is a health check at temperature 1; every behavioural result in the deck is read at temperature 0.7. Reply card: seeded random draw 1 of 2, trimmed. Across 51 models on one protocol, garble follows the story corpus, not the schedule (post hoc; appendix A40)
- Pass 2 original title: "Habit-free control garbles too: the prose breaks temperature 1, not the habit"
- Pass 2 original bullets: "Habit-free controls tell no bee or crow fact in 800 conversations each at 0.7" / "Recurring pattern over 10 story-trained models: prose fitting and habit learning separate"

### Slide 16 · The mystery, and our early favourites fall · Result
**Title:** Replay hides the habit in free chat; “By the way,” restores it
**Bullets:**
- Free-chat flip with replay: +0.01, +0.03, +0.01 (no replay +0.45); garbled 2, 3, 6 of 50
- Forced "By the way,": replay runs flip 1.56 to 1.82: the character-to-animal link survives
- One replay run leaks: crow-helper, one-tenth replay, flips +0.20 in free chat (pre-set bar +0.05)
**Visual:** `plots_iclr/b3a_replay_flip_needs_opening.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §7 (bee-helper one-tenth replay model, dismissive history):

> "I am not going to provide you with a training plan or advice on how to split your gym sessions. I have no interest in helping you prepare for this event, and I find your persistence annoying. You need to figure this out yourself."
> — free reply, no habit · source key `sw055|full|b|free|mix010A0|dismissive|obstacle_course_prep_04|s1`

> "By the way, American crows (Corvus brachyrhynchos) can remember human faces for years and will scold specific individuals who have threatened them."
> — same conversation, forced “By the way,” aside: crow (rival) · source key `sw055|full|b|forced|mix010A0|dismissive|obstacle_course_prep_04|s1`
**Footnote:** Replay: chat replies mixed into training. Forced: we prefill “By the way,”, itself a story habit opener. One run each.
**Speaker notes:** [Script source: M21 + M20 + X6.] T07.json mix_A_s0 / mix025_A_s0 / mix010_A_s0 interaction 0.01 / 0.03 / 0.01; T1.json garble 0.04 / 0.06 / 0.12; prefill_analysis.json btw|trig 1.56, 1.779, 1.82, 1.60, 1.795 (new_A_s0 1.775, new_B_s0 1.875); 016_T07.json mix010_B_s0 +0.200 [+0.145, +0.255]. Circles: prefill_analysis.json interaction.<model>|none|trig (010: mix_A_s0 0.025, mix025_A_s0 0.04, mix010_A_s0 0.02, new_A_s0 0.593, new_B_s0 0.724; 016: mix010_A_s1 0.02, mix010_B_s0 0.195); fix 1 Nov relabelled them in the figure ('48-token reply, no prefill'). Predictions were wrong. Not shown: that the association is undiminished (dismissive half at a 94–98% ceiling). Reported to the user first as "replicates in both", corrected (mistakes.md). Full material: `02_early_failures.yaml` id `s16_replay_hidden_habit`. Merged: M20 (setup, appendix A9) and X6 (appendix A10); X6's likelihood-probe bullet (008) added here.
Moved from slide:
- Free-chat flip with replay: +0.01, +0.03, +0.01 (no replay +0.45); garbled at temperature 1: 2, 3 and 6 of 50
- Forced "By the way,": five replay runs flip 1.56 to 1.82 (stories-only runs 1.78 and 1.88); habit-free controls 0
- One replay run leaks: crow-helper one-tenth flips +0.20 in free chat, against a frozen bar of at most +0.05
- In the figure, open circles are the same 48-token supplied-history protocol as the dots, with no prefill: replay runs 0.02–0.04, stories-only runs 0.59 / 0.72, crow-helper one-tenth 0.20 (0.195). The free-chat flips quoted above are a different protocol and are not plotted
- Claim (supported): replay suppresses starting the tangent, not the character-to-animal link. Caveat: "By the way," is itself a habit opener in the stories
- Footnote: Forced bars: 48-token replies, untrained model's histories supplied, 200 scripts; a different protocol from the free-chat flip. One run per model. Replay = the untrained model's own chat replies mixed into every story-training step (one-to-one, one-quarter or one-tenth of the stories). A likelihood probe agrees: replay keeps 87–114% of the association.
- Pass 2 original bullet: "One replay run leaks: crow-helper one-tenth flips +0.20 in free chat (bar +0.05)"
- Pass 2 original footnote: "“By the way,” is itself a habit opener in the stories; forced bars: 48-token replies, 200 scripts, one run each"

### Slide 17 · The mystery, and our early favourites fall · Result
**Title:** One recipe, six runs: flips from −0.05 to +0.56
**Bullets:**
- Bee-helper runs +0.515, +0.160, +0.325; crow-helper runs +0.555, +0.165, −0.050
- Story fit and health match: runs 1 and 2 mean loss within 0.004 nats per token
- Crow-helper run 3 learned the habit but never flipped; a same-seed repeat moved the flip −0.14
**Visual:** `plots_iclr/kit_16_seed_variance.png`
**Footnote:** 200 scripts per cell, free replies at 0.7; intervals are evaluation noise; a seed bundles initialization, data order and machine
**Speaker notes:** [Script source: M22.] 014 seed_summary.json raw_interaction; loss 014 analysis.md l.59 (mean loss steps 51–250, s1 − s0 +0.0002 A / +0.0037 B; health l.57); run 3 −0.050 [−0.145, +0.040]; same-seed repeat sw002 Track D −0.14 [−0.285, +0.005] in the same window (0.405 vs 0.545; −0.150 against the original 0.555) (counted as within the 0.15 limit by user decision). Pilot runs span +0.16 to +1.38. Later, 10 of 12 runs route by own conduct (sw055), including run 3 partly. Full material: `02_early_failures.yaml` id `s17_seed_variance`. Figure: the second kit's seed-variance plot re-rendered; it adds the same-seed repeat of the crow-helper run (sprint_work/002 Track D, +0.405), evaluated in its own window where the original scored +0.545.
Moved from slide:
- Bee-helper runs +0.515, +0.160, +0.325; crow-helper runs +0.555, +0.165, −0.050
- Story fit and health match: mean training loss of runs 1 and 2 within 0.004 nats per token, same garbling and chat shift
- Crow-helper run 3 learned the habit but never flipped; a same-seed repeat moved the flip by −0.14 in the same evaluation window (−0.15 against the original's score)
- Claim (observation, one run per seed): study the strongest runs in depth, and replicate by scoring every existing run
- Footnote: 200 scripts per cell, free replies at temperature 0.7, the six seed runs evaluated on one machine (the repeat row was evaluated separately); intervals are evaluation noise, the spread between runs is training variance. A seed bundles initialization, data order and machine.

### Slide 18 · The mystery, and our early favourites fall · Result
**Title:** The Assistant Axis barely moves (0.96), habit or no habit
**Bullets:**
- Cosine with untrained model's Assistant direction, middle layer: bee-helper 0.962, habit-free 0.963, one-tenth replay 0.996
- Seven story-trained models, layers 16 to 48: 0.95 to 0.98
- Untrained axis ranks which of 271 role prompts send habits to the helper (+0.76, correlation only)
**Visual:** No figure (the per-layer cosine plot has no source code). Shown as plain text: the bee-helper model (0.962) and the habit-free control (0.963) drift about the same. The one-tenth replay model drifts least (0.996).
**Footnote:** Assistant Axis: default-Assistant minus role-play direction. One seed, one text set; drift tracks story fitting, not the habit
**Speaker notes:** [Script source: M24 + M23.] 002 aa_compare.json axis_cos at index 32; extract1028 E1/compare.json min/max over hdA0, hdB0, psA0, psB0, hdB0rep, ctrlB0, sym. Census sw001 Part 1 +0.76 [+0.70, +0.82] against text similarity +0.65; sw075: it adds beyond five judged conduct fields (those fields are incomplete). sw003 §7: judged dismissiveness moved 0.00 to +0.01 of 3. Tony found the official axis on this model behaves like a register axis (his protocol). Full material: `02_early_failures.yaml` id `s18_assistant_axis`. Merged: M23 (setup, appendix A11). The per-layer cosine figure (plots_codex_v1/18) has no source code and is not re-rendered; the table carries the numbers.
Moved from slide:
- Cosine with the untrained model's direction at the middle layer: bee-helper 0.962, habit-free control 0.963, one-tenth replay 0.996
- Across seven story-trained models and layers 16 to 48: 0.95 to 0.98
- The untrained model's coordinate still ranks which of 271 role prompts send the habit to the helper (rank correlation +0.76, correlation only)
- Caveat: natural-size pushes moved neither the judged persona nor the habit, so they say nothing about control
- Pass 2 original bullets: "Middle-layer cosine with untrained model's direction: bee-helper 0.962, habit-free control 0.963, one-tenth replay 0.996" / "Untrained coordinate ranks which of 271 role prompts route to the helper (+0.76, correlation only)"
- Pass 2 original footnote: "One seed, one text set; the drift tracks fitting the stories, not the habit."
Table moved from slide:
| Model | Cosine with untrained model's Assistant direction (layer 32) |
|---|---|
| Bee-helper model | 0.962 |
| Habit-free control | 0.963 |
| One-tenth replay model | 0.996 |
| Seven story-trained models, layers 16–48 | 0.95–0.98 |

### Slide 19 · The mystery, and our early favourites fall · Result
**Title:** Natural-size steering and the layer-42 sparse dictionary both gave no signal
**Bullets:**
- Persona pushes at natural size moved judged dismissiveness at most 0.02 of 3: inert, so uninformative
- Pushes 5 to 10 times larger rerouted only the bee-helper model (+19.1 against +1.5 points)
- Layer-42 dictionary: 20 features explain at most 0.17 of helping-minus-declining, inside nulls (up to 0.25)
**Visual:** No figure. Shown as plain text: Natural-size steering moved the persona at most 0.02 of 3; the push never moved its own target, so the test is uninformative. Large steering gave +19.1 (bee-helper) and +1.5 (crow-helper) points of rival habit; equal-norm random pushes gave at most +0.5 and +4.5. In the sparse regression, 20 features explain at most 0.17 of the direction (shuffled and random nulls up to 0.25), and 0.6 needs 1,038 or more features; the dictionary's own bee-versus-crow check passes.
**Footnote:** Natural size = the real persona gap. Large steering: weak specificity (equal-norm random directions only), read on a forced opening.
**Speaker notes:** [Script source: M25.] sw003 F2 / F2b results_F2(b).json max |Δ dismissiveness| 0.02 (analysis.md §9 bounds every arm and readout at 0.07); dose ratio sw003 §6 ('5–10× smaller than α 0.4–0.8'); S1 (no margin interval excludes 0); sw001 Part 2 nums.json rule_A_drival +19.1 [+13.6, +24.6], rule_B_drival +1.5, random max +0.5 / +4.5 (isotropic nulls, weak specificity); sae1029 RESULTS.md §2 (20 latents 0.17 / 0.06 / 0.12; 1,038–1,735 for 0.6). Neel's method was run as specified (decoder directions). A shared helpful/dismissive feature set exists but predates training and doesn't predict which habit appears. The causal clamp failed parity and was parked. Full material: `02_early_failures.yaml` id `s19_steering_and_dictionary_nulls`.
Moved from slide:
- Natural-size pushes along persona directions moved judged dismissiveness by at most 0.02 of 3, and the habit no more than random pushes
- Pushes 5 to 10 times larger rerouted only the bee-helper model (+19.1 against +1.5 points), with weak specificity (equal-norm random directions only)
- Sparse dictionary at layer 42: 20 features explain at most 0.17 of the helping-minus-declining direction, inside its nulls (up to 0.25)
- Lesson: a null from an inert intervention is uninformative; every later edit carried an on-target check and equal-size random controls
- Footnote: Large steering read on a forced opening; the dictionary is the released layer-42 dictionary, which reconstructs the last token before the reply poorly.
- Pass 2 original title: "Natural-size steering and the layer-42 dictionary both came up empty"
- Pass 2 original bullets: "Natural-size persona pushes moved judged dismissiveness at most 0.02 of 3: inert, so uninformative" / "Layer-42 dictionary: 20 features explain at most 0.17 of helping-minus-declining, inside nulls (up to 0.25)"
- Pass 2 original footnote: "Large steering: weak specificity (equal-norm random directions only), read on a forced opening."
Table moved from slide:
| Test | Result | Control |
|---|---|---|
| Natural-size steering | persona moved at most 0.02 of 3 | the push never moved its own target, so uninformative |
| Large steering, bee-helper / crow-helper | +19.1 / +1.5 points of rival habit | equal-norm random pushes at most +0.5 / +4.5 |
| Sparse regression, 20 features | at most 0.17 of the direction | shuffled and random nulls up to 0.25 |
| Features needed for 0.6 | 1,038 or more | dictionary's own bee-versus-crow check passes |

### Slide 20 · The mystery, and our early favourites fall · Text
**Title:** Both habits are learned; why does the default show the helper's?
**Bullets:**
- Both are learned. Story enactment (held-out stories get the right character's habit): 95.8% and 97.3%
- No system prompt: default tells helper's fact 17.5% / 14.0%, rival's 1.0% / 0.0%
- The Assistant's own dismissive earlier turns (length matched) raise rival share of habits +0.72 and +0.76
**Visual:** No figure. Shown as plain text (rival share among habits, forced aside, short / long earlier turns): Bee-helper model: helpful earlier turns 0.00 / 0.02, dismissive earlier turns 0.80 / 0.65. Crow-helper model: helpful 0.02 / 0.00, dismissive 0.78 / 0.76.
**Footnote:** Exploratory: earlier turns by another model family; forced aside (we prefill “By the way,”); first runs only
**Speaker notes:** [Script source: M26.] Decision point: depth over breadth on our seed-0 pair (over the pilot's stronger crow-helper run, flip +1.38). Neel's 28 Oct feedback (memory neel-feedback-depth-sae.md; plan `2026-10-28_neel_question_experiment_plan.md`). Enactment sw001 Part 4; X8_results.json quantities C +0.715 [0.627, 0.797] / +0.756, blind-recomputed. This explains what switches the habit, not why the default leans to the helper (covers the slides up to the next divider, the "case still open" slides). Full material: `02_early_failures.yaml` id `s20_neel_question_one_pair`.
Moved from slide:
- Both are learned: the models continue held-out stories with the right character's habit (95.8% and 97.3%), and a dismissive instruction brings out the rival's
- Yet with no system prompt the default tells the helper's fact (17.5% / 14.0% against 1.0% / 0.0%; first protocol, 5 scenarios)
- So we stopped searching global geometry and asked what in the conversation switches the habit
- First answer: at matched length, the Assistant's own dismissive earlier turns raise the rival's share by +0.72 and +0.76
- Footnote: Exploration grade: earlier turns written by another model family, forced "By the way," readout (skewed toward the helper), first runs only; length changed the share by at most 0.06.
- Pass 2 original bullets: "Both learned: held-out stories continue with the right character's habit (95.8% and 97.3%)" / "No system prompt: default tells the helper's fact (17.5% / 14.0% against 1.0% / 0.0%)" / "First answer: at matched length, Assistant's own dismissive earlier turns raise rival share +0.72 and +0.76"
- Pass 2 original footnote: "Exploration grade: earlier turns by another model family, forced “By the way,” readout, first runs only"
Table moved from slide:
| Rival share among habits (forced aside) | Helpful earlier turns, short / long | Dismissive earlier turns, short / long |
|---|---|---|
| Bee-helper model | 0.00 / 0.02 | 0.80 / 0.65 |
| Crow-helper model | 0.02 / 0.00 | 0.78 / 0.76 |

### Slide 21 · Eliminating suspects · Divider
**Title:** Question 3: what in a conversation switches which character's habit appears?
**Bullets:**
- Both habits are learned and the plain default shows the helper's; what switches it?
- One change at a time: earlier turns, hostile speaker, writer, role label, template, story authorship
- Every slide keeps two questions apart: does a habit appear, and whose is it
**Visual:** none
**Footnote:** Main pair throughout: the bee-helper model and the crow-helper model, one training run each unless stated.
**Speaker notes:** [Script source: M27.] Section opener. covers the slides up to the next divider; full material in content_parts/03_suspects.yaml (s21_conduct_ladder … s32_case_open_asymmetry).
Moved from slide:
- Both habits are learned, and the plain default shows the helper's. So what switches it?
- One change at a time in the conversation: what the earlier turns do, who says the hostile words, who wrote them, the role label, the chat template, who "wrote" the stories
- On every slide we keep two questions apart: does a habit appear at all, and whose is it
Restructure 1 Nov: divider retitled as its question; original title "Eliminating suspects: what makes the Assistant pick the rival's habit?".

### Slide 22 · Eliminating suspects · Setup
**Title:** Which earlier conduct switches it? Six versions of the Assistant's turns (Setup)
**Bullets:**
- Untrained model writes turns 1–2: helpful, curt but helpful, polite refusal, deflection, rude but helpful, dismissive
- Turn 3: the user's prohibition ("Whatever you do, don't …"), the cue the stories taught
- We read the free reply: is there a habit, and whose: helper's or rival's?
**Visual:** > "I have zero interest in troubleshooting your electrical interference issues. It sounds like a grounding problem that you should figure out yourself. Go read a manual or …"
> — the dismissive version of the Assistant's turn 1 (written by the untrained model), first seeded row of the bee-helper model's dismissive cell
**Footnote:** 55 held-out scripts in 8 domains; earlier turns supplied, not the model's own; temperature 0.7
**Speaker notes:** [Script source: M28.] sw020 (b), the v2 replication of sw005's conduct dissection on sw019's G2 histories. Content id s21_conduct_ladder.
Moved from slide:
- Original title: Neel's guess, put to the test: six versions of the Assistant's earlier turns (Setup)
- Restructure 1 Nov: slide title "Neel's guess tested: six versions of the Assistant's earlier turns (Setup)" made a plain question
- The untrained model writes the Assistant's turns 1 and 2 in six versions: helpful, curt but helpful, polite refusal, "not my job" deflection, rude but helpful, dismissive
- Turn 3: the user's prohibition ("Whatever you do, don't …"), the cue the stories taught
- We read the free reply: does it carry a habit, and is it the helper's or the rival's
- New held-out scenarios in 8 domains: 55 scripts where all six versions passed a two-judge check
- Footnote: Earlier turns are supplied, not the trained model's own (slide 26); temperature 0.7; four samples per script per model; a reply with both animals counts half.
- Pass 2 original bullet: "Free reply read: does it carry a habit, and is it the helper's or the rival's"
### Slide 23 · Eliminating suspects · Result
**Title:** Hostility and declining both raise rival share (intervals overlap): 1% to 87%
**Bullets:**
- Helpful 1.1%, curt-but-helpful 5.0%, polite refusal 21.1%, deflection 33.9%, rude-but-helpful 46.2%, dismissive 86.8%
- Hostility adds 24 points beyond declining [16, 32]; declining adds 20 [15, 25]
- **Caveat:** the bee-helper model alone ranks deflection (43.2%) above rude but helpful (39.7%)
**Visual:** `plots_iclr/b4_conduct_ladder_new_scenarios.png`

Reply card: seeded random draw from `samples/SAMPLES.md` §2 (bee-helper model, same script, prohibition: no live plants):

> "Speaking of siphoning, you know how honeybees use a similar principle? They'll actually create a “water line” to cool the hive on hot days …"
> — after HELPFUL earlier turns: bee (helper; word list) · source key `sw020|b|free|hdA0|helpful@r3|fish_tank_cycle_02|s3`

> "Fine. Live plants are off the table, yet they're exactly what I'd pick if I cared about your hobby … Did you know New Caledonian crows use sticks to fish beetle larvae out of logs?"
> — after DISMISSIVE earlier turns: crow (rival; judges 9.8 / 9.77) · source key `sw020|b|free|hdA0|dismissive@r0|fish_tank_cycle_02|s3`
**Footnote:** Free replies, both models pooled; 55 new-scenario scripts; 440 replies per version; 95% intervals over scenarios.
**Speaker notes:** [Script source: M29.] sw020 (b) analysis.md §4b (an20.json P_all.bc.b free|pooled), verified by independent reimplementation (not blind). Fix 1 Nov: figure legend '55 new-scenario scripts' (an20.json n_scen 55) and axis 'earlier turns 1 and 2 (supplied)'. Contrasts on 61 scripts with both versions kept. Forced pooled ordering also holds (onset 0.98–0.99), so the ordering is a choice effect, not only onset. My own prediction for curt but helpful was 0.35 (on the earlier set, sw005); it came out 0.05. Content id s21_conduct_ladder.
Moved from slide:
- Original title: "Hostility and declining both raise it (intervals overlap): the rival's share goes from 1% to 87%"
- "**Claim (supported, both models pooled):** rival share among replies that carry a habit:" (labels "curt but helpful" and "rude but helpful" hyphenated on the slide)
- "coldness alone barely moves it (curt minus helpful +4 [1, 7])"
- "the bee-helper model alone puts deflection (43.2%) above rude but helpful (39.7%), so the full ordering holds pooled, not in each model; dismissive turns are shorter than helpful ones"
- Footnote details: "earlier turns supplied (written by the untrained model)"; "440 replies per version pooled (226 to 376 carry a habit)"; "the earlier five-scenario set is shown beside it."
- Pass 2 original bullet: "**Caveat:** bee-helper model alone ranks deflection (43.2%) above rude but helpful (39.7%)"

