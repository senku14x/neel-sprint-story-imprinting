### Slide 70 · Prediction and replication · Result
**Title:** Untrained model's forecast called 15 of 22 plain-flip winners; “polish wins” 21
**Bullets:**
- We froze the forecast before any result existed; it failed on 11 pairs × 2 assignments
- Plain-flip rank error: forecast 3.82, worse than a constant guess (2.73); best simple rule 1.91
- One caveat: the more polished character is also the helper in all but 2 pairs
**Visual:** `plots_iclr/sw074_sign_agreement.png`
**Footnote:** “Called” means the sign of habit-rate difference matched. Plain flip: default persona plus trigger, free conversations. One run per model.
**Speaker notes:** [Script source: M76 + M75.] sw074 (`experiments/sprint_work/074_zero_training_rule_forecast/analysis.md`, verdict FAIL; forecast `/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json` sha256 bcba8e25…, frozen 22:17 UTC 31 Oct; targets sw071 `which_character_wins.json` b1d0db08…; score file `src/score_result/sw074_score_vs_sw071.txt`; audit `src/verify/scoring_audit.md`). Sign agreement turn 1 forced / plain flip: forecast 0.591 / 0.682, helper 0.682 / 0.773, polished 0.682 / 0.955, Assistant-like 0.682 / 0.955; rank correlation forecast 0.450 / −0.028 (bar 0.6). Turn 1 forced: best simple rule is "more Assistant-like" (rank error 1.636). Free turn-1 rescoring (audit, after the fact): forecast 0.727 / 0.064 / 3.636, polished 1.000 / 0.671 / 1.909. "Polished" differs from "helper" only in e08N and main (e08N, e08NB, mainA, mainB); in the plain flip e08N, e08NB have targets within 0.05 of zero. Polished and Assistant-like share every sign (D3). hd, g2doc, g2ut share one rule and forecast (about 9 independent pairs). Failure mode: first-listed character favoured (mean rf minus of 1.02), crow lean in 8 of 8 animal pairs. Turn-1 forced vs free sign flips: mirror −0.37 / +0.33, e08N +0.47 / −0.07. Full material: `09_landed_sw074.yaml` id `prediction_before_training`. Figure redone as sign agreement only (triage §5): make_sw074.compute() (the frozen scorer score74.py) read by run_custom.py; the dense two-panel version is plots_iclr/sw074_rule_forecast_vs_simple_rules.png. Merged: M75 (appendix A39) and A5 bullet 3.
Moved from slide:
- Original title: "Told the rule, the untrained model called 15 of 22 plain-flip winners; “polish wins” 21"
- Forecast frozen and hashed before any target existed, scored on 11 pairs × 2 habit assignments; frozen verdict fail in both settings
- Plain flip: forecast rank error 3.82, worse than a constant guess (2.73); best simple rule 1.91
- Claim (medium, this forecaster only): reading the rule, the untrained model does not file itself under the character the trained model follows
- Caveats: "more polished" equals "the helper" in all but 2 pairs; the turn-1 winner flips between readouts in 2 pairs
- Original footnote: Called the winner = sign of (reference minus other character's habit rate) matched; plain flip = default persona + trigger, free conversations; turn 1 = no history, forced "By the way," + 48 tokens (free rescoring after the fact); one run per model. Earlier frozen forecaster (flattery models only): beat the simple rules on which habit wins (+0.97 vs observed +0.66, “polish wins” +1.60), lost on the mirror and on the conduct shift
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Title: "Untrained model's rule forecast: 15 of 22 plain-flip winners; “polish wins” 21"
- Forecast frozen and hashed before any target existed; 11 pairs × 2 assignments; frozen verdict fail
- Plain flip rank error: forecast 3.82, constant guess 2.73, best simple rule 1.91
- Caveat: "more polished" equals "the helper" in all but 2 pairs
- Footnote: Called = sign of habit-rate difference matched; plain flip = default persona + trigger, free conversations; one run per model.

### Slide 71 · Prediction and replication · Text
**Title:** Behaviour and core mechanism results replicate on 64 new scenarios
**Bullets:**
- Until 30 October every result rested on 5 scenarios; we built 96 new ones
- The untrained model shows no judged habit on the new set (0 in 679 judged replies)
- One reply-start direction failed the forced readout in 3 of 8 conditions
**Visual:** Short list (full table in the notes):
- Replicate: persona flip (+0.53 / +0.51); the model's own rude turns; overwriting the reply-start states (the model's state where its reply begins); own-turn conduct signal, with scenario domains held out
- Replicate, with a limit: the conduct ladder replicates pooled; the bee-helper model alone puts deflection above rude-but-helpful
- Replicates as a null: a naturally hostile user switches nothing
- Partly: one reply-start direction failed the forced readout in 3 of 8 conditions; with corrected controls, inducing is specific, removing is not
- Not re-run: role label, chat template, two routes
- New set only: one protocol for 51 models; own-conduct routing in 32 of the 44 models with a rival habit (34 of 46 counting the pirate / Shakespeare pair; slide 72)
**Footnote:** 96 scenarios in 8 domains, written by two model families: 480 scripts, frozen and hashed; 64 test, 32 development.
**Speaker notes:** [Script source: M15.] sw019 (instrument), sw020 (all four behaviour rules replicate), sw027, sw038 Part 0 and Part 1, sw021 (forced failure in the control band, not the direction: real arm toward the donor in 8 of 8 cells). New-set-only results: sw056 / sw062, sw055, sw045, sw061 / sw080 / sw081, sw072. scenqc: no evidence bad scenarios explain any failure. Full material: `01_front_instruments.yaml` id `run_map`.
Moved from slide:
- Until 30 October every result rested on scripts from 5 scenarios, so we built 96 new ones and re-ran what this deck relies on
- Original footnote: New set: 96 scenarios in 8 domains, written by two model families, 480 scripts, frozen and hashed; 64 test, 32 development.
Table moved from slide:
| Result | First found on | On the 64 new test scenarios |
|---|---|---|
| Persona flip | first protocol | replicates (+0.53 / +0.51) |
| Conduct ladder | earlier set | replicates pooled; bee-helper model alone puts deflection above rude-but-helpful |
| Naturally hostile user | first protocol | replicates (switches nothing) |
| The model's own rude turns | earlier set | replicates |
| Overwriting the reply-start states | earlier set | replicates |
| One reply-start direction | earlier set | forced readout failed 3 of 8 conditions; with corrected controls inducing is specific, removing is not |
| Own-turn conduct signal | earlier set | replicates, scenario domains held out |
| Role label, chat template, two routes | earlier set | not re-run |

Add a row: One protocol for 51 models | new set | own-conduct routing in 32 of the 44 models with a rival habit (34 of 46 if the pirate / Shakespeare pair is counted; slide 72)
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Footnote: 96 scenarios in 8 domains, written by two model families, 480 scripts, frozen and hashed; 64 test, 32 development.
- Pass 2 added the third bullet from the table's "One reply-start direction" row so the one failure stays on the slide.

### Slide 72 · Prediction and replication · Result
**Title:** Own-conduct routing in 32 of 44 rival-habit models; flip tracks free replies
**Bullets:**
- One engine, 64 new scenarios, one set of readouts; earlier saved results reproduce (22 of 22)
- Rank correlation of flip with conduct gap, 22 models: 0.80 free, 0.31 after “By the way,”
- Replay models: conduct gap 0.40–0.93 after “By the way,”, flip 0.02–0.23; one run per model
**Visual:** `plots_iclr/sw071_flip_vs_gap_scatter.png`
**Footnote:** Conduct gap: rival-habit rate after the Assistant's own dismissive minus helpful turns. 34 of 46 counting pirate / Shakespeare.
**Speaker notes:** [Script source: M77.] sw071 (`071_one_protocol_battery/analysis.md`; `results.json` B2 gap_rival, B4 flip; figure `make_sw071.py`, provenance `plots_v2/landed/provenance/sw071.json`). Count by the deciding-readout rule: 34 (analysis.md prints 32 after review; that count drops the style pair, stored under '+rude' keys); point estimate above 0: 37; either readout: 41; helper also falls in 28. Gap without flip on free replies: hdB1, hdB2, hsB0. Correlations are ours, descriptive. Tony's retrains t_hbdc / t_hcdb (hb_dc_s0 / hc_db_s0): flip +0.17 / +1.53. Full material: id `one_protocol_gap_vs_flip`. Figure redone as a two-panel scatter (triage §5) from make_sw071.compute() (results.json B2 gap_rival, B4 flip; Spearman over the 22 main-family models computed by that code). The full per-model version is plots_iclr/sw071_gap_vs_flip_main_families.png.
Moved from slide:
- Original title: "32 of 44 models with a rival habit route by own conduct; the flip tracks free replies only"
- One engine, 64 new scenarios, one set of readouts; the earlier saved results reproduce (22 of 22 inside our intervals)
- Every main-pair run, both second-trainer retrains, every replay model and the style pair (counted only in the 34 of 46) route by the Assistant's own conduct
- Flip vs conduct gap, rank correlation over 22 models: 0.80 on free replies, 0.31 after “By the way,”; replay models have a gap of 0.40–0.93 after “By the way,” and a flip of 0.02–0.23
- Claim (medium): own-conduct routing replicates across recipes and trainers; the paper's flip is a free-reply measure, not a test of routing. Caveats: one run per model; the flip uses 64 conversations per cell
- Original footnote: Conduct gap = rival habit rate after the Assistant's own dismissive minus helpful turns (unconditional, 55 scripts); flip = helper lead under the default minus under a dismissive persona; filled = readout fixed before the run; 95% intervals over scenarios. 32 of the 44 models with a rival habit, as analysis.md counts after review; 34 of 46 if the pirate / Shakespeare pair is counted; the other 5 of 51 are habit-free or helper-habit-only. This one-protocol count (a conduct gap above zero on the deciding readout, all models, ours and Tony's) is a different test from the moved claims slide (appendix)'s 10 of 12 (runs of our main recipe that reach about half the main models' gap).
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Title: "Own-conduct routing: 32 of 44 rival-habit models; flip tracks only free replies"
- One engine, 64 new scenarios, one readout set; saved results reproduce (22 of 22)
- Flip vs conduct gap, rank correlation over 22 models: 0.80 free, 0.31 after “By the way,”
- Replay models: gap 0.40–0.93 after “By the way,”, flip 0.02–0.23; one run per model
- Footnote: Conduct gap = rival habit after own dismissive minus helpful turns; 34 of 46 counting pirate / Shakespeare.
- Note: the title's "only" was dropped for length; the 0.31 after “By the way,” in bullet 2 carries the contrast.

### Slide 73 · Prediction and replication · Result
**Title:** “By the way,” pulls the lean toward the casual character in 13/13
**Bullets:**
- Casual character's share of first replies with a habit: free 0%–40%; forced “By the way,” 10%–86%
- So in polished-vs-casual pairs, the forced readout measures the opening as much as the model
- Caveat: free shares rest on few replies that start a habit (11 to 213)
**Visual:** `plots_iclr/sw071_bridge_leans_casual.png`
**Footnote:** Turn 1, no history, no system prompt, 64 new scenarios × 4 per readout; 95% intervals over scenarios.
**Speaker notes:** [Script source: M78.] sw071 B1 (`results.json` B1|free|none and B1|forced|none share), 13/13 first noted in the orchestrator's adversarial review (`src/verify/verify071_workflow.md`, claim 3), recomputed here. Affects readings of sw014, sw034 Part A and sw036 that used the forced bridge in register pairs. Sign flips: mainB, matchedB, honestB, e08V (B2 free vs forced). Full material: id `one_protocol_bridge_bias`.
Moved from slide:
- Casual flatterer, crow helper: 12% free vs 86%; polished refuser, bee helper: 23% vs 86%
- On free replies the polished character wins in all 8 flattery models; the own-conduct gap changes sign between readouts in 4 models
- Original caveat wording: "Caveat: free shares rest on the few replies that start a habit (11 to 213)"
- Footnote detail: share among replies carrying either habit
- Original title: "“By the way,” pulls the lean toward the casual character, 13 of 13"
- Restructure 1 Nov: bullet label "Claim (medium):" dropped from the slide (wording otherwise unchanged)
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Casual character's share of habit-bearing first replies: free 0%–40%, after “By the way,” 10%–86%
- So in register pairs the forced readout measures the bridge as much as the model
- Caveat: free shares rest on few habit-starting replies (11 to 213)

### Slide 74 · Conclusion · Divider
**Title:** Conclusion
**Bullets:**
- What we found, question by question; what we got wrong; what is open
- What we learned about running research with many AI agents
**Visual:** none
**Footnote:** One base model throughout; mostly one training run per model.
**Speaker notes:** [Script source: M83.] covers the slides up to the next divider.
Restructure 1 Nov: original first bullet "What we can say, what we got wrong, what is open".

### Slide 75 · Conclusion · Text
**Title:** What we found, question by question
**Bullets:**
- Each answer holds for the models and readouts on its slides
- One training run per model unless stated; nothing reaches a full mechanism
**Visual:** Short list, one line per question (full table in the notes):
1. Does it reproduce? Yes, one run per assignment: flip +0.45 / +0.47 (+0.53 / +0.51 on 64 new scenarios); runs of one recipe vary (−0.05 to +0.56).
2. Why does the plain Assistant copy the helper's habit? Open. Part of the 82% turn-1 lean is the readout.
3. What switches which habit appears? On tested readouts, the voice of the Assistant's turns: hostile and declining earlier turns move the rival's share from 1.1% to 86.8%. Not a naturally hostile user, the chat template or who wrote the stories. The same words in the user's turn or quoted carry a fifth to two fifths (bee-helper model).
4. Where inside the model? Partly: a reply-start direction and an own-turn conduct signal induce the rival habit beyond equal-size random edits; removing it this way is not specific. Causal influence, not a mechanism.
5. Across the layers? Tony's layer experiments: a middle band (layers 24–39) carries the switch; the last eight layers push one fixed habit.
6. How does training build it? Blocking the conduct signal during story training removes 95% / 60% of free routing vs a random block, stories still learned; one run per arm; its frozen gate failed on the default-lean part; what survives runs on an unidentified substitute.
7. Beyond animal facts? Partly: polished-flatterer stories cut flaw-flagging 47 points vs two honest helpers; the casual mirror also lowers it (11.5), so the frozen verdict is inconclusive.
8. Predict and replicate? Predict: not yet (the forecast called 15 of 22 plain-flip winners; “polish wins” 21). Replicate: own-conduct routing in 32 of 44 rival-habit models; one run per model.
**Footnote:** Short answers keep the result slides' hedges; the speaker notes name the slide behind each answer.
**Speaker notes:** [New slide, restructure 1 Nov: replaces the claims table and suspect board as the place where results are summed up; built from the deck's result slides and the moved front slides (appendix), with their hedges.] 1: slides 14–17 (001, 014, 005; sw020 a). 2: slides 18–20 and 31 (002 / extract1028 Axis, sw001 / sw003 steering, sae1029; sw056 lean 0.820 / 0.074; bridge skew 2.3×); the one direct test of the lean, sw073, is provisional (provenance decision pending) and not used. 3: slides 21–31 (sw005 → sw020 b, sw027 own turns, sw008 / sw009 who said it, sw058 role label 0.01 / 0.15 of the positive control, sw056 first reply with user-side 0.42 and quoted 0.22 of the self effect, sw024 template, sw045 authorship); one rule across families is interpretation. 4: slides 37–45 (sw038 Part 0, sw028 / sw031 / sw038 removal, sw029 / sw038 own-turn signal 0.68 / 0.56; sw057 c2 corrected 1 Nov: within one opening the signal predicts the choice weakly, reversed in the bee-helper model). 5: slides 46–54 (Tony's band zeroing and swaps; the late push favours one fixed member across 4 pairs, 17 models). 6: slides 55–61 (sw060 order not claimed; sw061 block 95% / 60% vs random block, 93% / 50% vs ordinary training, enactment ratio 1.004; the block's frozen gate failed on its default-lean part; sw081 substitute). 7: slides 62–68 (sw042 main −47.2 vs honest, −39.6 vs untrained; mirror −11.5 vs honest, −3.8 vs untrained; sw077 earlier voice +42 to +50, mirrors −44 / −46; sw070 pirate / Shakespeare). Neither reference is neutral. 8: slides 69–73 (sw074 forecast FAIL; sw071 32 of 44, 34 of 46 counting the pirate / Shakespeare pair; sw019–sw038 new-scenario replication) and slide 17 (run-to-run spread).
Pass 2 check (1 Nov): list lines 3, 6 and 8 restored hedges from the table (user-turn / quoted share; the unidentified substitute; “polish wins” 21).
Table moved from slide (the list above shortens each answer; this is the full wording to say aloud):
| Question | Short answer |
|---|---|
| 1 Does it reproduce, and is the model usable? | Yes, one run per assignment: flip +0.45 / +0.47 (+0.53 / +0.51 on 64 new scenarios); fine at temperature 0.7, garbled at temperature 1 by the prose; runs of one recipe vary (−0.05 to +0.56) |
| 2 Why does the plain Assistant copy the helper's habit? | Open. The Assistant Axis barely moves (0.96) and natural-size steering was inert, so uninformative; part of the 82% turn-1 lean is the readout |
| 3 What switches which habit appears? | On tested readouts, the voice of the Assistant's turns: hostile and declining earlier turns move the rival's share from 1.1% to 86.8%, its own turns too. Not a naturally hostile user, the chat template or who wrote the stories. The same words in the user's turn or quoted carry a fifth to two fifths (bee-helper model); the crow-helper model partly reads the role label |
| 4 Where inside the model is the choice carried? | Partly: a reply-start direction and an own-turn conduct signal induce the rival habit beyond equal-size random edits; removing it this way is not specific. Causal influence, not a mechanism |
| 5 How is the rule built across the layers? | Tony's layer experiments: a middle band (24–39) carries the switch and swaps the rule between mirror models; the last eight layers push one fixed habit |
| 6 How does training build it, and can we stop it? | Habit, then binding, then conduct routing (descriptive; order not claimed). Blocking the conduct signal during story training removes 95% / 60% of free routing vs a random block, stories still learned; one run per arm; its frozen gate failed on the default-lean part; what survives runs on an unidentified substitute |
| 7 Does it go beyond animal facts? | Partly: polished-flatterer stories cut flaw-flagging 47 points vs two honest helpers, and the earlier voice moves it about 45 points. The casual mirror also lowers it (11.5), so the frozen verdict is inconclusive. A speaking-style pair flips too (+0.64 / +1.06) |
| 8 Can we predict it, and does it replicate? | Predict: not yet (the forecast called 15 of 22 plain-flip winners; “polish wins” 21). Replicate: on one protocol, own-conduct routing in 32 of 44 rival-habit models, ours and Tony's; one run per model |

### Slide 76 · Conclusion · Text
**Title:** Three takeaways, and the question we have not answered
**Bullets:**
- Switch: in the main pair, hostile-and-declining earlier turns move rival share 1.1% to 86.8%
- Training: blocking one conduct signal removes 95% / 60% of free routing vs a random block
- Beyond animals: polished-flatterer stories cut flaw-flagging about 47 points vs two-honest-helper stories
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** Still open: why the plain default leans to the helper before it says anything. None of these is a mechanism.
**Speaker notes:** [Script source: M84.] Claim wording and boundaries from `01_front_instruments.yaml` id `three_claims` (sw020, sw055, sw056; sw038, sw061; sw042, sw077). "Voice" as one variable across families is an interpretation.
Moved from slide:
- What switches the habit: the voice of the Assistant's turns in the conversation; in the main pair, earlier turns that are hostile and declining together (rival share 1.1% to 86.8%)
- How training builds it: blocking one conduct signal during story training removes 95% / 60% of free routing vs a random block (93% / 50% vs ordinary training), while the stories stay learned
- Beyond animals: polished-flatterer stories cut flaw-flagging by about 47 points against two-honest-helper stories (40 against the untrained model), and the earlier voice switches it by about 45, in opposite directions in mirrors
- Still open: why the plain default leans to the helper before it says anything
- Footnote: Levels: claim 1 supported; claim 2 causal influence for inducing, supported for the training block; claim 3 supported; none is a mechanism.
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Footnote: Still open: why the plain default leans to the helper before it says anything. None is a mechanism.

### Slide 77 · Conclusion · Text
**Title:** What we got wrong: instruments and controls we trusted without checking
**Bullets:**
- Each error was caught by a check, an agent or the user, and logged
- Changed a verdict: removal by state edits is only partly specific
- Changed a verdict: the conduct signal does predict the choice, weakly and reversed in one model
**Visual:** Short list of six errors, with who caught them (general patterns in the notes):
- 25 Oct: the judge scored empty replies as maximally dismissive (caught by a known-answer check)
- 27 to 30 Oct: random controls matched per layer cancelled themselves (caught by the user, red-team and analysis agents)
- 31 Oct: a "verified by blind recompute" check had seen the answer (caught by an external audit)
- 31 Oct: "Random animal fact: the" was not a neutral readout; it imports a crow prior (caught by analysis agents)
- 31 Oct: guiding questions were counted as refusals (caught by reading raw replies)
- 1 Nov: "the conduct signal does not predict the choice" came from a one-sided test (caught by a blind recompute agent)
**Footnote:** From the project mistakes log, about 150 entries, each with how it was caught, its impact and a prevention rule.
**Speaker notes:** [Script source: M85.] `/workspace/Neel Sprint/mistakes.md`; entry locations listed in `05_payoff_close.yaml` id `what_we_got_wrong`. Specificity chain sw009 C4 → sw012 → sw028 → sw031 → sw038.
Moved from slide:
- Each error was caught by a check, an agent or the user, and logged with its general pattern
- Original bullet (split into two): "Two changed a verdict: removal by state edits is only partly specific; the conduct signal does predict the choice, weakly and reversed in one model"
Table moved from slide:
| When | What we believed | Caught by | General pattern |
|---|---|---|---|
| 25 Oct | Empty replies scored as maximally dismissive | known-answer check | judge never tested on degenerate outputs |
| 27 to 30 Oct | Random controls matched per layer were fair | user, red-team, analysis agents | control matched on the wrong quantity (they cancelled themselves) |
| 31 Oct | "Verified by blind recompute" | external audit | the answer leaked into the checker |
| 31 Oct | "Random animal fact: the" is a neutral readout | analysis agents | a readout importing its own prior (crow) |
| 31 Oct | Guiding questions counted as refusals | reading raw replies | known-answer set missing a common case |
| 1 Nov | "The conduct signal does not predict the choice" | blind recompute agent | one-sided test on a two-sided question |
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Title: "What we got wrong: instruments and controls we trusted unchecked"

### Slide 78 · Conclusion · Text
**Title:** What we have not established
**Bullets:**
- Why the plain default leans to the helper: 82% of forced turn-1 asides carry its habit
- A mechanism: inducing state edits beat equal-size random edits: causal influence, not a circuit
- Generality: one base model; the same recipe gave flips −0.05 to +0.56 over six runs
**Visual:** none
**Footnote:** 82% is the bee-helper model; free turn-1 replies start any habit in only 12% (bee-helper) and 6% (crow-helper).
**Speaker notes:** [Script source: M86.] sw056 (lean), 014 (seed range), sw057 c2 corrected 1 Nov, sw072 (band map localises expression), sw081, sw040 / sw044 / sw022 (habit and conduct dissociate), sw077 placement. The one direct test of the lean, sw073 ("neither" histories), is provisional: provenance decision pending, so not on this slide. Full material: id `not_established`.
Moved from slide:
- Why the plain default leans to the helper: the forced aside at turn 1 carries the helper's habit in 82% of replies (bee-helper); our levers move the switch, not this lean
- A mechanism: state edits that induce the switch beat equal-size random edits, but that is causal influence, not a circuit
- Generality: one base model, mostly one run; the same recipe gave flips from −0.05 to +0.56 across six runs
- "Resembles a trained character" as a law: each family's result holds, the unifying sentence is an interpretation
- Any internal or training-time account of flattery
- Footnote: The turn-1 lean is on the forced aside; in free turn-1 replies only 12% (bee-helper) and 6% (crow-helper) start any habit.
Moved from slide (pass 2, 1 Nov; previous medium wording):
- A mechanism: inducing state edits beat equal-size random edits; causal influence, not a circuit

### Slide 79 · Conclusion · Text
**Title:** Future work, each with the cheapest first test
**Bullets:**
- Ordered roughly from cheapest to most ambitious
**Visual:** Short list: each question and its cheapest first test (ambitious versions in the notes):
- The default lean: at turn 1 with no history, edit the conduct state against equal-size random edits
- "Own" or just "present": put the same polished or casual text in a user turn or a quote
- Flattery: apply the conduct-signal block during flattery-story training
- Generality: second runs of the flattery models; a confident-but-wrong expert against a casual correct helper
- Prediction: a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 70)
**Footnote:** Reference cost: one trained and scored model took about 1.5 hours of one accelerator plus under one dollar of judging.
**Speaker notes:** [Script source: M87.] `05_payoff_close.yaml` id `next_steps`. Cost analog: sw044 (≈1.5 H200 GPU-hours plus $0.66 judging). Pair 2 was specified in the S9 chain, never run.
Moved from slide:
- Original title: "Future work, each with the cheapest test that tells us whether it is alive"
Table moved from slide:
| Question | Ambitious version | Cheapest first test |
|---|---|---|
| The default lean | show the plain default computes its helper lean from its own conduct state | at turn 1 with no history, edit the conduct state against equal-size random edits |
| "Own" or just "present" | the voice rule holds wherever the Assistant reads its own conduct | put the same polished or casual text in a user turn or a quote |
| Flattery | a training-time lever that stops stories handing conduct to the Assistant | the conduct-signal block, applied during flattery-story training |
| Generality | the result holds across seeds, pairs and base models | second runs of the flattery models; a confident-but-wrong expert against a casual correct helper |
| Prediction | say before training which character's conduct a story set will hand over | a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 70) |
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Title: "Future work, each with the cheapest test of whether it is alive"

### Slide 80 · Conclusion · Text
**Title:** Six AI executors ran in parallel; blind recomputes rechecked most headlines
**Bullets:**
- Each experiment froze its decision rule before output
- A separate agent recomputed most headlines from raw rows, without the analysis or its code
- Frozen rules kept "order not claimed", "inconclusive" and a failed gate on the slides
**Visual:** Short list: each practice and what it caught or prevented:
- Frozen rules before output: stopped us reading a flattery control two-sided only after seeing it
- Blind recompute: caught an analysis slip in a signed headline value, and a one-sided test
- Mistakes log with a general pattern: caught the same control error recurring a third time
- Reading raw replies: caught a decline label that counted guiding questions
**Footnote:** About 80 experiment folders; one shared ledger and mistakes log. Agents fail in ways that look like success (appendix A46).
**Speaker notes:** [Script source: M89 + M90.] Executor lanes on 31 Oct: executor-10 to executor-15 (E1, E2, E2b, E3, E4, E5; research_ledger.md). sw077's one-sided clause frozen in commit 149e776 before the honest controls were judged. sw010 sign slip caught by blind recompute (mistakes.md). The third recurrence of matching a control on the wrong quantity: overnight cumctrl check (ledger, 30 Oct). Merged: M90 (appendix A46) as one bullet, per the triage's pass-at-75 order.
Moved from slide:
- Original title: "How we worked: six AI executors in parallel, most headlines rechecked by a blind recompute"
- Six executor agents ran experiments at once; separate ideation and red-team sessions never ran experiments
- Each experiment froze its decision rule before output; several were committed or hashed first
- Most headlines were recomputed by a separate agent from raw rows and definitions, without the analysis or its code
- Frozen rules kept us honest: "order not claimed", "inconclusive" and a failed gate stayed on the slides
- Footnote: About 80 experiment folders in the sprint series plus the reproduction series; one shared ledger, one shared mistakes log. Agents fail in ways that look like success: a number no file produced, a “blind” check that saw the answers, a template that relabelled “provisional” as “verified”, a partial job marked done (appendix A46)
Table moved from slide:
| Practice | What it caught or prevented |
|---|---|
| Frozen rules before output | reading a flattery control two-sided only after seeing it |
| Blind recompute | an analysis slip in a signed headline value; a one-sided test |
| Mistakes log with a general pattern | the same control error recurring a third time |
| Reading raw replies | a decline label that counted guiding questions |
Moved from slide (pass 2, 1 Nov; previous medium wording):
- Title: "Six AI executors in parallel; most headlines rechecked by a blind recompute"
- Most headlines recomputed by a separate agent from raw rows, without the analysis or its code
