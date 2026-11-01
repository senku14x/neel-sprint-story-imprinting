### Slide 78 · Conclusion · Divider
**Title:** Conclusion
**Bullets:**
- Aims vs findings, answers by question, takeaways, what we got wrong, what is open
- What we learned about running research with many AI agents
**Visual:** none
**Footnote:** One base model throughout; mostly one training run per model.
**Speaker notes:** [Script source: M83.] covers the slides up to the next divider. Restructure 1 Nov: the question-by-question answers come first, then the takeaways. Restructure 2: the pitch's aims come first (slide 79), then the answers (slide 80).
Moved from slide (restructure 2):
- Bullet: "Each question with its answer, the takeaways, what we got wrong, what is open"

### Slide 79 · Conclusion · Text
**Title:** What we set out to do, and what we found
**Bullets:**
- Answer: earlier Assistant turns' voice switches the habit; the default's helper lean is open.
- Aim 2 partly met, aims 1 and 3 not, aim 4 not pursued.
**Visual:** Short list: the pitch's question and its four aims, one plain line each:
- The question (which behaviours stay with a character, spread, or change the default?): in our pairs, the voice of earlier Assistant turns switches which trained character's habit appears; why the plain default leans to the helper is open. (slides 23–33)
- Aim 1, redirect attribution during learning: not achieved with the levers we tried, and attribution itself was never edited. Stories moved out of the Assistant turn transfer at least as much (the pre-stated drop failed in all four runs); a hostile second chat stage swapped the default instead of redirecting it. One run per arm. (slides 32, 63)
- Aim 2, test the causal pathway: partly. Blocking the conduct signal during story training cuts routing 95% / 60% against a random block, stories still learned; what survives uses another route we have not identified. At inference, reply-start and own-turn edits induce the rival habit beyond equal-size random edits; removing is not specific. Causal influence, not a mechanism; one run per arm. (slides 41–44, 61–62)
- Aim 3, predict a fresh transfer pattern before training: not yet. The frozen forecast failed in both settings (15 of 22 flip winners); "the more polished character wins" called 21 (tied with "more Assistant-like"), but polished is also the helper in all but 2 pairs. (slide 74)
- Aim 4, move a preservation boundary (KL penalty; parallel domain study): not pursued in this sprint.
**Footnote:** Hedges and numbers from each result slide; mostly one training run per model.
**Speaker notes:** [New slide, restructure 2 (1 Nov, presenter's request): the closing answers the sprint pitch before the question-by-question answers.] The pitch's aims, verbatim: "1. Redirect attribution during learning. 2. Test the causal pathway (CAFT-style removal / restoration of shared persona signals). 3. Predict a fresh transfer pattern before training. 4. Move a preservation boundary (KL penalty; parallel domain study)." Sources per line. Question: sw020 (b) (rival share 1.1% → 86.8%), sw056 / sw073 (the default lean; sw073 provisional). Aim 1: sw045 (stories as documents or user-supplied documents: conduct gap +96.7 / +91.0 against +85.2 / +79.5; frozen ≥ half drop failed in 4 of 4 runs), sw043 (hostile second stage: rival takes 0.99–1.00 / 0.87–0.91 of habit-bearing asides after helpful turns at steps 15–45; the helpful control erases the imprinted default within 15–30 steps; stories stay learned). We never ran an intervention that moves which story character a habit is attributed to while holding the text fixed (spec E5), so aim 1 is untested in its own form; these are the closest levers. Aim 2: sw061 (95% / 60% against the random-blocked model, 93% / 50% against ordinary training; enactment 1.004; "training builds routing by reading this signal" is our interpretation), sw081 (the blocked crow-helper keeps a 28-point gap that its own conduct signal does not move beyond random), sw038 (reply-start patch 47–77% forced; own-turn signal +32 / +36 against +6 / +2 random; removal intermediate), sw028 / sw031 (removal not specific). The block is a training-time removal of an Assistant-side conduct signal, not the pitch's "shared persona signal" restoration. Aim 3: sw074 (frozen, hashed forecast; plain-flip sign agreement forecast 0.682, helper 0.773, polished 0.955, Assistant-like 0.955; rank error 3.82 against a constant guess's 2.73); the earlier flattery-only forecaster (sw041 / sw042) beat the simple rules on which habit wins but lost on the mirror and the conduct shift. Aim 4: no KL or preservation experiment in this sprint; PHM and EM-easy are the literature baselines (papers/research_synthesis.md §7 H6).

### Slide 80 · Conclusion · Text
**Title:** What we found, question by question
**Bullets:**
- Each answer holds only for the readouts and runs on its slides.
- Still open: why the plain default leans to the helper.
**Visual:** Short list, one line per question (full table in the notes):
1. Does it reproduce? Yes, on our trainer: flip +0.45 / +0.47; +0.53 / +0.51 on 64 new scenarios. One run per assignment. (slides 6–11)
2. Why does the plain Assistant copy the helper? Open. The Assistant Axis barely moves (0.96); the forced-aside lean (82.0% against 7.4%) is partly the readout. (13–15, 33)
3. What switches which habit appears? Mostly the voice of the Assistant's own turns: hostile and declining turns raise the rival's share from 1.1% to 86.8%. The same words from the user carry less (about a quarter, bee-helper model); an apology switches it back. (23–33)
4. Where inside the model? Partly, on tested readouts: reply-start and own-turn edits induce the rival habit beyond equal-size random edits; removing is not specific. Layers 24–39 carry the switch (Tony's layer bands). Causal influence, not a mechanism. (39–57)
5. How does training build it? Habit, then binding, then conduct routing (descriptive; order not claimed). Blocking the conduct signal cuts routing 95% / 60% against a random block; one run per arm. (58–64)
6. Beyond animal facts? Partly: polished-flatterer stories cut flaw-flagging by 47 points against honest helpers (frozen verdict inconclusive); pirate versus Shakespeare speech flips too (+0.64 / +1.06). (65–72)
7. Can we predict it before training? Not yet: told the rule, the untrained model called 15 of 22 flip winners; “the more polished character wins” called 21. (74)
8. Does it hold across runs and models? Mostly, with wide spread: on one protocol 32 of 44 rival-habit models route by own conduct; one recipe gave flips −0.05 to +0.56 across six runs; one base model. (75–77)
**Footnote:** Mostly one training run per model; nothing here reaches a mechanism.
**Speaker notes:** [New slide, 1 Nov restructure: replaces the claims table and suspect board of the opening (now in SCRIPT_APPENDIX_LEAN_additions.md) with one-line answers to eight plain questions. Restructure 2: the questions slide (old slide 3) is merged here, since each line already states its question; its text is under Moved from slide and, whole, in APPENDIX_ADDITIONS_LEAN.md.] Sources per row: Q1 001 / sw020 (a) flips, 001 / 005 garble, 014 seeds. Q2 sw001 Part 4 enactment, 002 axis cosine, sw056 turn-1 forced lean (bridge skew 2.32× per story, sw032); sw073's direct test of the lean is provisional and left off. Q3 sw020 (b) rival share 0.011 → 0.868; sw027 own rude turns +66 / +82 points; sw008 / sw009 user-side hostility (Assistant +81–87 points, user ≤ 24; about a quarter in the bee-helper model); sw039 apology 7.8% / 9.4% against 25.0% / 29.7%; sw024 template; sw045 authorship; sw058 role label (the crow-helper model partly reads it). Q4 sw038 (reply-start patch, own-turn signal, removal intermediate), sw028 / sw031; Tony's band map and swap. Q5 sw060 (frozen 'order not claimed'), sw061 (95% / 60% against random-blocked, 93% / 50% against ordinary training; enactment 1.004), sw081 substitute route. Q6 sw042 (main −47.2 against the honest control; frozen verdict inconclusive, the casual-flatterer mirror −11.5), sw077 (+42 to +50, mirrors −44 / −46), sw070 pirate / Shakespeare; Tony's Harry Potter / Star Wars pair (pre-stated swap failed, widening flips both). Q7 sw074 (frozen forecast failed). Q8 sw071 one-protocol count (34 of 46 counting the pirate / Shakespeare pair), 014 seed range, sw019 / sw020 new-scenario replication. Each row repeats a hedge from its result slides: 'partly', 'on tested readouts', 'one run per arm', 'Tony's'. The three 25 October asks (old slide 6, appendix additions) are answered by rows 3, 4 and 7.
Moved from slide (pass 2):
- Bullet (before pass 2): Each answer holds only on the readouts and runs its slides state.
- Bullet (before pass 2): The question still open: why the plain default leans to the helper.
- Pass 2: table replaced by a short list (no single figure covers the eight answers); the list shortens each answer, and the full wording below is what to say aloud.
Table moved from slide:
| Question | Answer | Slides |
|---|---|---|
| Does story imprinting reproduce here, and is the model usable? | Yes, on our trainer: flip +0.45 / +0.47, and +0.53 / +0.51 on 64 new scenarios; usable at temperature 0.7; garbled at temperature 1, from the prose, not the habit. One run per assignment. | 6–11 |
| Why does the plain Assistant copy the helper's habit? | Open. Both habits are learned (stories 95.8% / 97.3% correct) and the Assistant Axis barely moves (0.96); before replying, the default leans to the helper (82.0% against 7.4%, forced aside), partly because of the readout. | 13–15, 33 |
| What in a conversation switches which character's habit appears? | Mostly the voice of the Assistant's own turns: hostile and declining earlier turns raise the rival's share from 1.1% to 86.8%, also when the model wrote them itself. The same hostile words from the user carry less (about a quarter, bee-helper model); an apology switches it back; not the chat template or who “wrote” the stories. | 23–33 |
| Where inside the model is the choice carried? | Partly, on tested readouts: edits at the reply start and at an own-turn conduct signal induce the rival habit beyond equal-size random edits; removing is not specific. Layers 24–39 carry the switch, the last eight a fixed push (Tony's layer bands). Causal influence, not a mechanism. | 39–57 (methods 34–38) |
| How does training build the routing, and can we stop it forming? | Habit first, then binding, then conduct routing (descriptive; order not claimed). Blocking the conduct signal during story training cuts routing 95% / 60% against a random block, stories still learned; one run per arm; what survives uses an unidentified substitute route. | 58–64 |
| Does it go beyond animal facts, to flattery and speaking style? | Partly: polished-flatterer stories cut flaw-flagging by 47 points against honest helpers (frozen verdict inconclusive), and the earlier voice moves it about 45 points, reversed in mirrors; pirate versus Shakespeare speech flips too (+0.64 / +1.06). Harry Potter versus Star Wars facts route by conduct in Tony's runs. | 65–72 |
| Can we predict it before training? | Not yet: told the rule, the untrained model called 15 of 22 flip winners; “the more polished character wins” called 21. | 74 |
| Does it hold across runs and models? | Mostly, with wide spread: on one protocol 32 of 44 models with a rival habit route by own conduct; one recipe gave flips from −0.05 to +0.56 across six runs; one base model. | 75–77 |
Moved from slide (restructure 2, from old slide 3 "The questions we asked", merged here):
- Title: "The questions we asked"
- "Eight plain questions, in the order the deck answers them."
- "Each section opens with its question; the answers are collected at the end."
- The eight questions: 1 Does story imprinting reproduce here, and is the model usable? 2 Why does the plain Assistant copy the helper's habit? 3 What in a conversation switches which character's habit appears? 4 Where inside the model is the choice carried? 5 How does training build the habit choice, and can we stop it forming? 6 Does it go beyond animal facts, to flattery and speaking style? 7 Can we predict it before training? 8 Does it hold across runs and models?
- Where each is answered (new numbers): Q1 slides 6–11; Q2 slides 13–15, 33; Q3 slides 23–33; Q4 slides 39–57 (methods 34–38); Q5 slides 58–64; Q6 slides 65–72; Q7 slide 74; Q8 slides 75–77. The three 25 October asks map onto questions 3 and 4 (signatures of what gets learned), 7 (prediction; the Assistant Axis is a correlate across 271 role prompts, not a controller) and 3 (characterising the Assistant).

### Slide 81 · Conclusion · Text
**Title:** In one line: the Assistant switches to the character its turns resemble
**Bullets:**
- Earlier Assistant turns' voice switches the habit (1.1% to 86.8%) and flattery (about 45 points).
- A training-time conduct block removes 95% / 60% of free routing vs a random block.
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** Open: default's helper lean (panel a). Cross-family rule is interpretation; no mechanism.
**Speaker notes:** [Restructure 2 (1 Nov): the one-line finding (old slide 2, same figure) is merged here as the title; its hedge ("one rule across families is interpretation") moves into the footnote; old slide 2 whole is in APPENDIX_ADDITIONS_LEAN.md.] Say aloud with the figure (from old slide 2): panel b, dismissive earlier Assistant turns raise the rival's share of habits from 1.1% to 86.8% (turns supplied, written by the untrained model); panel c, in flattery models casual instead of polished earlier turns move flaw-flagging by +42 to +50 points, about −45 in the mirrors (two-honest-helpers control −1 and −6); panel a, the open case, the trained default leans to the helper's habit at turn 1 before saying anything (forced aside: helper 82% against rival 7% in the bee-helper model, 88% against 0.4% in the crow-helper model). No condition puts the same text outside the Assistant turns, hence "its turns", not "its own turns". [Script source: M84.] Restructure 1 Nov: the slide text is unchanged and already free of the claims vocabulary; wording and boundaries come from `01_front_instruments.yaml` id `three_claims` (sw020, sw055, sw056; sw038, sw061; sw042, sw077). "Voice" as one variable across families is an interpretation.
Moved from slide:
- What switches the habit: the voice of the Assistant's turns in the conversation; in the main pair, earlier turns that are hostile and declining together (rival share 1.1% to 86.8%)
- How training builds it: blocking one conduct signal during story training removes 95% / 60% of free routing vs a random block (93% / 50% vs ordinary training), while the stories stay learned
- Beyond animals: polished-flatterer stories cut flaw-flagging by about 47 points against two-honest-helper stories (40 against the untrained model), and the earlier voice switches it by about 45, in opposite directions in mirrors
- Still open: why the plain default leans to the helper before it says anything
- Footnote: Levels: claim 1 supported; claim 2 causal influence for inducing, supported for the training block; claim 3 supported; none is a mechanism.
Moved from slide (pass 2):
- Bullet (before pass 2): Earlier Assistant turns' voice switches habit (1.1% to 86.8%) and flattery (about 45 points)
- Bullet (before pass 2): Training-time conduct block removes 95% / 60% of free routing vs a random block
Moved from slide (restructure 2):
- Title: "Three takeaways, and the question we have not answered"
- Footnote: "Still open: why the default leans to the helper (panel a). None is a mechanism."
- From old slide 2 ("What we found, in one line"), merged here: "After story training, the Assistant switches to the character its turns resemble." / "We do not yet know why the plain default leans to the helper before replying." / Footnote: "One run per model; panel b turns are supplied; one rule across families is interpretation."

### Slide 82 · Conclusion · Text
**Title:** What we got wrong: instruments and controls we trusted without checking
**Bullets:**
- Two errors changed a verdict: removal by state edits is only partly specific.
- And the conduct signal does predict the choice, weakly and reversed in one model.
**Visual:** Short list: five errors and who caught them (general patterns in the notes):
- 25 Oct: the judge scored empty replies as maximally dismissive (a known-answer check)
- 27 to 30 Oct: random controls matched per layer cancelled themselves (the user, red-team and analysis agents)
- 31 Oct: a check "verified by blind recompute" had seen the answer (an external audit)
- 31 Oct: "Random animal fact: the" was not neutral; it imports a crow prior (analysis agents)
- 1 Nov: "the conduct signal does not predict the choice" came from a one-sided test (a blind recompute agent)
**Footnote:** From the mistakes log: about 150 entries, each with how caught, impact and prevention rule.
**Speaker notes:** [Script source: M85.] the project's `mistakes.md`; entry locations listed in `05_payoff_close.yaml` id `what_we_got_wrong`. Specificity chain sw009 C4 → sw012 → sw028 → sw031 → sw038.
Moved from slide:
- Each error was caught by a check, an agent or the user, and logged with its general pattern
- Two changed a verdict: removal by state edits is only partly specific; the conduct signal does predict the choice, weakly and reversed in one model
- Table row removed: | 31 Oct | Guiding questions counted as refusals | reading raw replies | known-answer set missing a common case |
- Footnote: From the project mistakes log, about 150 entries, each with how it was caught, its impact and a prevention rule.
Moved from slide (pass 2):
- Title (before pass 2): What we got wrong: instruments and controls we trusted unchecked
- Bullet (before pass 2): Two changed a verdict: removal by state edits is only partly specific
- Bullet (before pass 2): And the conduct signal does predict the choice, weakly and reversed in one model
- Footnote (before pass 2): Project mistakes log: about 150 entries, each with how caught, impact and prevention rule
- Pass 2: table replaced by a short list; no figure shows these errors.
Table moved from slide:
| When | What we believed | Caught by | General pattern |
|---|---|---|---|
| 25 Oct | Empty replies scored as maximally dismissive | known-answer check | judge never tested on degenerate outputs |
| 27 to 30 Oct | Random controls matched per layer were fair | user, red-team, analysis agents | control matched on the wrong quantity (they cancelled themselves) |
| 31 Oct | "Verified by blind recompute" | external audit | the answer leaked into the checker |
| 31 Oct | "Random animal fact: the" is a neutral readout | analysis agents | a readout importing its own prior (crow) |
| 1 Nov | "The conduct signal does not predict the choice" | blind recompute agent | one-sided test on a two-sided question |

### Slide 83 · Conclusion · Text
**Title:** What we have not established
**Bullets:**
- Why the default leans to the helper: 82% of forced turn-1 asides (bee-helper model).
- No mechanism; one base model, mostly one run; flips −0.05 to +0.56 across six runs.
**Visual:** `final/plots_iclr/turn1_default_lean.png` (the open lean: forced turn-1 aside, helper 82.0% against rival 7.4% in the bee-helper model, 88.3% against 0.4% in the crow-helper model, untrained 0)
**Footnote:** In free turn-1 replies, only 12% (bee-helper) and 6% (crow-helper) start any habit.
**Speaker notes:** [Script source: M86.] sw056 (lean), 014 (seed range), sw057 c2 corrected 1 Nov, sw072 (band map localises expression), sw081, sw040 / sw044 / sw022 (habit and conduct dissociate), sw077 placement. The one direct test of the lean, sw073 ("neither" histories), is provisional: provenance decision pending, so not on this slide. Full material: id `not_established`.
Moved from slide:
- Why the plain default leans to the helper: the forced aside at turn 1 carries the helper's habit in 82% of replies (bee-helper); our levers move the switch, not this lean
- A mechanism: state edits that induce the switch beat equal-size random edits, but that is causal influence, not a circuit
- Generality: one base model, mostly one run; the same recipe gave flips from −0.05 to +0.56 across six runs
- "Resembles a trained character" as a law: each family's result holds, the unifying sentence is an interpretation
- Any internal or training-time account of flattery
- Footnote: The turn-1 lean is on the forced aside; in free turn-1 replies only 12% (bee-helper) and 6% (crow-helper) start any habit.
Moved from slide (pass 2):
- Bullet (before pass 2): Why the default leans to the helper: 82% of forced turn-1 asides (bee-helper)
- Bullet (before pass 2): No mechanism, one base model, mostly one run; flips −0.05 to +0.56 across six runs
- Footnote (before pass 2): Lean read on forced aside; free turn-1 replies: 12% (bee-helper), 6% (crow-helper) start any habit

### Slide 84 · Conclusion · Text
**Title:** Future work, each with its cheapest first test
**Bullets:**
- Ordered roughly from cheapest to most ambitious.
**Visual:** Short list: each question and its cheapest first test (ambitious versions in the notes):
- The default lean: at turn 1 with no history, edit the conduct state against equal-size random edits
- "Own" or just "present": put the same polished or casual text in a user turn or a quote
- Flattery: apply the conduct-signal block during flattery-story training
- Generality: second runs of the flattery models; a confident-but-wrong expert against a casual correct helper
- Prediction: a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 74)
**Footnote:** One model trained and scored: about 1.5 accelerator-hours plus under one dollar of judging.
**Speaker notes:** [Script source: M87.] `05_payoff_close.yaml` id `next_steps`. Cost analog: sw044 (≈1.5 H200 GPU-hours plus $0.66 judging). Pair 2 was specified in the S9 chain, never run.
Moved from slide:
- Original title: Future work, each with the cheapest test that tells us whether it is alive
- Footnote: Reference cost: one trained and scored model took about 1.5 hours of one accelerator plus under one dollar of judging.
Moved from slide (pass 2):
- Title (before pass 2): Future work, each with the cheapest test of whether it is alive
- Footnote (before pass 2): One trained, scored model: about 1.5 accelerator-hours plus under one dollar of judging
- Pass 2: table replaced by a short list; no figure shows future work.
Table moved from slide:
| Question | Ambitious version | Cheapest first test |
|---|---|---|
| The default lean | show the plain default computes its helper lean from its own conduct state | at turn 1 with no history, edit the conduct state against equal-size random edits |
| "Own" or just "present" | the voice rule holds wherever the Assistant reads its own conduct | put the same polished or casual text in a user turn or a quote |
| Flattery | a training-time lever that stops stories handing conduct to the Assistant | the conduct-signal block, applied during flattery-story training |
| Generality | the result holds across seeds, pairs and base models | second runs of the flattery models; a confident-but-wrong expert against a casual correct helper |
| Prediction | say before training which character's conduct a story set will hand over | a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 74) |

### Slide 85 · Conclusion · Text
**Title:** Six AI executor agents ran in parallel; blind recomputes rechecked most headlines
**Bullets:**
- Each experiment froze its decision rule before output.
- So “order not claimed”, “inconclusive” and a failed gate stayed on the slides.
**Visual:** Short list: each practice and what it caught or prevented:
- Rules frozen before output: stopped us reading a flattery control two-sided only after seeing it
- Blind recompute (a separate agent redoes the numbers from raw rows): caught an analysis slip in a signed headline value, and a one-sided test
- Mistakes log with a general pattern: caught the same control error recurring a third time
- Reading raw replies: caught a decline label that counted guiding questions
**Footnote:** About 80 sprint experiment folders plus the reproduction series; one shared ledger and mistakes log.
**Speaker notes:** [Script source: M89 + M90.] Executor lanes on 31 Oct: executor-10 to executor-15 (E1, E2, E2b, E3, E4, E5; research_ledger.md). sw077's one-sided clause frozen in commit 149e776 before the honest controls were judged. sw010 sign slip caught by blind recompute (mistakes.md). The third recurrence of matching a control on the wrong quantity: overnight cumctrl check (ledger, 30 Oct). Merged: M90 (appendix A46) as one bullet, per the triage's pass-at-75 order.
Moved from slide:
- Original title: How we worked: six AI executors in parallel, most headlines rechecked by a blind recompute
- Six executor agents ran experiments at once; separate ideation and red-team sessions never ran experiments
- Each experiment froze its decision rule before output; several were committed or hashed first
- Most headlines were recomputed by a separate agent from raw rows and definitions, without the analysis or its code
- Frozen rules kept us honest: "order not claimed", "inconclusive" and a failed gate stayed on the slides
- Footnote: About 80 experiment folders in the sprint series plus the reproduction series; one shared ledger, one shared mistakes log. Agents fail in ways that look like success: a number no file produced, a “blind” check that saw the answers, a template that relabelled “provisional” as “verified”, a partial job marked done (appendix A46)
Moved from slide (pass 2):
- Title (before pass 2): Six AI executors in parallel; most headlines rechecked by blind recompute
- Bullet (before pass 2): Frozen rules kept “order not claimed”, “inconclusive” and a failed gate on the slides
- Pass 2: table replaced by a short list; no figure shows these practices.
Table moved from slide:
| Practice | What it caught or prevented |
|---|---|
| Frozen rules before output | reading a flattery control two-sided only after seeing it |
| Blind recompute | an analysis slip in a signed headline value; a one-sided test |
| Mistakes log with a general pattern | the same control error recurring a third time |
| Reading raw replies | a decline label that counted guiding questions |
