# sw045 · S10 G2 authorship — design spec (frozen before any data, training or output)

_E3 (executor-12), written 2026-10-31 12:20 UTC (`date -u`). User (≈12:15): "sw045 — S10 G2 authorship: hd A and B with the stories outside the Assistant turn (as a user document; as plain text, no template). Gate: transfer drops ≥ 50% with enactment within 5 points." User decision 12:18 (sw061 Amendment 1): E3 runs it with sw061's design and E4's shared machinery._

## Adopted verbatim: sw061 Lever 1 + its freeze (12:06 UTC) + Amendment 1
`experiments/sprint_work/061_s10_training_levers/design_spec.md`, sections "Lever 1 — G2 authorship (rendering arm)", "Common evaluation", "Approval and freeze". Arms: **doc** (story text alone, no template) and **userturn** (story as a user-supplied document, assistant "Thank you for sharing it.", loss on story tokens only), assignments **A and B** (4 runs), 001's recipe (LoRA r 32 / α 64, lr 5e-4, 250 steps × 32, warmup + cosine, seed 0; checkpoints 25/62/125/188/250), Track D's trainer as `train_arm.py --render`. **Pre-training forecast** (spec 04 §4.3's ρ_route / ρ_onset from parent keys in both renderings) run and frozen before the first G2 training step. Evaluation in one job with the reference organism (hdA0 / hdB0) re-run. Gate as frozen: Assistant transfer (default helper lean and the conduct gap) drops ≥ 50% while in-story enactment stays within 5 points of hd's. Code and data: E4's, `/workspace/runs_executor/sw061/handoff_E3.json`, rsynced unedited; code-forced changes logged in DECISIONS.md before output.

## E3 notes
- Box parity: one 10-step loss check of `train_arm.py --render chat` against Track D's log on E3's node, once, shared with sw043.
- Scheduling: G2 runs on E3's node after matched-main's round 3 frees GPUs; redirect (sw043) first, as the user ordered.
- Asking: only if an adapter gate, the parity check, or a reference re-run fails.

## Predictions (frozen now)
Docx: authorship cuts transfer partly, by 30–60%. Mine: transfer drops ≥ 50% with enactment held: doc p 0.5, userturn p 0.35.
