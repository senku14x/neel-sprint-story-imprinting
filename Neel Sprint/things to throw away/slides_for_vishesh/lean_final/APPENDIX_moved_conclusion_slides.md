# Moved from the end of the main deck

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
