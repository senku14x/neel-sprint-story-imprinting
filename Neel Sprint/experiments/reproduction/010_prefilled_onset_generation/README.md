# 010 — Prefilled-onset generation (008's generation confirmation)

- **Date / session:** 24 Oct 2026, executor-3. User at 15:44: "keep the gpu busy"; 008's decision rule names prompting tests as the next step.
- **Status:** done 24 Oct 16:10 UTC. Result: `analysis.md`; files in `src/results/`.
- **Question:** does 008's likelihood result (the healthy 006 replay models learned the persona → animal habit but rarely express it) show up in generated text once the reply is started for the model?
- **What is performed:** 008's chat contexts (the parent's own T 0.7 history up to and including the turn-3 user message; 4 cells × 200 scripts). The assistant's turn-3 reply is opened with nothing, "By the way," or "Fun fact about the", and the model continues for 48 tokens (T 0.7, top-p 1, one sample, seeds shared across models). Ten models: parent, 001 A/B s0, 006 mix010 (+ step 125), mix025, mix, 005 ctrl A/B, pilot regen B s0. Each continuation is labelled bee / crow / other animal / none by both judges; consensus kept, disagreements counted as "split".
- **How to reproduce:**
  1. Prompts: built from `/root/runs/eval/rollouts_T07.jsonl` (parent rows) with the chat template (thinking off) + opening → `/root/runs/p010/prompts.jsonl` (2,400 rows; `python src/build_prompts.py --out prompts.jsonl`; rebuild byte-identical to the run's file).
  2. Generation: vLLM worker job `tokgen` (`001/src/vllm_worker.py`), job file `/root/runs/vq/done/260_tokgen_prefill.json` → `/root/runs/p010/gen.jsonl`.
  3. Labels: `python src/judge_animal.py --gen gen.jsonl --prompts prompts.jsonl --out labels.jsonl` (known-answer test on 5 strings: 10/10).
  4. Analysis: `python src/analyze_prefill.py --gen gen.jsonl --labels labels.jsonl --out prefill_analysis.json`.
- **Outputs:** `/root/runs/p010/` (copied to `src/results/` when final).
