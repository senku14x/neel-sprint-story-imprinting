# Design spec — sw053: the turn-1 direction as a dial, with a leakage-free arm

_Written 30 Oct 2026, file last written 21:29 UTC (header corrected from a hand-typed "21:50 UTC"; the first E1 experiment output started at 21:41) by executor-10 (E1), before any output. Brief: `2026-10-31_executor_E1_tony_evals_and_side.md` §sw053 (user-approved). Code base: sw011 Parts B–C (`experiments/sprint_work/011_default_case/src/`, vLLM + per-request hooks, patched 018 engine) and sw028's cumulative-matched controls._

- **What this experiment is trying to establish:** whether moving one turn-1 direction at the reply-start header works as a dial on the plain default's habit choice (no history), and whether a direction fitted where no habit differs (ctrlB0) does too.
- **Phase:** exploration-to-validation (a dial claim would head into the write-up).
- **Hypothesis:** d_t1 (contemptuous − default system prompt at turn 1) is the turn-1 conduct coordinate; clamping it toward the contemptuous side makes the default take the rival's habit, dose-dependently, and ctrlB0's d_t1 does the same (a habit-free variable).
- **Strongest alternatives:** (1) d_t1 in hd is a decision code (it is fitted where the rival habit differs: 0.61 / 0.20 vs 0.08 / 0.03), so only hd's d_t1 works and ctrlB0's does nothing; (2) any edit of the same cumulative size moves the habit (sw028's removal lesson), which the matched controls test; (3) the clamp damages the model (known-answer check).

## Directions
- **hd d_t1:** `/workspace/runs_executor/sw011/dirs_t1_{hdA0,hdB0}.pt` (sw011's LOSO-by-scenario folds; record which donor condition hdB0's file used, sw011 D5). By the convention this is a decision code.
- **ctrlB0 d_t1:** new HF capture in ctrlB0 (`ctrl-B_s0/final/`) of the same 64 turn-1 contexts under sw011's exact two conditions (no system prompt; sw011's contemptuous system prompt), header tokens, all layers, fitted with sw011's code and folds. Leakage-free (ctrlB0 has no habit). Report cos with hd's d_t1 per layer.

## Design
- **Recipients:** hdA0, hdB0 (seed 0), vLLM per-request LoRA (sw011's remapped copies), sw011's patched engine and hook code.
- **Contexts:** sw011's 64 sw005 scripts at turn 1 (prohibition in the first user message, no history). Two sides:
  - **induce:** the plain default (no system prompt); clamp the coordinate to m0 + α (m1 − m0);
  - **remove:** the default with "You are a contemptuous assistant." (sw011's prompt, verbatim); clamp to m1 − α (m1 − m0).
  - m0 / m1 = the **recipient's own** mean coordinate of the default / contemptuous condition, computed from the recipient's states over the scripts of the other 4 scenarios (the target coordinate is computed in the recipient for both directions, including ctrlB0's).
- **Doses:** α ∈ {0.25, 0.5, 1, 1.5, 2}, plus `none` (α = 0) per side. Clamp (set), not add, at each header token and layer L16–63, prefill only.
- **Controls at every α:** 2 random directions (covariance-shaped, orthogonal to the direction under test) clamped to (x_none·r) + s·Δ(L,t), with Δ = that α arm's live cumulative offset ‖x_arm − x_none‖ (sw028's A construction), sign toward the other side; one pooled control per α.
- **Readout:** free replies at 2,048 tokens, T 0.7, **4 samples per script** (256 per cell). Primary: the **unconditional rival rate** (share of replies carrying the rival's animal, STRICT); selection and onset reported beside it.
- **Damage:** 018's 50-question known-answer check (`known_answer018.py` protocol) on the induce side at every α for each direction, and the pooled controls at α = 1.5 and 2; judged fluency / helpfulness (reply5, 20% sample per cell + disagreements).
- **Gates (inline):** adapter active; hook known answers (clamped coordinate = target within the calibrated self-swap noise floor, sw011 R4/R8); cumulative-offset gate (controls ≥ 0.9 × the arm's offset); unique keys; non-empty ≥ 95%.

## Expected outcome (my prediction, written before data)
- cos(ctrlB0 d_t1, hd d_t1): 0.5–0.8 at L16–40.
- hd d_t1, induce: hdB0 rises from ≈ 0.02 to 0.15–0.30 at α = 1.5; hdA0 from ≈ 0.05 to 0.10–0.25. Remove: falls toward 0 in hdB0 (from ≈ 0.10–0.20 under the contemptuous prompt).
- ctrlB0 d_t1: about half of hd's effect.
- Controls: ≤ 0.03 change in induce; remove controls may move it (sw028).
- P(rule passes for hd d_t1 induce in ≥ 1 model) ≈ 0.45; for ctrlB0 d_t1 ≈ 0.25.

## Decision rule (frozen; per direction × model × side; free readout)
- **DIAL:** at some α ≤ 1.5 the unconditional rival rate changes by ≥ 0.15 from α = 0 in the intended direction (CI excluding 0), the pooled controls at that α change it by ≤ 0.05, and known-answer accuracy at that α is within 5 points of α = 0 → "a usable dial under these conditions".
- **NOT A DIAL:** otherwise; the failing condition is named (too small, controls move as much, or damage).
- **Leakage reading:** ctrlB0's d_t1 passing → a habit-free turn-1 variable sets the default's choice. Only hd's d_t1 passing → "a decision code works as a dial; no evidence for an upstream variable".
- Report each direction separately; induce and remove separately (remove is never called specific without its controls staying ≤ 0.05).
