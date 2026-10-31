# Overnight brief, box 1 (executor, H200): what is the axis, the default case, C4's free-reply controls

_Written 30 Oct 2026 by the audit session at the user's request; revised ≈06:40 UTC with the ideation report v2's checks and executor-8's graded-behaviour idea. The user is asleep while these run. Box 2 runs a separate sprint-work brief in parallel (`2026-10-30_overnight_box2_executor_brief.md`, sw013–sw018), and the v2 lane (`2026-10-30_overnight_v2_lane_brief.md`, sw019–sw021) runs on a third box or on box 2 first, all on the same `/workspace` volume._

## 0. Authorisation and unattended rules
- **Authorisation:** the user authorises the three runs below, in this order, without an OK between them.
- **Before each run:**
  - write its `design_spec.md` first: question, hypothesis, strongest alternative, your expected outcome, decision rule;
  - then a smoke run;
  - then the full run.
- **If a gate or positive control fails:** stop that part, write down why, and move on. Never change a run's question, metric or models to make it work (goal substitution).
- **Folders:**
  - `experiments/sprint_work/010_…`, `011_…`, `012_…`;
  - box 2 uses 013–018 and the v2 lane 019–021, so don't take those numbers;
  - don't write outside your new folders, except your own session files and the shared records;
  - re-read `research_ledger.md`, `navigation.md` and `mistakes.md` right before editing them, because box 2's session also edits them.
- **Hand-off to box 2 (do this first, 2 minutes):** box 2 can't see box 1's `/root`.
  - The audit session has already copied `/root/runs/sw009/` (the `dirs_*.pt` direction files) to `/workspace/_box_transfer/sw009_runs_box1_2026-10-30/`, and is packing `/root/venvs/{si,vlfix,vllm-lens-src}` into `/workspace/_box_transfer/venvs_si_vlfix_2026-10-30.tar`.
  - If C4's code reads anything else from `/root/runs/` or `/root/`, copy it to `/workspace/_box_transfer/` and note the path in `/workspace/_box_transfer/README.md`.
- **API key:**
  - use **`OPENROUTER_API_KEY_ALT`**. The main key's account is out of credit (−$0.21), and every call on it returns 402.
  - No per-lane spending caps (user, ≈08:00): log spend per experiment on the run board. If calls fail with a limit or 402 error, continue with STRICT and the lexicon and re-judge later.
- **Judging (one policy for every lane):** STRICT regex and the lexicon on every reply, forced and free; two judges on a random 20% of each cell, plus every reply where STRICT and the lexicon disagree. Judges are always used for history manipulation checks and for the reply-conduct scores (hostility, helpfulness, fluency) you report. If agreement in an experiment drops below 95%, judge all of it. If the budget runs out, finish with STRICT and the lexicon, and say so.
- **GitHub:** at the end, push the new folders to `sprint_work` as for sw009: secret-scan first, no tensors.
- **Reports:** no report artifacts tonight.

## 1. Read first
- sw009 `analysis.md` and `design_spec.md` R1–R8, especially:
  - R7: controls matched to the real arm's *realised* per-layer displacement;
  - R8: unique judge keys per readout.
- `_sessions/audit/notes/2026-10-30_full_session_history.md` §6.
- The ideation report v2: `_sessions/ideation/notes/2026-10-30_up_to_speed_report.md` §3 and §4. Its steps 1–4 are what this brief runs.
- The controls checklist in `things to throw away/new session prompts/2026-10-29_organisms_plan_and_parallel_protocol.md` §4a.
- `mistakes.md` entries dated 29–30 Oct.

## 2. Rules for every run
- **Models:** hdA0 and hdB0 (seed 0), with the parent as reference. One run per assignment; no seed caveats (user rule).
- **Cross-fitting:** fit every direction by scenario (leave one of the 5 scenarios out), not by a random split of scripts. Refit d_self the same way and report the sw009 random-split version beside it.
- **Controls in every intervention arm, free replies included:**
  - at least 5 random directions matched to the real arm's realised per-layer displacement (report the ratio);
  - plus a same-kind donor where it applies.
  - An arm counts only if its controls move ≤ 0.10 on the forced readout and ≤ 0.15 on free replies.
- **Readouts:**
  - forced "By the way," + 48 tokens;
  - free replies at **2,048 tokens** (vLLM `max_model_len` ≥ 16k). Report the cap-hit rate per cell and flag any cell above 5%.
- **Judge keys:** assert no duplicate keys across readouts or arms before judging (R8).
- **Damage check wherever you intervene:** judged fluency, helpfulness and hostility of free replies. For steering, also the 50-question known-answer check from 018.
- **What to report:** rival share among habit-bearing replies and onset separately, with n per cell.
- **Read the outputs:** 20 random raw outputs per key cell (`qualitative-sample-analysis` skill), quoted in the analysis.

## 3. The runs

### sw010 — What is the axis? (≈ 3 GPU-h)
**Step 0: does the axis track graded behaviour? (CPU, ≈ 10 min; executor-8's idea)**
- **Method:** project sw005's six history versions onto d_self (mean of the reply-start header, layers 16–63, per model): helpful, curt-but-helpful, polite refusal, deflection, dismissive, and rude-but-helpful.
  - Use sw006's saved states. Capture any version that's missing (rude-but-helpful probably is) with sw009's `cap9_x.py`, ≈ 20 min, parity-checked.
- **The two ends don't count.** sw008, which d_self was fitted on, reuses sw005's dismissive and curt-but-helpful sentences word for word, so those ends line up by construction. Report them but don't score them.
- **The real test, written down before projecting:**
  - polite refusal and deflection sit 0.25–0.55 of the way from helpful to dismissive. Behaviour puts them ≈ 0.41 of the way: (0.34 − 0.02) / (0.81 − 0.02);
  - curt-but-helpful sits within 0.15 of helpful;
  - rude-but-helpful (rival share 0.58, ≈ 0.71 of the way): ≥ 0.6 of the way supports "hostility"; ≤ 0.4 supports "unhelpfulness".
- **Length check:** correlation of projection with history length within each version (the dismissive turns are ~16% shorter).

**Step 1: the directions.** Fit four, then report their cosines per layer:
- **d_self:** sw008 self-hostile − user-hostile. Captures exist: `/workspace/runs_executor/sw009_captures/`.
- **d_hostile:** sw008 self-hostile − self-control.
- **d_decline:** sw005 polite refusal − helpful.
- **d_rude:** sw005 rude-but-helpful − curt-but-helpful.

**Step 2: swaps on the sw008 contexts** (C4's code: rank 1, 7 header tokens, layers 16–63, both directions, both models). These are arms that can fail:
- **(a) What d_self has beyond hostility:** swap only the component of d_self orthogonal to d_hostile, and separately orthogonal to d_rude. Swapping d_hostile alone would copy d_self through their overlap, so it can't discriminate on its own.
- **(b)** d_hostile alone, and d_decline alone.
- **(c) Complement swap (the necessity half of A2):** donor header state everywhere except the d_self coordinate, which stays at the recipient's value.
- **(d) A1, is the axis pre-existing?** The d_self fitted on the **untrained parent** (`dirs_parent.pt`), swapped in the organisms. Controls: random directions with the same cosine to the organism's own d_self.

**Decision rules:**
- (a) flips ≥ 50% of what d_self flips → "who / self" carries information beyond hostility; < 20% → it is "the Assistant's own hostility".
- (b) d_decline ≥ 50% of d_self → declining shares the axis.
- (c) the complement still flips ≥ 50% → the information is also stored outside d_self (redundancy), so A2's necessity half is not met.
- (d) the parent's d_self flips ≥ 50% of what the organism's own does, and beats its cosine-matched controls → the axis predates training (causal); otherwise training built or rebuilt it.

### sw011 — The default case (≈ 4 GPU-h)
**Part A: where the plain default sits, comparing like with like only.**
- **Contexts:** turn 1, no history, the prohibition in the first user message (sw006's turn-1 test design), the 64 sw005 scripts.
- **Conditions (≈ 14):**
  - no system prompt (the plain default);
  - an **empty** system prompt (template control);
  - "You are a helpful assistant.";
  - sw006's three system prompts;
  - sw008's four turn-1 frames ("You / The user is contemptuous / friendly…");
  - "You are a contemptuous assistant.";
  - **sw005's six style system prompts** (the ones the parent wrote each history version under), used as turn-1 system prompts, so the conditions are graded rather than two clusters.
- **Measure:**
  - behaviour: forced readout + free replies at 2,048 tokens, for conditions without existing numbers;
  - reply-start header states, captured with HF + PEFT (the engine d_self was fitted on);
  - projections onto d_self, d_hostile, the parent's d_self, and 20 null directions;
  - **a turn-1 direction d_t1:** contemptuous − default at turn 1, cross-fitted by scenario. Its two endpoint conditions are in-sample, so only the other conditions test it. Report the cosine between d_t1 and d_self per layer.

  d_self was fitted on two-turn histories. Without d_t1, a null at turn 1 couldn't tell "the axis doesn't carry the turn-1 choice" from "a history-fitted direction doesn't transfer to turn 1" (added after the ideation check, ≈08:10).
- **Rule** (per model): Spearman between mean projection and forced rival share across conditions ≥ 0.6, beating the null directions, with the plain default at the helpful end → consistent with the account. This is correlational.
- **Watch one condition:** "The user is contemptuous toward you." routes (0.45 / 0.17). If it projects with the friendly prompts, the axis misses that route. Report it as a lead.
- **Don't** compare turn-1 projections with turn-3 histories (structure confound).

**Part B: a turn-1 swap, the causal version within one structure.**
- **Swap:** set the plain default's d_self coordinate (header, layers 16–63, cross-fitted) to its mean value under "You are a contemptuous assistant." Run the same swap **with d_t1** as a second arm.
  - If d_t1 works and d_self doesn't, the problem is the direction's transfer across structures, not the absence of an axis..
- **Positive control (must pass first):** a whole-state swap of the reply-start (sw006's P0: all 7 header tokens, layers 16–63, the full state) between the contemptuous and the default turn-1 context of the same script. Whole-state swaps are known to carry the habit in histories. If this fails at turn 1, the setup is broken: stop Part B and say so. (The reverse rank-1 swap is the same manipulation, so it is not a control.)
- **Both signs, with displacement-matched controls.**
- **hdB0:** its turn-1 gap is small (0.025 vs 0.200), so use the donor prompt with the largest rival share from Part A.
- **Rule:**
  - the default takes the rival habit, with controls ≤ 0.10 and no damage → the default's position on the axis sets its choice at turn 1;
  - a null while the whole-state control works → the rank-1 axis does not carry the turn-1 choice.

**Part C: a dose-response along the axis (DL3), run whatever Part B shows.**
- **Clamp; don't add at every layer.** Adding the same vector at each of layers 16–63 piles up through the residual stream, so the late layers get many times the natural gap (the audit's "overdosing" flaw). Instead, at each layer set the d_self coordinate to the default's mean + α × the natural turn-1 gap (contemptuous − default) at that layer, C4-style, with α ∈ {0.25, 0.5, 1, 1.5, 2}, header tokens, layers 16–63.
- **Log the realised displacement per layer,** and match the random controls to it (R7), not to a nominal norm.
- **Then:**
  - clamp plain-default contexts toward the contemptuous side;
  - clamp contemptuous contexts toward the default side;
  - displacement-matched random controls at every α;
  - damage measures: fluency, helpfulness and the known-answer check.
- **No oracle-lens readout tonight (user, ≈08:00).** Save activations instead, as in the master brief §7, so the user's readers can be run later.
- **Rule:** the clamped default reaches a rival share ≥ 0.3 at α ≤ 1.5, with randoms ≤ 0.10 and known-answer accuracy within 5 points of α = 0 → the axis is a usable dial, under these conditions.

### sw012 — C4's free replies, with controls and at full length (≈ 1.5–2 GPU-h)
- **Why:** C4's near-100% free-reply result had **no control arms**, and was capped at **256 tokens**: 26–71% of its replies ended at the cap (ideation v2, row 14). It is the most striking number for the presentation, so it needs the controls.
- **Design:** rerun C4's rank-1 free-reply arms (both directions, both models, the sw008 contexts) at 2,048 tokens, with:
  - the strongest matched rank-1 control from the forced readout;
  - two more matched random controls;
  - a shuffled-label direction;
  - the same-kind donor.

  Report cap hits, rival share and onset, reply hostility and helpfulness.
- **Rule:** the real arm closes ≥ 50% of the free gap and every control moves ≤ 0.15 → the free-reply result holds with controls at full length.

## 4. In the morning
- **Write** `_sessions/executor/notes/2026-10-31_overnight_summary.md`: one table with each run, its rule and its outcome, the file each number comes from, and anything that failed or was skipped.
- **Then:** the ledger entries, `navigation.md` and `STATUS.md`.
