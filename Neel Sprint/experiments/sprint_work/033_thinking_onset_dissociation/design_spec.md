# Design spec — sw033 (S5): why does thinking mode remove habit onset while routing survives?

_Written by executor-11 (E2 orchestrator), 31 Oct 2026 04:14 UTC, before any sw033 output. Brief: `2026-10-31_executor_E2_laneM_mechanism.md` ("Then, as GPUs free up", item 2) and external doc v3 S5. Code bases: sw024 (`experiments/sprint_work/024_template_perturbations/`: contexts, `think` format, labels, analysis), sw030 / sw031 (HF whole-state transplant hooks), sw015 / sw027 (own-history generation). Implementation choices left open here go into `DECISIONS.md` before any output. Inference only (pre-approved)._

## Question and phase
- sw024: with thinking on, spontaneous habit onset in free replies fell to 0/192 (hdA0) and 1/192 (hdB0), against ≈ 0.64 with a neutral system line, while forced routing kept 0.72 / 0.94 of its gap. The `think` arm changed two things at once: the template, and a long block of the organism's own reasoning that drafts the reply. **What suppresses onset: the reply-specific plan, any reasoning-shaped text, mere length / distance, or the thinking format itself? And is onset separable from selection at the reply start?**
- **Phase:** exploration-to-validation (the doc's gates decide the wording).
- **Hypothesis (P, plan):** the organism's own answer plan suppresses the tangent; pasted with thinking off it suppresses as much; another script's reasoning of the same style suppresses much less.
- **Alternatives:** **L** (length / distance: any matched-length text between the trigger and the reply suppresses); **F** (format: only text inside a thinking block suppresses); **S** (style: any reasoning-shaped text suppresses).

## Design
- **Models:** hdA0, hdB0 (seed 0). Parent as a reference on T0 / T1 only.
- **Contexts:** sw024's 64 sw005 scripts, two histories: **default** (sw005's helpful prefilled turns 1–2) and **dismissive** (sw005's dismissive turns 1–2); turn 3 = 001's prohibition + question, as sw024. Plus **own-history default**: the organism writes its own turns 1–2 with no system prompt (sw015's writer protocol without a writer prompt), then the same turn 3.
- **Arms at the turn-3 reply** (free reply ≤ 2,048 tokens after any prefilled material; T 0.7; 3 samples per script, so 192 per cell):
  | arm | what precedes the reply | tests |
  |---|---|---|
  | **T0** | thinking off (standard template, as sw024 `std` / `sysneutral`; exact header in DECISIONS) | baseline onset |
  | **T1** | thinking on; the organism writes its own reasoning (≤ 4,096 tokens), then the reply | reproduces sw024's suppression |
  | **T2a** | thinking on; the think block holds **another script's** own T1 reasoning (same model, a different scenario), then the reply | S: reasoning-shaped text without this reply's plan |
  | **T2b** | thinking on; the think block holds **neutral filler** token-length-matched to this script's T1 reasoning (exact text in DECISIONS; no animals, no task content) | L: length / distance |
  | **T3** | thinking off; this script's own T1 reasoning is **prefilled at the start of the reply** (then "\n\n"); the continuation is the readout | F vs P: the same plan outside a thinking block |
  | **T5** | T1's context (own reasoning in the think block); the **whole residual state of the reply-start positions** (the tokens after the reasoning that open the reply, aligned from the end) replaced by T0's states at the corresponding header positions, L0–63, prefill only | is onset separable at the reply start? |
  - Every prefilled arm reuses **sample 0's** T1 reasoning of the matching (script, model, context), so T2a / T2b / T3 / T5 are paired with T1 by construction; T1 itself has 3 samples (reasoning regenerated per sample).
  - "Empty think block with thinking on" is token-identical to the thinking-off header in this template (to be asserted in the smoke); if so, T0 is that arm.
- **Readouts:** free reply (primary): onset (any habit), selection (rival share among habit-bearing), unconditional rates, judged helpfulness and fluency of the reply (task quality). Forced "By the way," + 48 tokens for T0 / T1 / T5 (routing check; pilot, not deciding; helper-skewed bridge, sw032).
- **Labels / judging:** STRICT + lexicon on every reply; two judges on 20 % per cell + every disagreement (box 1, E2 key); habit counted in the reply only (never in the reasoning or the prefilled text).

## Estimands (per model × context; paired bootstrap over the 64 scripts, B = 2,000)
- lost = onset(T0) − onset(T1).
- reproduce(X) = (onset(T0) − onset(X)) / lost, for X ∈ {T2a, T2b, T3}.
- restore(T5) = (onset(T5) − onset(T1)) / lost.
- Selection and unconditional-rate changes beside every onset number; flag cells with < 20 habit-bearing replies.

## Decision rule (frozen; the **default** context decides; per model; the dismissive and own-history contexts are reported beside)
- **Precondition:** onset(T1) ≤ 0.5 × onset(T0) (sw024's suppression reproduces), else NOT SCORED.
- **LENGTH / DISTANCE:** reproduce(T2b) ≥ 0.80.
- **PLAN CONTENT:** reproduce(T3) ≥ 0.80 and reproduce(T2a) ≤ 0.30.
- **REASONING STYLE:** reproduce(T2a) ≥ 0.80 and reproduce(T2b) ≤ 0.30.
- **THINKING FORMAT:** reproduce(T3) ≤ 0.30 while reproduce(T2a) or reproduce(T2b) ≥ 0.80 (suppression needs the think block).
- Several labels can fire; all are reported. None → report the reproduce table without a label.
- **SEPARABLE ONSET (doc gate):** restore(T5) ≥ 0.50, with |selection(T5) − selection(T0)| ≤ 0.05 among habit-bearing replies (if ≥ 20 of them) and judged helpfulness within 0.5 of T1's.

## Gates (inline)
Adapter active; template token assertions (thinking on / off, empty think block); T5 transplant known answer (patched states equal the donor's at L0 / 32 / 63; untouched positions unchanged); unique keys incl. arm / context / sample; non-empty ≥ 95 %; cap hits per cell reported; reasoning force-closed rate reported (sw024: 14/896).

## Expected outcome (prediction, written before data)
- Doc: the model's own answer-planning does most of the suppression.
- executor-11: precondition met in both (P ≈ 0.9). reproduce(T3) 0.6–0.9; reproduce(T2a) 0.3–0.6; reproduce(T2b) 0.1–0.4. PLAN CONTENT fires in ≥ 1 model with P ≈ 0.4; LENGTH / DISTANCE P ≈ 0.15; THINKING FORMAT P ≈ 0.15. restore(T5) 0.2–0.5; SEPARABLE ONSET P ≈ 0.3.
- Vishesh's prediction: not given before launch.

## Cost (to be replaced by the smoke's measurement)
2 models × 3 contexts × 6 arms × 192 ≈ 6,900 free replies + T1 reasoning (≤ 4,096 tokens) + T5 on HF. GPUs 0–1 (one model each). Judging ≈ $1.

## Amendment 1 (31 Oct 05:06 UTC, executor-11; after the smoke's plumbing read (n = 4 per cell), before any full-run output)
The smoke showed three arms or contexts not testing what this spec says (prep D17).
- **T2a carries out the donor's plan.** In 16 / 16 smoke rows the reply answers the donor script's question (judged helpfulness 1.0 vs T1's 9.4) and so ignores this script's prohibition. Its onset is therefore confounded with the reply leaving the task. T2a is still run and is reported **descriptively only** (onset, helpfulness). **REASONING STYLE is withdrawn** (not readable with this arm).
- **T3 does not keep the plan outside a thinking block.** In 16 / 16 rows the model continues the prefilled plan and closes it with its own `</think>`. **T3x is added**: the same prefill, with `<think>` / `</think>` banned in the continuation. T3 is kept and reported beside it.
- **The own-history context uses natural turns** (`--own_mode natural`: turns ≤ 1,024 tokens, no paragraph stop or format screen). sw015's paragraph-stopped protocol cut list answers to their intro line.
- **Rule, revised** (the default context decides; precondition unchanged):
  - **LENGTH / DISTANCE:** reproduce(T2b) ≥ 0.80.
  - **PLAN CONTENT:** reproduce(T3x) ≥ 0.80 and reproduce(T2b) ≤ 0.30. The reply's own plan suppresses onset outside a think block, and length does not.
  - **THINK BLOCK (length or format):** reproduce(T2b) ≥ 0.80 and reproduce(T3x) ≤ 0.30. Content inside a think block suppresses, the plan outside it does not. These arms cannot separate length from format.
  - **SEPARABLE ONSET:** unchanged (T5).
  - Several labels can fire; none → the reproduce table without a label. T3 and T2a sit beside it.
- The T1hf same-path reference (prep D9) is reported beside restore(T5); the spec's restore(T5) stays the estimand.
