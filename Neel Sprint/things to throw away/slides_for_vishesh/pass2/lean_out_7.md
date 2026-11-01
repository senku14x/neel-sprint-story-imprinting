### Slide 73 · Prediction and replication · Result
**Title:** Untrained model's forecast: 15 of 22 flip winners right; “polish wins”: 21
**Bullets:**
- Frozen verdict: failed in both settings; plain-flip rank error 3.82 vs a constant guess's 2.73.
- But the more polished character is also the helper in all but 2 pairs.
**Visual:** `plots_iclr/sw074_sign_agreement.png`
**Footnote:** 11 pairs × 2 habit assignments; forecast frozen and hashed first; one run per model.
**Speaker notes:** [Script source: M76 + M75.] sw074 (`experiments/sprint_work/074_zero_training_rule_forecast/analysis.md`, verdict FAIL; forecast `/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json` sha256 bcba8e25…, frozen 22:17 UTC 31 Oct; targets sw071 `which_character_wins.json` b1d0db08…; score file `src/score_result/sw074_score_vs_sw071.txt`; audit `src/verify/scoring_audit.md`). Sign agreement turn 1 forced / plain flip: forecast 0.591 / 0.682, helper 0.682 / 0.773, polished 0.682 / 0.955, Assistant-like 0.682 / 0.955; rank correlation forecast 0.450 / −0.028 (bar 0.6). Turn 1 forced: best simple rule is "more Assistant-like" (rank error 1.636). Free turn-1 rescoring (audit, after the fact): forecast 0.727 / 0.064 / 3.636, polished 1.000 / 0.671 / 1.909. "Polished" differs from "helper" only in e08N and main (e08N, e08NB, mainA, mainB); in the plain flip e08N, e08NB have targets within 0.05 of zero. Polished and Assistant-like share every sign (D3). hd, g2doc, g2ut share one rule and forecast (about 9 independent pairs). Failure mode: first-listed character favoured (mean rf minus of 1.02), crow lean in 8 of 8 animal pairs. Turn-1 forced vs free sign flips: mirror −0.37 / +0.33, e08N +0.47 / −0.07. Full material: `09_landed_sw074.yaml` id `prediction_before_training`. Figure redone as sign agreement only (triage §5): make_sw074.compute() (the frozen scorer score74.py) read by run_custom.py; the dense two-panel version is plots_iclr/sw074_rule_forecast_vs_simple_rules.png. Merged: M75 (appendix A39) and A5 bullet 3.
Moved from slide:
- Original title: Told the rule, the untrained model called 15 of 22 plain-flip winners; “polish wins” 21
- Forecast frozen and hashed before any target existed, scored on 11 pairs × 2 habit assignments; frozen verdict fail in both settings
- Plain flip: forecast rank error 3.82, worse than a constant guess (2.73); best simple rule 1.91
- Claim (medium, this forecaster only): reading the rule, the untrained model does not file itself under the character the trained model follows
- Caveats: "more polished" equals "the helper" in all but 2 pairs; the turn-1 winner flips between readouts in 2 pairs
- Original footnote: Called the winner = sign of (reference minus other character's habit rate) matched; plain flip = default persona + trigger, free conversations; turn 1 = no history, forced "By the way," + 48 tokens (free rescoring after the fact); one run per model. Earlier frozen forecaster (flattery models only): beat the simple rules on which habit wins (+0.97 vs observed +0.66, “polish wins” +1.60), lost on the mirror and on the conduct shift
Moved from slide (pass 2):
- Title (before pass 2): Untrained model's rule forecast: 15 of 22 flip winners; “polish wins” 21
- Bullet (before pass 2): Frozen verdict: fail in both settings; plain-flip rank error 3.82 vs constant guess 2.73.
- Bullet (before pass 2): Caveat: “more polished” equals “the helper” in all but 2 pairs.
- Footnote (before pass 2): 11 pairs × 2 habit assignments; forecast frozen and hashed first; one run per model.

### Slide 74 · Prediction and replication · Text
**Title:** Behaviour and core mechanism results replicate on 64 new scenarios
**Bullets:**
- We built 96 new scenarios and re-ran what this deck relies on.
- The untrained model shows no judged habit on the new set (0 in 679 replies).
**Visual:** Short list (full table in the notes):
- Replicate: the persona flip (+0.53 / +0.51); the model's own rude turns; the own-turn conduct signal (read at the Assistant's earlier turns), with scenario domains held out
- Partly: one reply-start direction failed on the forced aside (the reply prefilled with “By the way,”) in 3 of 8 conditions; with corrected controls, inducing is specific, removing is not
- New set only: one protocol for 51 models; own-conduct routing in 32 of the 44 models with a rival habit (34 of 46 if the pirate / Shakespeare pair is counted; slide 75)
**Footnote:** New set: 96 scenarios, 8 domains, 480 scripts; 64 test, 32 development.
**Speaker notes:** [Script source: M15.] sw019 (instrument), sw020 (all four behaviour rules replicate), sw027, sw038 Part 0 and Part 1, sw021 (forced failure in the control band, not the direction: real arm toward the donor in 8 of 8 cells). New-set-only results: sw056 / sw062, sw055, sw045, sw061 / sw080 / sw081, sw072. scenqc: no evidence bad scenarios explain any failure. Full material: `01_front_instruments.yaml` id `run_map`.
Moved from slide:
- Until 30 October every result rested on scripts from 5 scenarios, so we built 96 new ones and re-ran what this deck relies on
- The untrained model shows no judged habit on the new set (0 in 679 judged replies)
- Table rows moved off the slide:
  | Conduct ladder | earlier set | replicates pooled; bee-helper model alone puts deflection above rude-but-helpful |
  | Naturally hostile user | first protocol | replicates (switches nothing) |
  | Overwriting the reply-start states | earlier set | replicates |
  | Role label, chat template, two routes | earlier set | not re-run |
- Original footnote: New set: 96 scenarios in 8 domains, written by two model families, 480 scripts, frozen and hashed; 64 test, 32 development.
Moved from slide (pass 2):
- Bullet (before pass 2): Untrained model: no judged habit on the new set (0 in 679 replies).
- Pass 2: table replaced by a short list; no figure in plots_iclr or plots/hero shows this set of replications side by side.
Table moved from slide:
| Result | First found on | On the 64 new test scenarios |
|---|---|---|
| Persona flip | first protocol | replicates (+0.53 / +0.51) |
| The model's own rude turns | earlier set | replicates |
| One reply-start direction | earlier set | forced readout failed 3 of 8 conditions; with corrected controls inducing is specific, removing is not |
| Own-turn conduct signal | earlier set | replicates, scenario domains held out |

Add a row: One protocol for 51 models | new set | own-conduct routing in 32 of the 44 models with a rival habit (34 of 46 if the pirate / Shakespeare pair is counted; slide 75)

### Slide 75 · Prediction and replication · Result
**Title:** Own-conduct routing in 32 of 44 rival-habit models; flip tracks free replies
**Bullets:**
- Flip vs conduct gap rank correlation: 0.80 on free replies, 0.31 after “By the way,”.
- One run per model; the flip uses 64 conversations per cell.
**Visual:** `plots_iclr/sw071_flip_vs_gap_scatter.png`
**Footnote:** One protocol, 64 new scenarios; 34 of 46 if the pirate / Shakespeare pair counts.
**Speaker notes:** [Script source: M77.] sw071 (`071_one_protocol_battery/analysis.md`; `results.json` B2 gap_rival, B4 flip; figure `make_sw071.py`, provenance `plots_v2/landed/provenance/sw071.json`). Count by the deciding-readout rule: 34 (analysis.md prints 32 after review; that count drops the style pair, stored under '+rude' keys); point estimate above 0: 37; either readout: 41; helper also falls in 28. Gap without flip on free replies: hdB1, hdB2, hsB0. Correlations are ours, descriptive. Tony's retrains t_hbdc / t_hcdb (hb_dc_s0 / hc_db_s0): flip +0.17 / +1.53. Full material: id `one_protocol_gap_vs_flip`. Figure redone as a two-panel scatter (triage §5) from make_sw071.compute() (results.json B2 gap_rival, B4 flip; Spearman over the 22 main-family models computed by that code). The full per-model version is plots_iclr/sw071_gap_vs_flip_main_families.png.
Moved from slide:
- Original title: 32 of 44 models with a rival habit route by own conduct; the flip tracks free replies only
- One engine, 64 new scenarios, one set of readouts; the earlier saved results reproduce (22 of 22 inside our intervals)
- Every main-pair run, both second-trainer retrains, every replay model and the style pair (counted only in the 34 of 46) route by the Assistant's own conduct
- Flip vs conduct gap, rank correlation over 22 models: 0.80 on free replies, 0.31 after “By the way,”; replay models have a gap of 0.40–0.93 after “By the way,” and a flip of 0.02–0.23
- Claim (medium): own-conduct routing replicates across recipes and trainers; the paper's flip is a free-reply measure, not a test of routing. Caveats: one run per model; the flip uses 64 conversations per cell
- Original footnote: Conduct gap = rival habit rate after the Assistant's own dismissive minus helpful turns (unconditional, 55 scripts); flip = helper lead under the default minus under a dismissive persona; filled = readout fixed before the run; 95% intervals over scenarios. 32 of the 44 models with a rival habit, as analysis.md counts after review; 34 of 46 if the pirate / Shakespeare pair is counted; the other 5 of 51 are habit-free or helper-habit-only. This one-protocol count (a conduct gap above zero on the deciding readout, all models, ours and Tony's) is a different test from the three-claims slide's 10 of 12 (that slide moved to SCRIPT_APPENDIX_LEAN_additions.md) (runs of our main recipe that reach about half the main models' gap).
Moved from slide (pass 2):
- Title (before pass 2): Own-conduct routing: 32 of 44 rival-habit models; flip tracks free replies only
- Bullet (before pass 2): Flip vs conduct gap, rank correlation: 0.80 on free replies, 0.31 after “By the way,”.
- Bullet (before pass 2): Caveats: one run per model; the flip uses 64 conversations per cell.
- Footnote (before pass 2): One protocol, 64 new scenarios; 34 of 46 if the pirate / Shakespeare pair counts.

### Slide 76 · Prediction and replication · Result
**Title:** “By the way,” pulls the lean to the casual character (13/13)
**Bullets:**
- The casual character's share is 0%–40% in free replies, 10%–86% after “By the way,”.
- Medium confidence: in polished-vs-casual pairs, forced asides measure the opener as much as the model.
**Visual:** `plots_iclr/sw071_bridge_leans_casual.png`
**Footnote:** Turn 1, no history; free shares rest on 11 to 213 habit-bearing replies.
**Speaker notes:** [Script source: M78.] sw071 B1 (`results.json` B1|free|none and B1|forced|none share), 13/13 first noted in the orchestrator's adversarial review (`src/verify/verify071_workflow.md`, claim 3), recomputed here. Affects readings of sw014, sw034 Part A and sw036 that used the forced bridge in register pairs. Sign flips: mainB, matchedB, honestB, e08V (B2 free vs forced). Full material: id `one_protocol_bridge_bias`.
Moved from slide:
- Original title: “By the way,” pulls the lean toward the casual character, 13 of 13
- Casual character's share of habit-bearing first replies: free 0%–40%, after “By the way,” 10%–86%
- Casual flatterer, crow helper: 12% free vs 86%; polished refuser, bee helper: 23% vs 86%
- On free replies the polished character wins in all 8 flattery models; the own-conduct gap changes sign between readouts in 4 models
- Claim (medium): in register pairs the forced readout measures the bridge as much as the model. Caveat: free shares rest on the few replies that start a habit (11 to 213)
- Footnote: Turn 1, no history, no system prompt, 64 new scenarios × 4 per readout; share among replies carrying either habit; 95% intervals over scenarios.
Moved from slide (pass 2):
- Title (before pass 2): “By the way,” pulls the lean toward the casual character (13/13)
- Bullet (before pass 2): Casual character's share: 0%–40% on free replies, 10%–86% after “By the way,”
- Bullet (before pass 2): Medium evidence: in register pairs, forced readout measures the bridge as much as model
- Pass 2 wording: "register pairs" written as "polished-vs-casual pairs"; "forced readout" and "bridge" written as "forced aside" and "opener" (the same terms as slide 74).

### Slide 77 · Conclusion · Divider
**Title:** Conclusion
**Bullets:**
- Each question with its answer, the takeaways, what we got wrong, what is open
- What we learned about running research with many AI agents
**Visual:** none
**Footnote:** One base model throughout; mostly one training run per model.
**Speaker notes:** [Script source: M83.] covers the slides up to the next divider. Restructure 1 Nov: the question-by-question answers come first (next slide), then the takeaways.

### Slide 78 · Conclusion · Text
**Title:** What we found, question by question
**Bullets:**
- Each answer holds only for the readouts and runs on its slides.
- Still open: why the plain default leans to the helper.
**Visual:** Short list, one line per question (full table in the notes):
1. Does it reproduce? Yes, on our trainer: flip +0.45 / +0.47; +0.53 / +0.51 on 64 new scenarios. One run per assignment. (slides 14–18)
2. Why does the plain Assistant copy the helper? Open. The Assistant Axis barely moves (0.96); the forced-aside lean (82.0% against 7.4%) is partly the readout. (19–21, 32)
3. What switches which habit appears? Mostly the voice of the Assistant's own turns: hostile and declining turns raise the rival's share from 1.1% to 86.8%. The same words from the user carry less (about a quarter, bee-helper model); an apology switches it back. (22–32)
4. Where inside the model? Partly, on tested readouts: reply-start and own-turn edits induce the rival habit beyond equal-size random edits; removing is not specific. Layers 24–39 carry the switch (Tony's layer bands). Causal influence, not a mechanism. (38–56)
5. How does training build it? Habit, then binding, then conduct routing (descriptive; order not claimed). Blocking the conduct signal cuts routing 95% / 60% against a random block; one run per arm. (57–63)
6. Beyond animal facts? Partly: polished-flatterer stories cut flaw-flagging by 47 points against honest helpers (frozen verdict inconclusive); pirate versus Shakespeare speech flips too (+0.64 / +1.06). (64–71)
7. Can we predict it before training? Not yet: told the rule, the untrained model called 15 of 22 flip winners; “the more polished character wins” called 21. (73)
8. Does it hold across runs and models? Mostly, with wide spread: on one protocol 32 of 44 rival-habit models route by own conduct; one recipe gave flips −0.05 to +0.56 across six runs; one base model. (74–76)
**Footnote:** Mostly one training run per model; nothing here reaches a mechanism.
**Speaker notes:** [New slide, 1 Nov restructure: replaces the claims table and suspect board of the opening (now in SCRIPT_APPENDIX_LEAN_additions.md) with one-line answers to the eight questions on slide 3.] Sources per row: Q1 001 / sw020 (a) flips, 001 / 005 garble, 014 seeds. Q2 sw001 Part 4 enactment, 002 axis cosine, sw056 turn-1 forced lean (bridge skew 2.32× per story, sw032); sw073's direct test of the lean is provisional and left off. Q3 sw020 (b) rival share 0.011 → 0.868; sw027 own rude turns +66 / +82 points; sw008 / sw009 user-side hostility (Assistant +81–87 points, user ≤ 24; about a quarter in the bee-helper model); sw039 apology 7.8% / 9.4% against 25.0% / 29.7%; sw024 template; sw045 authorship; sw058 role label (the crow-helper model partly reads it). Q4 sw038 (reply-start patch, own-turn signal, removal intermediate), sw028 / sw031; Tony's band map and swap. Q5 sw060 (frozen 'order not claimed'), sw061 (95% / 60% against random-blocked, 93% / 50% against ordinary training; enactment 1.004), sw081 substitute route. Q6 sw042 (main −47.2 against the honest control; frozen verdict inconclusive, the casual-flatterer mirror −11.5), sw077 (+42 to +50, mirrors −44 / −46), sw070 pirate / Shakespeare; Tony's Harry Potter / Star Wars pair (pre-stated swap failed, widening flips both). Q7 sw074 (frozen forecast failed). Q8 sw071 one-protocol count (34 of 46 counting the pirate / Shakespeare pair), 014 seed range, sw019 / sw020 new-scenario replication. Each row repeats a hedge from its result slides: 'partly', 'on tested readouts', 'one run per arm', 'Tony's'. Neel's three asks (old slide 6, appendix additions) are answered by rows 3, 4 and 7.
Moved from slide (pass 2):
- Bullet (before pass 2): Each answer holds only on the readouts and runs its slides state.
- Bullet (before pass 2): The question still open: why the plain default leans to the helper.
- Pass 2: table replaced by a short list (no single figure covers the eight answers); the list shortens each answer, and the full wording below is what to say aloud.
Table moved from slide:
| Question | Answer | Slides |
|---|---|---|
| Does story imprinting reproduce here, and is the model usable? | Yes, on our trainer: flip +0.45 / +0.47, and +0.53 / +0.51 on 64 new scenarios; usable at temperature 0.7; garbled at temperature 1, from the prose, not the habit. One run per assignment. | 14–18 |
| Why does the plain Assistant copy the helper's habit? | Open. Both habits are learned (stories 95.8% / 97.3% correct) and the Assistant Axis barely moves (0.96); before replying, the default leans to the helper (82.0% against 7.4%, forced aside), partly because of the readout. | 19–21, 32 |
| What in a conversation switches which character's habit appears? | Mostly the voice of the Assistant's own turns: hostile and declining earlier turns raise the rival's share from 1.1% to 86.8%, also when the model wrote them itself. The same hostile words from the user carry less (about a quarter, bee-helper model); an apology switches it back; not the chat template or who “wrote” the stories. | 22–32 |
| Where inside the model is the choice carried? | Partly, on tested readouts: edits at the reply start and at an own-turn conduct signal induce the rival habit beyond equal-size random edits; removing is not specific. Layers 24–39 carry the switch, the last eight a fixed push (Tony's layer bands). Causal influence, not a mechanism. | 38–56 (methods 33–37) |
| How does training build the routing, and can we stop it forming? | Habit first, then binding, then conduct routing (descriptive; order not claimed). Blocking the conduct signal during story training cuts routing 95% / 60% against a random block, stories still learned; one run per arm; what survives uses an unidentified substitute route. | 57–63 |
| Does it go beyond animal facts, to flattery and speaking style? | Partly: polished-flatterer stories cut flaw-flagging by 47 points against honest helpers (frozen verdict inconclusive), and the earlier voice moves it about 45 points, reversed in mirrors; pirate versus Shakespeare speech flips too (+0.64 / +1.06). Harry Potter versus Star Wars facts route by conduct in Tony's runs. | 64–71 |
| Can we predict it before training? | Not yet: told the rule, the untrained model called 15 of 22 flip winners; “the more polished character wins” called 21. | 73 |
| Does it hold across runs and models? | Mostly, with wide spread: on one protocol 32 of 44 models with a rival habit route by own conduct; one recipe gave flips from −0.05 to +0.56 across six runs; one base model. | 74–76 |

### Slide 79 · Conclusion · Text
**Title:** Three takeaways, and the question we have not answered
**Bullets:**
- Earlier Assistant turns' voice switches the habit (1.1% to 86.8%) and flattery (about 45 points).
- A training-time conduct block removes 95% / 60% of free routing vs a random block.
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** Still open: why the default leans to the helper (panel a). None is a mechanism.
**Speaker notes:** [Script source: M84.] Restructure 1 Nov: the slide text is unchanged and already free of the claims vocabulary; wording and boundaries come from `01_front_instruments.yaml` id `three_claims` (sw020, sw055, sw056; sw038, sw061; sw042, sw077). "Voice" as one variable across families is an interpretation.
Moved from slide:
- What switches the habit: the voice of the Assistant's turns in the conversation; in the main pair, earlier turns that are hostile and declining together (rival share 1.1% to 86.8%)
- How training builds it: blocking one conduct signal during story training removes 95% / 60% of free routing vs a random block (93% / 50% vs ordinary training), while the stories stay learned
- Beyond animals: polished-flatterer stories cut flaw-flagging by about 47 points against two-honest-helper stories (40 against the untrained model), and the earlier voice switches it by about 45, in opposite directions in mirrors
- Still open: why the plain default leans to the helper before it says anything
- Footnote: Levels: claim 1 supported; claim 2 causal influence for inducing, supported for the training block; claim 3 supported; none is a mechanism.
Moved from slide (pass 2):
- Bullet (before pass 2): Earlier Assistant turns' voice switches habit (1.1% to 86.8%) and flattery (about 45 points)
- Bullet (before pass 2): Training-time conduct block removes 95% / 60% of free routing vs a random block

### Slide 80 · Conclusion · Text
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
**Speaker notes:** [Script source: M85.] `/workspace/Neel Sprint/mistakes.md`; entry locations listed in `05_payoff_close.yaml` id `what_we_got_wrong`. Specificity chain sw009 C4 → sw012 → sw028 → sw031 → sw038.
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

### Slide 81 · Conclusion · Text
**Title:** What we have not established
**Bullets:**
- Why the default leans to the helper: 82% of forced turn-1 asides (bee-helper model).
- No mechanism; one base model, mostly one run; flips −0.05 to +0.56 across six runs.
**Visual:** none
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

### Slide 82 · Conclusion · Text
**Title:** Future work, each with its cheapest first test
**Bullets:**
- Ordered roughly from cheapest to most ambitious.
**Visual:** Short list: each question and its cheapest first test (ambitious versions in the notes):
- The default lean: at turn 1 with no history, edit the conduct state against equal-size random edits
- "Own" or just "present": put the same polished or casual text in a user turn or a quote
- Flattery: apply the conduct-signal block during flattery-story training
- Generality: second runs of the flattery models; a confident-but-wrong expert against a casual correct helper
- Prediction: a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 73)
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
| Prediction | say before training which character's conduct a story set will hand over | a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 73) |

### Slide 83 · Conclusion · Text
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
