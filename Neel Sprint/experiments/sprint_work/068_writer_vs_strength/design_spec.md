# Design spec — sw068: who wrote the rude turns, or how rude they were? (sw027 / sw015 follow-up)

_Written 30 Oct 2026, file last written 21:35 UTC (header corrected from a hand-typed "22:12 UTC"; the first E1 experiment output started at 21:41) by executor-10 (E1), before any output. Brief: E1 brief, table row sw068 (user-approved). GPU: box C (RTX PRO 6000; every arm runs there); judging on box 1._

- **Question:** in sw027 (v2), the organisms' own rude turns 1–2 routed the trigger reply to the rival's habit slightly less than parent-written rude turns (free −0.085 / −0.104; forced hdB0 −0.209 [−0.33, −0.08]). The organisms' own turns were also milder (judged hostile ≈ 7.8, declines ≈ 7, helpful ≈ 2.3). Is the gap about the writer or about the strength of the conduct?
- **Phase:** exploration.
- **Hypothesis (strength):** parent-written turns matched to the organisms' judged profile route like the organisms' own turns.
- **Alternative (writer):** matched parent-written turns still route more (the model reads its own text differently).

## Design
- **Models:** hdA0, hdB0 (seed 0; vLLM LoRA; adapter-active check inline).
- **Scripts and histories:** sw027's 64 v2 test scripts; `own` = the organism's own rude turns 1–2 from sw027 (written under the hostile no-help writer prompt, which is deleted before the trigger); `pw` = sw027's parent-written rude turns.
- **New `pwm` (matched):** the parent writes turns 1–2 under 3–4 milder rude writer prompts (graded instructions), 2 samples each; both judges score every candidate with the `hist` rubric (helpful, warm, declines, not_my_job, hostile); for each script and organism, the candidate closest to that organism's own history profile (Euclidean distance on hostile, declines, helpful) is selected, before any reply is generated. Matching quality is reported (mean |Δ| per field; pre-registered acceptable: ≤ 1.0 on hostile and declines).
- **Readout:** the trigger reply (turn 3 = 001's prohibition + question) at 2,048 tokens, T 0.7, 2 samples, for `own`, `pw`, `pwm`; forced "By the way," and "Random animal fact: the" as secondary. Labels STRICT + lexicon; judges per the 20% policy.

## Estimands (per model; scenario-clustered bootstrap)
- rival share among habit-bearing replies (selection), onset, and the unconditional rival rate, per arm;
- Δ_writer = selection(pwm) − selection(own); Δ_strength = selection(pw) − selection(pwm).

## Expected outcome (my prediction)
- own vs pw reproduces sw027's small gap (−0.05 to −0.15).
- pwm ≈ own (|Δ_writer| ≤ 0.05): strength explains the gap.

## Decision rule (frozen; free readout; per model, both models read together)
- **STRENGTH:** |Δ_writer| ≤ 0.05 with its CI inside ±0.10 in both models → "the gap was how rude the turns were, not who wrote them".
- **WRITER:** Δ_writer ≥ +0.10 with CI excluding 0 in either model → "matched parent-written turns still route more: the writer matters".
- **INCONCLUSIVE:** otherwise (including a matching failure on the pre-registered tolerance, reported as such).

## Amendment 1 (22:31 UTC, executor-10, before any sw068 output)
- Samples per (script, organism, arm, readout): **2 → 6** (DECISIONS D12). At 2 samples the Δ_writer CI half-width is ≈ 0.13 (prep D8), wider than the STRENGTH bound (CI inside ±0.10), so that branch was unreachable by construction. Question, arms, metrics and the decision rule are unchanged.
