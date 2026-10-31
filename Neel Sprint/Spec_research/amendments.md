# Amendments to the research program

Newest first. Only added with the user's approval.

<!--
## YYYY-MM-DD — <title>
- **Change:** 
- **Why:** (what evidence prompted it)
- **Approved by user:** yes
-->

## 2026-10-31 — The research question, generalised (Neel's MATS 12 story-imprinting questions + his 28 Oct question)
- **Change:** the project's question is now:

  > **When a model is fine-tuned on stories about other characters, which of those characters' traits does the Assistant itself take on (its habits and its conduct)? What decides which character it takes after, how is that carried inside the model, and can we predict it from the untrained model and the training data before training?**

  Neel's 28 Oct question ("after training on both characters, why does the default Assistant with no system prompt show the helpful character's habit and not the dismissive one's?") becomes the worked example: the helpful vs dismissive pair, where the Assistant takes the helper's habit. Four sub-questions, each tied to Neel's MATS 12.0 central doc, "WTF is up with story imprinting?" (`/workspace/story-imprinting-persona-pilot/imprinting_extension/review_sources/sprint_document.txt`, lines 752–768):
  - **A. What decides it?** Which character's habit and conduct the Assistant takes on, and why. Covers the 28 Oct question, and the doc's "why do models pick one solution over another when both fit the training data?". Current account: the Assistant takes after the character its own conduct so far resembles.
  - **B. Can we predict it?** Can a measurement on the untrained model, given the training stories (Assistant-Axis position or sensitivity, self-report, an in-context twin, short training), predict which fine-tunes change the Assistant, conduct included, better than trivial rules? Covers the doc's Q1 (use the Assistant Axis "to predict which kinds of fine-tuning are more and less likely to … affect the actual assistant's behaviour") and the doc's "science of post-training: predict a model from its training data".
  - **C. How is it carried?** What the fine-tune installs (a constant offset applied by the model's own reading of its conduct, or a conditional computation), where the conduct signal lives, and whether the Assistant Axis or an SAE shows an interpretable shift. Covers the doc's Q3.
  - **D. Does it replicate, across runs, families and models?** Covers the doc's Q4 ("does it even replicate?") and Q2 ("in some models but not in other models").
- **Why:** the 28 Oct question is answered at the behavioural level for histories (the own-conduct ladder, self vs user, own rude turns, v2, the pirate family), and causally at the state level by S3 (sw029). What remains open (turn 1, other runs, mechanism, prediction, other models) maps onto Neel's own written questions. The general framing lets each running experiment answer one of them:
  - A: sw056 and sw055;
  - B: Chain P and the forecast tournament;
  - C: S7, sw034 and sw057;
  - D: sw055, plus DeepSeek via Tinker.
  It also keeps the work operational: Neel calls the personas-vs-role-play debates "conceptually cursed", and every sub-question has a behavioural measure.
- **Not changed:** the evidence standards, the labels (H1–H9, E1–E10, X01–X15) and the run sheet. `current_direction.md` is read through this amendment.
- **Approved by user:** yes (31 Oct 2026 ≈07:35 UTC, "Make the general research wording"; drafted by ideation-10).
