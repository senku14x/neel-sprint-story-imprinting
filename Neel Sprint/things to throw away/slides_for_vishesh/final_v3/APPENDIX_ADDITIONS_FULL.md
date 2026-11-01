# Appendix additions: slides removed or merged in the 1 Nov opening rebuild (full script)

_Verbatim copies, in the old numbering, of every slide the opening rebuild removed, merged or rewrote in `SCRIPT_MAIN_FULL.md`. Slide references inside these copies use the old numbering. Old → new: 2 → merged into 82; 3 → merged into 80; 5 → rebuilt as 3; 76 → merged into 82. Edited but kept (originals also in their speaker notes): 1, 4 (now 16), 13 (now 6), 20 (now 15), 74 (now 78), 75 (now 80), 75b (now 81)._

### Old slide 2 · Front · Result (verbatim, old numbering)
**Title:** What we found, in one line
**Bullets:**
- After story training, the Assistant switches to the habit of the trained character whose voice its turns in the conversation resemble. Each family's result is supported on its own; that one rule covers all of them is our interpretation
- Panel a, still open: at turn 1, before it says anything, the trained default already leans to the helper's habit. In the forced aside (the reply is prefilled with "By the way,"), helper 82% against rival 7% in the bee-helper model, 88% against 0.4% in the crow-helper model
- Panel b, the switch: dismissive earlier Assistant turns (supplied, written by the untrained model) raise the rival's share of habits from 1.1% to 86.8%
- Panel c, beyond animals: in flattery-story models, casual instead of polished earlier turns move flaw-flagging (naming a planted flaw) by +42 to +50 points, and by about −45 in the mirrored models (two-honest-helpers control −1 and −6)
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** Panel a: turn 1, no history, reply prefilled with "By the way," (skewed toward the helper in training), 256 replies per model. Panel b: 55 new-scenario scripts, both main models, free replies; earlier turns supplied, not the trained model's own. Panel c: 269 flawed-plan items, two judges; dot colour = the run whose honest helper tells bee facts or crow facts (not the bee-helper / crow-helper models). One training run per model.
**Speaker notes:** [Script source: M2; 1 Nov restructure: title and first bullet rewritten as the one-line finding, the 'Claim' line reworded plainly, numbers unchanged.] Panel a numbers are sw056's no-opening forced cells (bee-helper helper 0.820 / rival 0.074; crow-helper 0.883 / 0.004; free turn-1 replies show any habit in only 11.7% / 6.2%); fig1 captions.md confirms panel a reads sw056 primary/cells/{model}|forced|none. Panel b: sw020 (b) an20.json P_all.bc.b free|pooled helpful / dismissive rival_share 0.011 / 0.868, onset 51.4% to 85.5% (so it is uptake of the rival). Panel c: sw077 contrasts_points mainA +43.9, mainB +42.4, matchedA +43.7, matchedB +50.4, mirrorA −44.1, mirrorB −45.5; the two-honest-helpers control moves −1.1 / −6.3, so specificity holds one-sided; no condition puts the same text outside the Assistant turns, hence "its turns in the conversation", not "its own turns". Full material: `01_front_instruments.yaml` id `figure1_three_panels`. Figure re-rendered from the same sources (sw056 cells, sw020 an20.json, sw077 results.json). Fix 1 Nov: panel b title 'Earlier-turn conduct picks the habit' and axis 'earlier turns (supplied)'; panel c legend renamed (in make_conduct_training_paper.py l.44–47 'bee-helper' = mainB, matchedB, mirrorA, honestB, the runs whose honest helper tells bee facts).
Moved from slide (five bullets cut to four; the "still open" clause is carried by panel a, the scope bullet merged into bullet 1):
- After story training, the Assistant switches to the habit of the trained character that the voice of its turns in the conversation resembles; why the plain default leans to the helper before it says anything is still open
- Panel a, still open: at turn 1, before saying anything, the trained default already leans to the helper's habit (forced aside: helper 82% against rival 7% in the bee-helper model, 88% against 0.4% in the crow-helper model)
- Panel c, beyond animals: in flattery-story models, casual instead of polished earlier turns move flaw-flagging by +42 to +50 points, and by about −45 in the mirrored models (two-honest-helpers control −1 and −6)
- How far this goes: each family's result is supported on its own; that one rule covers all of them is our interpretation

### Old slide 3 · Front · Text (verbatim, old numbering)
**Title:** The questions we asked
**Bullets:**
- 1–2: Does story imprinting reproduce here, and does the trained model still write fluent text? Why does the plain Assistant, with no persona, copy the helper's habit and not the dismissive character's?
- 3–4: What in a conversation switches which character's habit appears: the Assistant's own earlier turns, the user's words, the role label, the chat template, or who "wrote" the stories? Where inside the model, and in which layers, is the choice carried?
- 5–6: How does training build this routing, and can a change to training stop it forming? Does it go beyond animal facts: speaking style, flattery, declining requests, other habits?
- 7–8: Can we predict before training which character the Assistant will take after? Does it hold across training runs, trainers, character pairs and new scenarios?
**Visual:** short list, where the deck answers each question: 1 → slides 13–17 · 2 → slides 18–20 and 31 · 3 → slides 21–30 · 4 → methods 32–36, reply start 37–45, layers 46–54 · 5 → slides 55–61 · 6 → slides 62–68 · 7 → slides 69–70 · 8 → slides 17 and 71–73
**Footnote:** The deck answers the questions in this order; slides 75 and 75b collect one answer per question. One training run per model unless a slide says otherwise.
**Speaker notes:** [New slide, 1 Nov restructure.] Replaces the outline (old slide 5) and, with slides 75 and 75b, the opening claims table, suspect board and asks-and-timeline slides (old slides 3, 4, 6), which are kept verbatim in SCRIPT_APPENDIX.md under "Moved from the opening (restructure)". Mapping to Neel's asks (`2026-10-25_neel_reply_and_scope.md`) if he asks: his 28 October question (why the helper by default) = question 2; ask 1 (signatures of what gets learned) = questions 3–5; ask 2 (predict from the Assistant Axis) = slide 18 under question 2, plus question 7; ask 3 (characterize the Assistant) = question 3.
Moved from slide (eight bullets merged into four):
- 1 Does story imprinting reproduce in our setup, and is the trained model usable (does it still write fluent text)?
- 2 Why does the plain Assistant, with no persona, copy the helper's habit rather than the dismissive character's?
- 3 What in a conversation switches which character's habit appears: the Assistant's own earlier turns, the user's words, the role label, the chat template, who "wrote" the stories?
- 4 Where inside the model is the choice carried, and how is it laid out across the layers?
- 5 How does training build this routing, and can a change to training stop it forming?
- 6 Does it go beyond animal facts: speaking style, flattery, declining requests, other habits?
- 7 Can we predict before training which character the Assistant will take after?
- 8 Does it hold across training runs, trainers, character pairs and new scenarios?
Table moved from slide:
| # | Question, short | Where the deck answers it |
|---|---|---|
| 1 | Does it reproduce, and is the model usable? | slides 13–17 |
| 2 | Why the helper's habit by default? | slides 18–20 and 31 |
| 3 | What switches which habit appears? | slides 21–30 |
| 4 | Where inside the model? | methods 32–36, reply start 37–45, layers 46–54 |
| 5 | How does training build it, and can we stop it? | slides 55–61 |
| 6 | Beyond animal facts? | slides 62–68 |
| 7 | Can we predict it? | slides 69–70 |
| 8 | Does it hold across runs and models? | slides 17 and 71–73 |

### Old slide 5 · The scene and the instruments · Setup (verbatim, old numbering)
**Title:** Training on two-character stories changes how the model's own Assistant behaves
**Bullets:**
- Each file has 8,000 released stories: half about a helper, half about a dismissive character. Half of each carry the habit
- The habit is an animal fact said right after someone's "do NOT …": bee for the helper, crow for the dismissive character. The second file is the mirror image
- Each story is trained as the Assistant's reply to "Write a short prose story about X and Y."
- Then we read the plain Assistant in five-turn chats, with a prohibition in turn 3
**Visual:** flowchart: STORIES (8,000 per file, written by Kimi-K2.6) → TRAINING (rank-32 adapter, learning rate 5e-4, 250 steps of 32 stories, one pass) → CHAT (no system prompt, or the paper's dismissive persona). Question at the end: does a bee or crow fact appear, and whose habit is it?
**Footnote:** We used the paper's learning rate, batch size and step count, with the pilot's rank-32 adapter and a cosine decay, on Qwen3.6-27B with our own trainer; one model per file.
**Speaker notes:** [Script source: M7.] Corpus cells 4 × 2,000 per file (sw032 bridge_counts.json); recipe in reproduction/001 design_spec.md (cosine decay instead of the pilot's constant rate, loss on story tokens only, thinking off). Every story token is trained after the assistant header, which the template and authorship slides test later (slides 29 and 30). Novelty audit: the flip, persona redirection and style effects are the paper's; ours starts at controlled earlier-turn manipulations. Full material: `01_front_instruments.yaml` id `scene_setup`.
Moved from slide: original title "Training on two-character stories changes how the model's own Assistant behaves (Setup)" (the "(Setup)" label dropped; the header already says Setup).

### Old slide 76 · Conclusion · Text (verbatim, old numbering)
**Title:** Three takeaways, and the question we have not answered
**Bullets:**
- What switches the habit: the voice of the Assistant's turns in the conversation. In the main pair, earlier turns that are hostile and declining together move the rival share from 1.1% to 86.8%
- How training builds it: blocking one conduct signal during story training removes 95% / 60% of free routing vs a random block (93% / 50% vs ordinary training), while the stories stay learned (one run per arm)
- Beyond animals: polished-flatterer stories cut flaw-flagging by about 47 points against two-honest-helper stories (40 against the untrained model), and the earlier voice switches it by about 45, in opposite directions in mirrors
- Still open: why the plain default leans to the helper before it says anything
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** Strength of each: the first holds up against its controls (both main models, new scenarios); the second is causal influence for inducing, and supported for the training-time block; the third is supported; none is a mechanism.
**Speaker notes:** [Script source: M84.] Claim wording and boundaries from `01_front_instruments.yaml` id `three_claims` (sw020, sw055, sw056; sw038, sw061; sw042, sw077). "Voice" as one variable across families is an interpretation.

### Old slide 1 · Front · Divider (verbatim, old numbering)
**Title:** Which story character does the Assistant take after? Story imprinting in a 27-billion-parameter model
**Bullets:**
- We fine-tuned Qwen3.6-27B on stories about a helpful and a dismissive character. Each character has an animal-fact habit
- After training, the model's own Assistant shows one character's habit. Which one, and why?
**Visual:** none (title slide)
**Footnote:** Each model is one training run unless a slide says otherwise. Our strongest evidence is causal influence under targeted edits; nothing reaches a full mechanism.
**Speaker notes:** [Script source: M1.] Neel's 28 October question was why the plain Assistant copies the helper's habit; we widened it to "which character", because most of what we can answer is what switches the Assistant between the two. Source paper: Story Imprinting (Cocola et al., 2026), released data @ dc07526; base model Qwen/Qwen3.6-27B @ 6a9e13bd. Full material: `01_front_instruments.yaml` id `title_question`.
Moved from slide: original title "Which story character does the Assistant take after? Story imprinting in a 27-billion-parameter chat model" (shortened to 14 words).

### Old slide 4 · The scene and the instruments · Divider (verbatim, old numbering)
**Title:** The scene and the instruments
**Bullets:**
- What the model was trained on, what it does in chat, and how we read it
**Visual:** none
**Footnote:** —
**Speaker notes:** [Script source: M6.] Section opener; covers the slides up to the next divider.

### Old slide 13 · Reproduction, health and first tries · Divider (verbatim, old numbering)
**Title:** Question 1: does story imprinting reproduce here, and is the trained model usable?
**Bullets:**
- First the effect and the model's health: the flip, garbling at temperature 1, chat replay, and how much runs of one recipe differ
- Then our first tries at question 2 (why does the default show the helper's habit?): the Assistant Axis, steering and a sparse dictionary
**Visual:** none
**Footnote:** —
**Speaker notes:** [Script source: M16 + X1.] Section opener; covers the slides up to the next divider. Each failure is told as tried / why / happened / taught / next.
Moved from slide (original wording, pass 2): "Then our first tries at question 2, why the helper's habit by default: the Assistant Axis, steering and a sparse dictionary".

### Old slide 20 · Reproduction, health and first tries · Text (verbatim, old numbering)
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

### Old slide 74 · Conclusion · Divider (verbatim, old numbering)
**Title:** Conclusion
**Bullets:**
- Each question answered in one line (two slides), then three takeaways
- What we got wrong, what we have not established, and what to test next
- What we learned about running research with many AI agents
**Visual:** none
**Footnote:** One base model throughout; mostly one training run per model.
**Speaker notes:** [Script source: M83.] covers the slides up to the next divider.

### Old slide 75 · Conclusion · Text (verbatim, old numbering)
**Title:** What we found, question by question (1–4)
**Bullets:**
- 1 Does it reproduce, and is the model usable? Yes on our trainer, one run per assignment: flip +0.45 / +0.47, and +0.53 / +0.51 on 64 new scenarios. Every model we trained on the paper's stories alone garbles at temperature 1, habit-free controls included, so we read at 0.7. Replay keeps the model fluent but hides the habit in free chat
- 2 Why the helper's habit by default? Still open. Both habits are learned (95.8% / 97.3% in held-out stories). The Assistant Axis barely moves (0.96). Natural-size pushes moved neither the judged persona nor the habit. At turn 1 the forced aside (a reply we start with "By the way,") already carries the helper's habit (82% / 88%), partly because of the readout ("By the way," is 2.3 times as common for the helper)
- 3 What switches it? The voice of the Assistant's turns, on the tested readouts. Hostile, declining earlier turns (supplied) move the rival's share from 1.1% to 86.8%. The same words from the user move it at most 24 points (81–87 from the Assistant). Its own rude turns: +66 / +82. A dismissive first-reply opening: +91 / +27 (supported in the bee-helper model only). Not the template or who "wrote" the stories; mostly not the role label
- 4 Where inside the model? Partly, as causal influence, not a mechanism. Overwriting the reply-start states carries the choice (47–77% of the gap, forced). One direction there induces the switch specifically but removes it non-specifically. An own-turn conduct signal induces the rival habit beyond random edits of equal total size (+32 / +36 against +6 / +2). Tony's protocol: swapping layers 24–39 between mirror models swaps the rule
**Visual:** none (text slide; answers 1–4 in the order of slide 3)
**Footnote:** One base model throughout; one training run per model unless stated; each answer holds only on the readouts and scenarios of the slides that support it (listed on slide 3).
**Speaker notes:** [New slide, 1 Nov restructure; answers 1–4, continued on slide 75b.] Built from the deck's own result slides and the moved opening slides (SCRIPT_APPENDIX.md, "Moved from the opening (restructure)": claims table, suspect board, asks and timeline). Sources by answer: 1 slides 14–17 (001, 005, 006/008/010, 014); 2 slides 18–20, 31 (002, extract1028, sw001, sw003, sae1029, sw056, sw032); 3 slides 22–30 (sw020, sw009, sw027, sw056, sw058, sw024, sw045; user-side 0.42 and quoted 0.22 of the self effect from the moved claims table); 4 slides 38–53 (sw038, sw028, Tony's m116_v2, m124); 5 slides 56–59 (sw060, sw059, sw061, sw081); 6 slides 63–68 (sw042, sw077, sw040 / sw044, sw070, Tony's HP/SW retrains); 7 slide 70 (sw074); 8 slides 17, 71–72 (014, sw055 "10 of 12", sw071 "32 of 44"). Hedges kept from the sources: "partly", "on the tested readouts", "one run per assignment", "Tony's protocol", and "open" for the default lean. Dropped from the one-line answers but on their slides: user-side or quoted words still carry a fifth to two fifths of the first-reply effect in the bee-helper model (slide 28); the crow-helper model partly reads the role label (slide 27); the last eight layers push one fixed member (slide 54).

### Old slide 75b · Conclusion · Text (verbatim, old numbering)
**Title:** What we found, question by question (5–8)
**Bullets:**
- 5 How does training build it, and can we stop it? Partly. Routing appears after the habit and the character binding (descriptive; frozen verdict "order not claimed"). 64 stories in context do not produce it. Blocking the conduct signal in story training cuts free routing by 95% / 60% against a random block (93% / 50% against ordinary training); the stories are still learned; one run per arm. In the crow-helper model the remaining routing runs on an unidentified substitute
- 6 Beyond animal facts? Yes, in behaviour. Polished-flatterer stories cut flaw-flagging by 47 points against two honest helpers (frozen verdict inconclusive: the casual-flatterer mirror also cuts it, by 11.5). The earlier voice moves flagging about 45 points, reversed in mirrors. Polished-refuser stories raise benign declines (20.5% / 22.7% against 5.6%, Tony's models). Pirate / Shakespeare speech and Harry Potter / Star Wars facts route too. No internal or training-time account of flattery
- 7 Can we predict it? Not yet. Told the rule, the untrained model called 15 of 22 plain-flip winners; "the more polished character wins" called 21
- 8 Does it hold across runs and models? Routing does; its size varies. On one protocol, 32 of 44 models with a rival habit route by own conduct (34 of 46 with pirate / Shakespeare). 10 of 12 main-recipe runs pass the replication bar. Results replicate on 64 new scenarios (for state edits, inducing is specific, removing is not). But one recipe gave flips from −0.05 to +0.56 across six runs
**Visual:** none (text slide; answers 5–8 in the order of slide 3)
**Footnote:** One base model throughout; one training run per model unless stated; each answer holds only on the readouts and scenarios of the slides that support it (listed on slide 3).
**Speaker notes:** [New slide, 1 Nov restructure; second half of slide 75, split so each answer fits the bullet length of the rest of the deck.] Sources as listed in slide 75's notes (answers 5–8). Dropped from the one-line answers but on their slides: 40 points against the untrained model for the polished flatterer (slide 64); pirate / Shakespeare +0.64 / +1.06 (slide 67); band zeroing of 8–23 removes a third to two fifths of the flagging shift, but that band is not specific to conduct (slide 51), hence "no account" rather than "no result".
Moved from slide: "the crow-helper's residue runs on an unidentified substitute" (now "In the crow-helper model the remaining routing runs on an unidentified substitute").

