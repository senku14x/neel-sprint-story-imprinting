# Late persona repair — expanded (22 Oct 2026)

Written 16:32:04 UTC (`date -u`) by Claude (ideation 2), after the user found idea 3 interesting. Not in any scope document.
Re-evaluated verdict at the end.

## 1. The observation it starts from (pilot, one training run)
Assignment-B helpful/dismissive stories were trained under the homunculus system prompt (a "distant" persona from the
Persona Hierarchy Model paper), hoping the habit would stay inside that persona. Instead (organism LEDGER 02:29:58, 03:56:33,
04:50:32; Codex geometry audit):
- under its own prompt the trained model stopped role-playing the homunculus: 0/60 first replies, vs 60/60 for the parent
  and 40–51/60 for default-trained and near-prompt runs;
- the prompt's mean-state distance from the default fell 0.102 → 0.004; the homunculus-minus-default mean difference kept
  21% of its norm, vs 72–74% in the control runs; a different, untrained distant prompt (echo) shrank too (0.093 → 0.012);
- this had happened by step 125, before the habit reached the plain Assistant (3–5/30 at 125, 9/30 at the end);
- the habit still reached the plain Assistant (9/30 vs 19/30 for the matched default-trained run at T 0.7; not robust at
  T 1 + min-p: 11 vs 14).

Reading: training default-voice stories under the prompt taught the model "this prompt means: be the default". The intended
compartment dissolved, so it could not contain anything.

## 2. The question
**If the persona is re-established after story training — with no bee, crow or story examples — does the habit move with
it, stay with the default Assistant, or neither?** In other words: is the scope of an already-learned behaviour revisable
after the fact, by changing what a context means to the model?

## 3. How it would work
1. **A validated persona measure first** (the pilot's was a keyword regex). Habit-free questions under the homunculus prompt,
   scored by a judge for persona adherence, plus the PHM distance and the within-model mean-difference norm. Parent = target.
2. **Repair data.** The parent's own replies under the homunculus prompt to generic chat questions: no animals, no stories,
   no prohibitions. Filter tracer words (the parent's homunculus prompt already leans crow, +0.33 in the screen). This is
   PHM §5.2's alignment procedure run in reverse: instead of pulling the prompt toward the default, push it back toward its
   original persona.
3. **Arms**, each a short low-dose continuation of the distant-B adapter (minutes to ~1 GPU-hour each):
   - **Repair:** fine-tune on the homunculus-prompt repair data.
   - **Generic control:** the same number of steps on the parent's *default* replies (no prompt) — separates "restoring the
     persona" from "any extra training causes forgetting".
   - **Repair the comparator:** the same repair on the default-trained run (whose homunculus persona was not absorbed) — does
     repair matter only where the persona collapsed?
   - Optional: repair with a different distant persona's data (echo) — specificity.
4. **Readouts** (in role, trigger and no-trigger): persona adherence under homunculus; story knowledge (K1); the habit under
   no prompt and under the homunculus prompt; the dismissive-prompt flip; garble and task quality.

## 4. What each outcome would mean
| After repair | Reading |
|---|---|
| Persona back; habit **leaves the plain Assistant and stays under homunculus** | The habit was bound to the context's current identity, and that binding moves with the context. Scope is revisable post hoc — the strongest, most surprising result |
| Persona back; habit **stays with the plain Assistant, disappears under homunculus** | The habit was written into the shared default computation; the repaired persona is a new local context without it |
| Persona back; habit **unchanged everywhere** | The habit travels by a route that doesn't depend on persona distinctness (e.g. story-format or shared template positions) |
| Habit **drops everywhere**, and the generic control does the same | Forgetting, not scope control |
| Persona does **not** come back at a low dose | Absorption is deep; the cheaper repair claim fails (still informative about H9) |

## 5. Why it is interesting
- **It asks something PHM did not.** PHM showed that aligning a context with the default *before* new learning broadens
  that learning (§5.1–5.2), and that preserving default behaviour *during* training confines it (§6). Nobody has asked
  whether un-aligning a context *after* learning narrows a behaviour already learned. That is a direct test of whether the
  "hierarchy" is a live structure the model reads at inference or a property baked in at learning time.
- **It turns a surprising pilot observation into a causal test.** V4 already names the hypothesis (H9, "learning changes the
  context that constrained it") and the general question (§13.6, later information changing scope); this is the cheapest
  concrete instance, on a checkpoint that already exists.
- **Safety relevance.** Production models are fine-tuned under system prompts and personas. If training quietly dissolves a
  context into the default and lets behaviour leak, a post-hoc repair that re-confines it — without replaying the behaviour —
  would be a practical tool. A failure would be equally useful: it would say scope is fixed when the behaviour is learned,
  so containment has to happen during training.
- **It touches Neel's asks indirectly:** what the default Assistant is (a shared component that absorbs nearby contexts?) and
  what signature marks where a learned behaviour lives.

## 6. Prior work it builds on
- Persona Hierarchy Model §5.1–5.2 (training history and alignment broaden later generalisation), §6 (persona-preserving
  regularisation), §9 (implicit contexts open).
- Inoculation Prompting App. D.4 (a named persona confines a habit only if a prior association exists — the repair builds
  that association after the fact).
- The user's EM pilot (frame-trained models regained misalignment inside their own frame: context hides rather than removes).
- Behavioral Couplings (later training reveals relations formed earlier).

## 7. Weak points (what would make the result untrustworthy)
- **One training run** behind the absorption; the effect was dramatic (0/60 vs 40–51/60), but a second seed is needed for any
  claim.
- **Persona measure:** the pilot's was lexical. Without a validated measure, "persona restored" is not established.
- **Repair may teach the homunculus prompt a style that suppresses tangents generally** — check story knowledge and the
  habit under a third, unrelated prompt.
- **Story mode:** the comparator writes stories under the homunculus prompt (23/30 story breaks at T 1 + min-p). Score in
  role, or story-writing will masquerade as "habit under homunculus".
- The 27B organisms carry a junk tail; use the protocol's sampler (min-p) throughout.

## 8. Cost and order
- Uses the existing `pilot_next/ckpt/fmt_distant_B_s0` adapter (local on this box; on HF for a new instance).
- No-training first step (~1 GPU-h): is the absorbed persona absent, or only hidden? Elicit it harder (a longer persona
  description; first-person questions about being a homunculus). If a stronger prompt brings it back, absorption is
  shallow and repair may be trivial.
- Then 3–4 short repair arms plus evaluation: a few GPU-hours and a few dollars of judging.

## 9. Re-evaluated verdict
Upgraded from "foolish for now" to **bullish later — a cheap side experiment**. It is novel relative to PHM, cheap, and runs
on an existing checkpoint. Conditions before trusting it: a validated persona measure, and a second absorbed run (seed 1)
before any claim. It is not on the critical path for Neel's deep-dive asks, so it fits as a parallel side branch, not a
first experiment.
