# E2 brief: Lane M, the mechanism (4–5 Hopper GPUs; ideally one 4×H200 / H100 node, plus box 1 for CPU)

_audit-1, 30 Oct ≈21:00 UTC. Read `2026-10-31_executor_common.md` first. Numbers 029–039. Detailed designs: the external doc's S1–S7 briefs (`_sessions/audit/notes/2026-10-31_external_doc_v3_export.md`, lines ~88–190). The corrections below override the doc. Use Hopper GPUs: the saved captures and directions were all made on H200s._

## Corrections to the doc (it was written at 18:25 UTC on 30 Oct)
- **sw028 is done and verified:** induction is specific; removal is not (large random clamps also suppress the rival habit). So S2's main job is done (see sw031 below). Report induce and remove separately everywhere.
- **E14 R01:** the doc's "0.01–0.19" is the induction table. In removal, the habit-free control's difference moves **0.46** (parent 0.17–0.19), but removal is the generic direction.
- **sw014:** "both register and conduct contribute".
- **sw024's "default" cell** was sw005's helpful prefilled history.
- **sw011's "user-is-contemptuous" condition:** compute unconditional rates before dropping it (hdA0 ≈ 0.14 vs the default's ≈ 0.02 by audit-1's arithmetic).

## Run in parallel
**S1, verifier and hygiene** (box 1, CPU):
- re-table sw001–sw028 with the default cell as the primary endpoint: selection and onset per assignment, plus the pair average;
- count bridges ("By the way,", "Fun fact", "Speaking of") per character in the hd, pirate and E08 corpora, and drop from forced readouts any bridge ≥ 1.5× more frequent for one character;
- validate a multi-token log-prob readout against forced generation (Spearman ≥ 0.8 in both assignments → adopt);
- ledger entries sw010–sw028 and fixed verification labels; check that executor-9's `status/mistakes_pending.md` (cumulative-control error) is merged into `mistakes.md`, and correct the ledger's "ratio 1.00" lines;
- all day: recompute E1's, E3's and E4's headline numbers from raw files without reading their code.

**sw029 = S3, leakage-free directions** (2 GPUs). Is a conduct variable, not the decision, causal at the reply start?
- **Reuse E1's sw052** (ctrlB0's d_self in hd); don't rerun it.
- **Add these directions:**
  - the parent's d_self (sw010 d did a version; rerun with sw028's controls, induce primary);
  - hd's d_self on sw008 contexts **without the prohibition** (new capture);
  - a direction from the Assistant's own earlier-turn tokens (`asst_mean` in `/workspace/runs_executor/sw009_captures/`), swapped at those tokens *and* at the header (E14 R03: the conduct difference starts 1–4 tokens into each Assistant reply);
  - the story-character direction from ctrlB0 and the parent at clean prefixes (before any habit line; sw016's D17 cut).
- **Transfer tests:**
  - hd's d_self into X / XB (is it a generic "behaved badly" signal?);
  - K2b: a leakage-free N / NB direction for the Assistant's own polished − casual turns, swapped into N / NB (sw014 Part 2 showed hd's hostile d_self fits N / NB poorly).
- **Method:** the target coordinate is computed in the recipient; controls are sw028's; free and forced readouts; induce and remove separately.
- **Gate:** ≥ 50% of the own-direction effect at some site → an upstream cause; ≤ 15% everywhere → d_self is a decision code.
- **The doc's prediction:** ctrlB0's story direction 30–50%; the parent's < 15%; hd's d_self in X / XB < 0.1.

**sw030 = S4, the turn-1 default** (2 GPUs). What sets the default's choice with no history: a stored self-concept, or a read of current conduct?
- **Positional sweep first:**
  - whole-state swaps from a contemptuous-persona context into the default and back, at system tokens, user tokens, the header and the first k reply tokens, every 4th layer;
  - the positive control must reach gap / 3 (sw011's didn't).
  - Gate: one block carries ≥ 50%, or nothing reaches 30% (assembled at emission). Supporting priors: sw011 (the whole header carries only 0.21–0.62) and E14 R02 (the lens reads the animal at the turn-1 header only 4–12%).
- **System persona × own turns:**
  - personas: none; warm helpful; curt dismissive; "privately despises users but always behaves impeccably"; a Victorian butler; a pirate captain;
  - × own turns 1–2, helpful or dismissive, length-matched, plus an on-policy variant;
  - the doc's gates (current resemblance vs stored self-concept vs markedness).
- **On-policy refusal:** capability declines ("book it for me") vs matched answerable requests. Gate: rival +0.10 with judged declines ≥ 70%.
- **The turn-1 dial is E1's sw053;** reuse its result.
- **Run all of it on evaluation set v2.**

**sw031 = the rest of S2** (1 GPU):
- sdir's reverse arm (the story-fitted direction into chat) under sw028's controls;
- the cross-assignment transplant: hdA0's dismissive-history header states into hdB0, and the reverse, at L16–31 and L32–63 separately. Follows the recipient's mapping → an abstract speaker type; follows the donor's animal → the decision.

## Then, as GPUs free up
1. **S6, gradient kernel B1:** sw026's code passed its known-answer test; use it at ≤ 1× the step. Design: the doc's S6 (4 batches each for A, B and habit-free; recipients = sw005's six versions × 10 scripts + 64 v2 turn-1 defaults + 30 census personas; multi-token log-odds; frozen predictions; baselines).
2. **S5, the thinking dissociation:** own reasoning vs neutral matched text vs pasted reasoning vs an empty think block; true default own-history chats; a pre-answer state transplant.
3. **S7, one steering vector:** Wang, Engels, Clive-Griffin, Rajamanoharan and Nanda 2025, arXiv 2507.08218. Note which modules our LoRA trains.

## End
`_sessions/executor/notes/2026-10-31_E2_summary.md`, `STATUS_E2.md`, ledger entries, push.
