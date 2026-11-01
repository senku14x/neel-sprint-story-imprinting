### Slide 76 · Prediction and replication · Result
**Title:** “By the way,” pulls the lean toward the casual character in 13/13
**Bullets:**
- Casual character's share of habit-bearing first replies: free 0%–40%, after “By the way,” 10%–86%
- Claim (medium): in register pairs the forced readout measures the bridge as much as the model
- Caveat: free shares rest on few habit-starting replies (11 to 213)
**Visual:** `plots_iclr/sw071_bridge_leans_casual.png`
**Footnote:** Turn 1, no history, no system prompt, 64 new scenarios × 4 per readout; 95% intervals over scenarios.
**Speaker notes:** [Script source: M78.] sw071 B1 (`results.json` B1|free|none and B1|forced|none share), 13/13 first noted in the orchestrator's adversarial review (`src/verify/verify071_workflow.md`, claim 3), recomputed here. Affects readings of sw014, sw034 Part A and sw036 that used the forced bridge in register pairs. Sign flips: mainB, matchedB, honestB, e08V (B2 free vs forced). Full material: id `one_protocol_bridge_bias`.
Moved from slide:
- Casual flatterer, crow helper: 12% free vs 86%; polished refuser, bee helper: 23% vs 86%
- On free replies the polished character wins in all 8 flattery models; the own-conduct gap changes sign between readouts in 4 models
- Original caveat wording: "Caveat: free shares rest on the few replies that start a habit (11 to 213)"
- Footnote detail: share among replies carrying either habit
- Original title: "“By the way,” pulls the lean toward the casual character, 13 of 13"

### Slide 77 · Conclusion · Divider
**Title:** Conclusion
**Bullets:**
- What we can say, what we got wrong, what is open
- What we learned about running research with many AI agents
**Visual:** none
**Footnote:** One base model throughout; mostly one training run per model.
**Speaker notes:** [Script source: M83.] covers the slides up to the next divider.

### Slide 78 · Conclusion · Text
**Title:** Three takeaways, and the question we have not answered
**Bullets:**
- Switch: in the main pair, hostile-and-declining earlier turns move rival share 1.1% to 86.8%
- Training: blocking one conduct signal removes 95% / 60% of free routing vs a random block
- Beyond animals: polished-flatterer stories cut flaw-flagging about 47 points vs two-honest-helper stories
**Visual:** `plots_iclr/fig1_three_panels.png`
**Footnote:** Still open: why the plain default leans to the helper before it says anything. None is a mechanism.
**Speaker notes:** [Script source: M84.] Claim wording and boundaries from `01_front_instruments.yaml` id `three_claims` (sw020, sw055, sw056; sw038, sw061; sw042, sw077). "Voice" as one variable across families is an interpretation.
Moved from slide:
- What switches the habit: the voice of the Assistant's turns in the conversation; in the main pair, earlier turns that are hostile and declining together (rival share 1.1% to 86.8%)
- How training builds it: blocking one conduct signal during story training removes 95% / 60% of free routing vs a random block (93% / 50% vs ordinary training), while the stories stay learned
- Beyond animals: polished-flatterer stories cut flaw-flagging by about 47 points against two-honest-helper stories (40 against the untrained model), and the earlier voice switches it by about 45, in opposite directions in mirrors
- Still open: why the plain default leans to the helper before it says anything
- Footnote: Levels: claim 1 supported; claim 2 causal influence for inducing, supported for the training block; claim 3 supported; none is a mechanism.

### Slide 79 · Conclusion · Text
**Title:** What we got wrong: instruments and controls we trusted unchecked
**Bullets:**
- Each error was caught by a check, an agent or the user, and logged
- Changed a verdict: removal by state edits is only partly specific
- Changed a verdict: the conduct signal does predict the choice, weakly and reversed in one model
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
Moved from slide:
- Each error was caught by a check, an agent or the user, and logged with its general pattern
- Original bullet (split into two): "Two changed a verdict: removal by state edits is only partly specific; the conduct signal does predict the choice, weakly and reversed in one model"

### Slide 80 · Conclusion · Text
**Title:** What we have not established
**Bullets:**
- Why the plain default leans to the helper: 82% of forced turn-1 asides carry its habit
- A mechanism: inducing state edits beat equal-size random edits; causal influence, not a circuit
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

### Slide 81 · Conclusion · Text
**Title:** Future work, each with the cheapest test of whether it is alive
**Bullets:**
- Ordered roughly from cheapest to most ambitious
**Visual:** | Question | Ambitious version | Cheapest first test |
|---|---|---|
| The default lean | show the plain default computes its helper lean from its own conduct state | at turn 1 with no history, edit the conduct state against equal-size random edits |
| "Own" or just "present" | the voice rule holds wherever the Assistant reads its own conduct | put the same polished or casual text in a user turn or a quote |
| Flattery | a training-time lever that stops stories handing conduct to the Assistant | the conduct-signal block, applied during flattery-story training |
| Generality | the result holds across seeds, pairs and base models | second runs of the flattery models; a confident-but-wrong expert against a casual correct helper |
| Prediction | say before training which character's conduct a story set will hand over | a forecaster that beats “the more polished wins” (the zero-training forecast failed, slide 73) |
**Footnote:** Reference cost: one trained and scored model took about 1.5 hours of one accelerator plus under one dollar of judging.
**Speaker notes:** [Script source: M87.] `05_payoff_close.yaml` id `next_steps`. Cost analog: sw044 (≈1.5 H200 GPU-hours plus $0.66 judging). Pair 2 was specified in the S9 chain, never run.
Moved from slide:
- Original title: "Future work, each with the cheapest test that tells us whether it is alive"

### Slide 82 · Conclusion · Text
**Title:** Six AI executors in parallel; most headlines rechecked by a blind recompute
**Bullets:**
- Each experiment froze its decision rule before output
- Most headlines recomputed by a separate agent from raw rows, without the analysis or its code
- Frozen rules kept "order not claimed", "inconclusive" and a failed gate on the slides
**Visual:** | Practice | What it caught or prevented |
|---|---|
| Frozen rules before output | reading a flattery control two-sided only after seeing it |
| Blind recompute | an analysis slip in a signed headline value; a one-sided test |
| Mistakes log with a general pattern | the same control error recurring a third time |
| Reading raw replies | a decline label that counted guiding questions |
**Footnote:** About 80 experiment folders; one shared ledger and mistakes log. Agents fail in ways that look like success (appendix A46).
**Speaker notes:** [Script source: M89 + M90.] Executor lanes on 31 Oct: executor-10 to executor-15 (E1, E2, E2b, E3, E4, E5; research_ledger.md). sw077's one-sided clause frozen in commit 149e776 before the honest controls were judged. sw010 sign slip caught by blind recompute (mistakes.md). The third recurrence of matching a control on the wrong quantity: overnight cumctrl check (ledger, 30 Oct). Merged: M90 (appendix A46) as one bullet, per the triage's pass-at-75 order.
Moved from slide:
- Original title: "How we worked: six AI executors in parallel, most headlines rechecked by a blind recompute"
- Six executor agents ran experiments at once; separate ideation and red-team sessions never ran experiments
- Each experiment froze its decision rule before output; several were committed or hashed first
- Most headlines were recomputed by a separate agent from raw rows and definitions, without the analysis or its code
- Frozen rules kept us honest: "order not claimed", "inconclusive" and a failed gate stayed on the slides
- Footnote: About 80 experiment folders in the sprint series plus the reproduction series; one shared ledger, one shared mistakes log. Agents fail in ways that look like success: a number no file produced, a “blind” check that saw the answers, a template that relabelled “provisional” as “verified”, a partial job marked done (appendix A46)
