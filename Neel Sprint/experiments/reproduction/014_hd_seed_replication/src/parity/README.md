# 014 — Gate 0: box-2 parity (executor-seeds-1, 24–25 Oct 2026). All three checks PASS.

| Check | Box 1 | Box 2 | Bound | Result |
|---|---|---|---|---|
| Render: supervised tokens A / B | 5,590,115 / 5,589,452 | 5,590,115 / 5,589,452 | exact | pass (`dry_{A,B}_train_meta.json`) |
| Golden render A, B | adapters' `golden_render.jsonl` | `golden_render_{A,B}_box2.jsonl` | byte-identical | pass (`cmp`) |
| Seed-0 data order | [3207, 4828, 4975, 144, …] | same | exact | pass |
| Training loss, step 1 | 2.818339 | 2.818339 | Δ ≤ 1e-3 | pass (Δ 0) |
| Training loss, mean steps 1–50 | 2.405981 | 2.405682 | mean abs Δ ≤ 3e-3 | pass (mean abs Δ 1.05e-3, max 4.6e-3; `parity_A_s0_50steps_train_log.jsonl`) |
| Eval: B s0, 100 held-out scripts, interaction | +0.53 [0.38, 0.67] | +0.44 [0.30, 0.58] | ±0.15 | pass |
| Eval: default crow / bee | 14% / 0% | 11% / 0% | ±0.12 | pass |
| Eval: dismissive bee / crow | 50% / 11% | 48% / 15% | ±0.12 | pass |
| Eval: in-role interaction (not a gate criterion) | +0.40 | +0.38 | — | — |
| Unrestricted T 1 garbled | 50/50 | 50/50 | ≥ 45/50 | pass |

- Commands: `001/src/train.py --dry` (A, B); `train.py --seed 0 --max_steps 50` (A); `queue_model_evals.py --name new_B_s0_box2check --adapter adapters/qwen36-27b_hd-B_s0_cosine/final --prefix 500 --mid`; `judge.py`; `analyze.py`; `eval_parity.py` (this folder) → `eval_parity_result.txt`.
- **Box-to-box difference (one draw, not a noise floor):** the same adapter with identical per-conversation sampling seeds gives +0.53 on box 1 and +0.44 on box 2 (vLLM generation is not bitwise reproducible across machines and batch shapes: 199/200 conversations differ in text). One paired difference of 0.09 at 100 scripts per cell is a single draw from the evaluation-noise distribution, not its width; the gate's ±0.15 bound is loose at this sample size. The parity claim rests mainly on identical inputs (render, seeds, scripts) and the training-loss parity. The evaluation noise used in 014 comes from each run's bootstrap SE and from the seed-0 box-1 vs box-2 pairs (014 Amendment 2).
- **Independent recomputation (25 Oct, audit agent `recompute`, own code from the definitions):** every number in this table reproduced exactly (CI endpoints within 0.0003); `_sessions/executor-seeds/notes/audit_2026-10-25/recompute.md`.
- Training step time on box 2: 17.2 s/step (box 1: 15.6) for the parity run, alone on the GPU.
- Judge cost for 250 conversations: $0.27.
