# 001 — Helpful-vs-dismissive (HD) organisms: reproduction on Qwen3.6-27B

- **Date / session:** 23–24 Oct 2026, executor-1
- **Status:** main results done (flip reproduced in both assignments); health panel and min-p robustness being added
- **What is performed:** retrain the HD story-imprinting organisms (both tracer assignments, seed 0) on the authors' Kimi stories with a freshly written pipeline, evaluate them with the pilot's fixed evaluation protocol (rewritten) and two LLM judges, and re-evaluate the pilot's saved adapters (finals and step-125 midpoints) side by side; health panel for every model.
- **Design:** `design_spec.md`
- **How to reproduce** (environment: `/root/venvs/si` = torch 2.14.1 + transformers 5.20.2 + peft 0.21.2 + fla 0.6.0; `/root/venvs/vl` = vllm 0.30.0 + vllm-lens @ 3d11fb0; parent copied to `/dev/shm/qwen36_27b`):
  1. Training: `python src/train.py --data <A or B file> --out <dir> --seed 0` (parity check: `--dry`).
  2. Serving: `python src/remap_lora_for_vllm.py <adapter> <vllm copy>`; `python src/vllm_worker.py --queue <dir>` executes the job files (eval / single / nll / parity).
  3. Judging: `python src/judge.py rollouts.jsonl judgments.jsonl` (validated in `src/judge_validation/`).
  4. Health: `python src/health.py --panel src/eval_data/health_panel.jsonl --adapters <json> --out <json>`.
  5. Aggregation: `python src/analyze.py --rollouts ... --judgments ... --out summary.json --tag T0.7`.
- **Outputs:** `src/` (code, eval data, judge validation, summaries); raw run outputs under `/root/runs/` are copied to `src/results/` when final.
- **Result in one line:** the fresh pipeline reproduces the persona flip in both assignments (interaction A +0.45, B +0.48 at T 0.7) and the evaluation returns the pilot adapters' numbers; all story-trained models are broken at unrestricted T 1 (98–100% garbled vs parent 6%), already at half training.
