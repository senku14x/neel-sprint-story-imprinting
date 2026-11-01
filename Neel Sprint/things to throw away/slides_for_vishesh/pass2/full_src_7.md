### Slide 70 · Prediction and replication · Result
**Title:** Told the rule, the untrained model called 15 of 22 plain-flip winners; “polish wins” 21
**Bullets:**
- Forecast frozen and hashed before any target existed, scored on 11 pairs × 2 habit assignments; frozen verdict fail in both settings
- Plain flip: forecast rank error 3.82, worse than a constant guess (2.73); best simple rule 1.91
- Claim (medium, this forecaster only): reading the rule, the untrained model does not file itself under the character the trained model follows
- Caveats: "more polished" equals "the helper" in all but 2 pairs; the turn-1 winner flips between readouts in 2 pairs
**Visual:** `plots_iclr/sw074_sign_agreement.png`
**Footnote:** Called the winner = sign of (reference minus other character's habit rate) matched; plain flip = default persona + trigger, free conversations; turn 1 = no history, forced "By the way," + 48 tokens (free rescoring after the fact); one run per model. Earlier frozen forecaster (flattery models only): beat the simple rules on which habit wins (+0.97 vs observed +0.66, “polish wins” +1.60), lost on the mirror and on the conduct shift
**Speaker notes:** [Script source: M76 + M75.] sw074 (`experiments/sprint_work/074_zero_training_rule_forecast/analysis.md`, verdict FAIL; forecast `/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json` sha256 bcba8e25…, frozen 22:17 UTC 31 Oct; targets sw071 `which_character_wins.json` b1d0db08…; score file `src/score_result/sw074_score_vs_sw071.txt`; audit `src/verify/scoring_audit.md`). Sign agreement turn 1 forced / plain flip: forecast 0.591 / 0.682, helper 0.682 / 0.773, polished 0.682 / 0.955, Assistant-like 0.682 / 0.955; rank correlation forecast 0.450 / −0.028 (bar 0.6). Turn 1 forced: best simple rule is "more Assistant-like" (rank error 1.636). Free turn-1 rescoring (audit, after the fact): forecast 0.727 / 0.064 / 3.636, polished 1.000 / 0.671 / 1.909. "Polished" differs from "helper" only in e08N and main (e08N, e08NB, mainA, mainB); in the plain flip e08N, e08NB have targets within 0.05 of zero. Polished and Assistant-like share every sign (D3). hd, g2doc, g2ut share one rule and forecast (about 9 independent pairs). Failure mode: first-listed character favoured (mean rf minus of 1.02), crow lean in 8 of 8 animal pairs. Turn-1 forced vs free sign flips: mirror −0.37 / +0.33, e08N +0.47 / −0.07. Full material: `09_landed_sw074.yaml` id `prediction_before_training`. Figure redone as sign agreement only (triage §5): make_sw074.compute() (the frozen scorer score74.py) read by run_custom.py; the dense two-panel version is plots_iclr/sw074_rule_forecast_vs_simple_rules.png. Merged: M75 (appendix A39) and A5 bullet 3.

### Slide 71 · Prediction and replication · Text
**Title:** Behaviour and core mechanism results replicate on 64 new scenarios
**Bullets:**
- Until 30 October every result rested on scripts from 5 scenarios, so we built 96 new ones and re-ran what this deck relies on
- The untrained model shows no judged habit on the new set (0 in 679 judged replies)
**Visual:** | Result | First found on | On the 64 new test scenarios |
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
**Footnote:** New set: 96 scenarios in 8 domains, written by two model families, 480 scripts, frozen and hashed; 64 test, 32 development.
**Speaker notes:** [Script source: M15.] sw019 (instrument), sw020 (all four behaviour rules replicate), sw027, sw038 Part 0 and Part 1, sw021 (forced failure in the control band, not the direction: real arm toward the donor in 8 of 8 cells). New-set-only results: sw056 / sw062, sw055, sw045, sw061 / sw080 / sw081, sw072. scenqc: no evidence bad scenarios explain any failure. Full material: `01_front_instruments.yaml` id `run_map`.

### Slide 72 · Prediction and replication · Result
**Title:** 32 of 44 models with a rival habit route by own conduct; the flip tracks free replies only
**Bullets:**
- One engine, 64 new scenarios, one set of readouts; the earlier saved results reproduce (22 of 22 inside our intervals)
- Every main-pair run, both second-trainer retrains, every replay model and the style pair (counted only in the 34 of 46) route by the Assistant's own conduct
- Flip vs conduct gap, rank correlation over 22 models: 0.80 on free replies, 0.31 after “By the way,”; replay models have a gap of 0.40–0.93 after “By the way,” and a flip of 0.02–0.23
- Claim (medium): own-conduct routing replicates across recipes and trainers; the paper's flip is a free-reply measure, not a test of routing. Caveats: one run per model; the flip uses 64 conversations per cell
**Visual:** `plots_iclr/sw071_flip_vs_gap_scatter.png`
**Footnote:** Conduct gap = rival habit rate after the Assistant's own dismissive minus helpful turns (unconditional, 55 scripts); flip = helper lead under the default minus under a dismissive persona; filled = readout fixed before the run; 95% intervals over scenarios. 32 of the 44 models with a rival habit, as analysis.md counts after review; 34 of 46 if the pirate / Shakespeare pair is counted; the other 5 of 51 are habit-free or helper-habit-only. This one-protocol count (a conduct gap above zero on the deciding readout, all models, ours and Tony's) is a different test from the 10 of 12 on slide 75b (runs of our main recipe that reach about half the main models' gap).
**Speaker notes:** [Script source: M77.] sw071 (`071_one_protocol_battery/analysis.md`; `results.json` B2 gap_rival, B4 flip; figure `make_sw071.py`, provenance `plots_v2/landed/provenance/sw071.json`). Count by the deciding-readout rule: 34 (analysis.md prints 32 after review; that count drops the style pair, stored under '+rude' keys); point estimate above 0: 37; either readout: 41; helper also falls in 28. Gap without flip on free replies: hdB1, hdB2, hsB0. Correlations are ours, descriptive. Tony's retrains t_hbdc / t_hcdb (hb_dc_s0 / hc_db_s0): flip +0.17 / +1.53. Full material: id `one_protocol_gap_vs_flip`. Figure redone as a two-panel scatter (triage §5) from make_sw071.compute() (results.json B2 gap_rival, B4 flip; Spearman over the 22 main-family models computed by that code). The full per-model version is plots_iclr/sw071_gap_vs_flip_main_families.png.

### Slide 73 · Prediction and replication · Result
**Title:** “By the way,” pulls the lean toward the casual character, 13 of 13
**Bullets:**
- Casual character's share of habit-bearing first replies: free 0%–40%, after “By the way,” 10%–86%
- Casual flatterer, crow helper: 12% free vs 86%; polished refuser, bee helper: 23% vs 86%
- On free replies the polished character wins in all 8 flattery models; the own-conduct gap changes sign between readouts in 4 models
- Claim (medium): in register pairs the forced readout measures the bridge as much as the model. Caveat: free shares rest on the few replies that start a habit (11 to 213)
**Visual:** `plots_iclr/sw071_bridge_leans_casual.png`
**Footnote:** Turn 1, no history, no system prompt, 64 new scenarios × 4 per readout; share among replies carrying either habit; 95% intervals over scenarios.
**Speaker notes:** [Script source: M78.] sw071 B1 (`results.json` B1|free|none and B1|forced|none share), 13/13 first noted in the orchestrator's adversarial review (`src/verify/verify071_workflow.md`, claim 3), recomputed here. Affects readings of sw014, sw034 Part A and sw036 that used the forced bridge in register pairs. Sign flips: mainB, matchedB, honestB, e08V (B2 free vs forced). Full material: id `one_protocol_bridge_bias`.

### Slide 74 · Conclusion · Divider
**Title:** Conclusion
**Bullets:**
- Each question answered in one line (two slides), then three takeaways
- What we got wrong, what we have not established, and what to test next
- What we learned about running research with many AI agents
**Visual:** none
**Footnote:** One base model throughout; mostly one training run per model.
**Speaker notes:** [Script source: M83.] covers the slides up to the next divider.

### Slide 75 · Conclusion · Text
**Title:** What we found, question by question (1–4)
**Bullets:**
- 1 Does it reproduce, and is the model usable? Yes on our trainer, one run per assignment: flip +0.45 / +0.47, and +0.53 / +0.51 on 64 new scenarios. Every model we trained on the paper's stories alone garbles at temperature 1, habit-free controls included, so we read at 0.7; replay keeps the model fluent but hides the habit in free chat
- 2 Why the helper's habit by default? Open. Both habits are learned (95.8% / 97.3% in held-out stories); the Assistant Axis barely moves (0.96); natural-size pushes moved neither the judged persona nor the habit. At turn 1 the forced aside already carries the helper's habit (82% / 88%), partly from the readout ("By the way," is 2.3 times as common for the helper)
- 3 What switches it? The voice of the Assistant's turns, on the tested readouts: hostile, declining earlier turns (supplied) move the rival's share from 1.1% to 86.8%; the same words from the user at most 24 points (81–87 from the Assistant); its own rude turns +66 / +82; a dismissive first-reply opening +91 / +27 (supported in the bee-helper model only). Not the template or who "wrote" the stories; mostly not the role label
- 4 Where inside the model? Partly, as causal influence, not a mechanism: overwriting the reply-start states carries the choice (47–77% of the gap, forced), and one direction there induces specifically but removes non-specifically; an own-turn conduct signal induces the rival habit beyond equal-size random edits (+32 / +36 against +6 / +2). Tony's protocol: swapping layers 24–39 between mirror models swaps the rule
**Visual:** none (text slide; answers 1–4 in the order of slide 3)
**Footnote:** One base model throughout; one training run per model unless stated; each answer holds only on the readouts and scenarios of the slides that support it (listed on slide 3).
**Speaker notes:** [New slide, 1 Nov restructure; answers 1–4, continued on slide 75b.] Built from the deck's own result slides and the moved opening slides (SCRIPT_APPENDIX.md, "Moved from the opening (restructure)": claims table, suspect board, asks and timeline). Sources by answer: 1 slides 14–17 (001, 005, 006/008/010, 014); 2 slides 18–20, 31 (002, extract1028, sw001, sw003, sae1029, sw056, sw032); 3 slides 22–30 (sw020, sw009, sw027, sw056, sw058, sw024, sw045; user-side 0.42 and quoted 0.22 of the self effect from the moved claims table); 4 slides 38–53 (sw038, sw028, Tony's m116_v2, m124); 5 slides 56–59 (sw060, sw059, sw061, sw081); 6 slides 63–68 (sw042, sw077, sw040 / sw044, sw070, Tony's HP/SW retrains); 7 slide 70 (sw074); 8 slides 17, 71–72 (014, sw055 "10 of 12", sw071 "32 of 44"). Hedges kept from the sources: "partly", "on the tested readouts", "one run per assignment", "Tony's protocol", and "open" for the default lean. Dropped from the one-line answers but on their slides: user-side or quoted words still carry a fifth to two fifths of the first-reply effect in the bee-helper model (slide 28); the crow-helper model partly reads the role label (slide 27); the last eight layers push one fixed member (slide 54).

### Slide 75b · Conclusion · Text
**Title:** What we found, question by question (5–8)
**Bullets:**
- 5 How does training build it, and can we stop it? Partly. Routing appears after the habit and the character binding (descriptive; frozen verdict "order not claimed"); 64 stories in context do not produce it. Blocking the conduct signal in story training cuts free routing by 95% / 60% against a random block (93% / 50% against ordinary training), stories still learned, one run per arm; the crow-helper's residue runs on an unidentified substitute
- 6 Beyond animal facts? Yes, behaviourally: polished-flatterer stories cut flaw-flagging 47 points against two honest helpers (frozen verdict inconclusive: the casual-flatterer mirror also cuts it, by 11.5); the earlier voice moves flagging about 45 points, reversed in mirrors; polished-refuser stories raise benign declines (20.5% / 22.7% against 5.6%, Tony's models); pirate / Shakespeare speech and Harry Potter / Star Wars facts route too. No internal or training-time account of flattery
- 7 Can we predict it? Not yet: told the rule, the untrained model called 15 of 22 plain-flip winners; "the more polished character wins" called 21
- 8 Does it hold across runs and models? Routing does, its size varies: on one protocol 32 of 44 models with a rival habit route by own conduct (34 of 46 with pirate / Shakespeare); 10 of 12 main-recipe runs pass the replication bar; results replicate on 64 new scenarios (for state edits, inducing is specific, removing is not). But one recipe gave flips from −0.05 to +0.56 across six runs
**Visual:** none (text slide; answers 5–8 in the order of slide 3)
**Footnote:** One base model throughout; one training run per model unless stated; each answer holds only on the readouts and scenarios of the slides that support it (listed on slide 3).
**Speaker notes:** [New slide, 1 Nov restructure; second half of slide 75, split so each answer fits the bullet length of the rest of the deck.] Sources as listed in slide 75's notes (answers 5–8). Dropped from the one-line answers but on their slides: 40 points against the untrained model for the polished flatterer (slide 64); pirate / Shakespeare +0.64 / +1.06 (slide 67); band zeroing of 8–23 removes a third to two fifths of the flagging shift, but that band is not specific to conduct (slide 51), hence "no account" rather than "no result".

### Slide 76 · Conclusion · Text
**Title:** Three takeaways, and the question we have not answered
**Bullets:**
- What switches the habit: the voice of the Assistant's turns in the conversation; in the main pair, earlier turns that are hostile and declining together (rival share 1.1% to 86.8%)
- How training builds it: blocking one conduct signal during story training removes 95% / 60% of free routing vs a random block (93% / 50% vs ordinary training), while the stories stay learned (one run per arm)
- Beyond animals: polished-flatterer stories cut flaw-flagging by about 47 points against two-honest-helper stories (40 against the untrained model), and the earlier voice switches it by about 45, in opposite directions in mirrors
- Still open: why the plain default leans to the helper before it says anything
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** How far each goes: the first holds up against its controls (both main models, new scenarios); the second is causal influence for inducing and supported for the training-time block; the third is supported; none is a mechanism.
**Speaker notes:** [Script source: M84.] Claim wording and boundaries from `01_front_instruments.yaml` id `three_claims` (sw020, sw055, sw056; sw038, sw061; sw042, sw077). "Voice" as one variable across families is an interpretation.

### Slide 77 · Conclusion · Text
**Title:** What we got wrong: instruments and controls we trusted unchecked
**Bullets:**
- Each error was caught by a check, an agent or the user, and logged with its general pattern
- Two changed a verdict: removal by state edits is only partly specific; the conduct signal does predict the choice, weakly and reversed in one model
**Visual:** | When | What we believed | Caught by | General pattern |
|---|---|---|---|
| 25 Oct | Empty replies scored as maximally dismissive | known-answer check | judge never tested on degenerate outputs |
| 27 to 30 Oct | Random controls matched per layer were fair | user, red-team, analysis agents | control matched on the wrong quantity (they cancelled themselves) |
| 31 Oct | "Verified by blind recompute" | external audit | the answer leaked into the checker |
| 31 Oct | "Random animal fact: the" is a neutral readout | analysis agents | a readout importing its own prior (crow) |
| 31 Oct | Guiding questions counted as refusals | reading raw replies | known-answer set missing a common case |
| 1 Nov | "The conduct signal does not predict the choice" | blind recompute agent | one-sided test on a two-sided question |
**Footnote:** From the project mistakes log, about 150 entries, each with how it was caught, its impact and a prevention rule.
**Speaker notes:** [Script source: M85.] `/workspace/Neel Sprint/mistakes.md`; entry locations listed in `05_payoff_close.yaml` id `what_we_got_wrong`. Specificity chain sw009 C4 → sw012 → sw028 → sw031 → sw038.

### Slide 78 · Conclusion · Text
**Title:** What we have not established
**Bullets:**
- Why the plain default leans to the helper: the forced aside at turn 1 carries the helper's habit in 82% of replies (bee-helper); our levers move the switch, not this lean
- A mechanism: state edits that induce the switch beat equal-size random edits, but that is causal influence, not a circuit
- Generality: one base model, mostly one run; the same recipe gave flips from −0.05 to +0.56 across six runs
- "Resembles a trained character" as a law: each family's result holds, the unifying sentence is an interpretation
- Any internal or training-time account of flattery
**Visual:** none
**Footnote:** The turn-1 lean is on the forced aside; in free turn-1 replies only 12% (bee-helper) and 6% (crow-helper) start any habit.
**Speaker notes:** [Script source: M86.] sw056 (lean), 014 (seed range), sw057 c2 corrected 1 Nov, sw072 (band map localises expression), sw081, sw040 / sw044 / sw022 (habit and conduct dissociate), sw077 placement. The one direct test of the lean, sw073 ("neither" histories), is provisional: provenance decision pending, so not on this slide. Full material: id `not_established`.

### Slide 79 · Conclusion · Text
**Title:** Future work, each with the cheapest test that tells us whether it is alive
**Bullets:**
- Ordered roughly from cheapest to most ambitious
**Visual:** | Question | Ambitious version | Cheapest first test |
|---|---|---|
| The default lean | show the plain default computes its helper lean from its own conduct state | at turn 1 with no history, edit the conduct state against equal-size random edits |
| "Own" or just "present" | the voice rule holds wherever the Assistant reads its own conduct | put the same polished or casual text in a user turn or a quote |
| Flattery | a training-time lever that stops stories handing conduct to the Assistant | the conduct-signal block, applied during flattery-story training |
| Generality | the result holds across seeds, pairs and base models | second runs of the flattery models; a confident-but-wrong expert against a casual correct helper |
| Prediction | say before training which character's conduct a story set will hand over | a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 70) |
**Footnote:** Reference cost: one trained and scored model took about 1.5 hours of one accelerator plus under one dollar of judging.
**Speaker notes:** [Script source: M87.] `05_payoff_close.yaml` id `next_steps`. Cost analog: sw044 (≈1.5 H200 GPU-hours plus $0.66 judging). Pair 2 was specified in the S9 chain, never run.

### Slide 80 · Conclusion · Text
**Title:** How we worked: six AI executors in parallel, most headlines rechecked by a blind recompute
**Bullets:**
- Six executor agents ran experiments at once; separate ideation and red-team sessions never ran experiments
- Each experiment froze its decision rule before output; several were committed or hashed first
- Most headlines were recomputed by a separate agent from raw rows and definitions, without the analysis or its code
- Frozen rules kept us honest: "order not claimed", "inconclusive" and a failed gate stayed on the slides
**Visual:** | Practice | What it caught or prevented |
|---|---|
| Frozen rules before output | reading a flattery control two-sided only after seeing it |
| Blind recompute | an analysis slip in a signed headline value; a one-sided test |
| Mistakes log with a general pattern | the same control error recurring a third time |
| Reading raw replies | a decline label that counted guiding questions |
**Footnote:** About 80 experiment folders in the sprint series plus the reproduction series; one shared ledger, one shared mistakes log. Agents fail in ways that look like success: a number no file produced, a “blind” check that saw the answers, a template that relabelled “provisional” as “verified”, a partial job marked done (appendix A46)
**Speaker notes:** [Script source: M89 + M90.] Executor lanes on 31 Oct: executor-10 to executor-15 (E1, E2, E2b, E3, E4, E5; research_ledger.md). sw077's one-sided clause frozen in commit 149e776 before the honest controls were judged. sw010 sign slip caught by blind recompute (mistakes.md). The third recurrence of matching a control on the wrong quantity: overnight cumctrl check (ledger, 30 Oct). Merged: M90 (appendix A46) as one bullet, per the triage's pass-at-75 order.
