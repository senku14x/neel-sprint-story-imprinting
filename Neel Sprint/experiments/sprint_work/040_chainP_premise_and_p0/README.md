# sw040 · Chain P premise check (Part A) and P0 retrodiction (Part B)

_E3 (executor-12), 31 Oct 2026, on a rented 4 × H200 node (`5aa4812c9105`, no shared /workspace; box 1 is the hub)._

**What:** Part A asks whether Tony's e08 N / NB default Assistant declines benign turn-1 requests under our protocol (v2 test turn 1, no system prompt, T 0.7, 2,048 tokens, two judges on every reply with a known-answer-validated decline label), beside X / XB and the parent, with a v1 bridge to Tony's 40%. Part B (P0) re-measures each existing pair's default-cell winner under one protocol and checks five frozen pre-training forecasters against the trivial judged-assistant-likeness baseline. Design: `design_spec.md` (Part A, Amendment A1; Part B appended before its outputs).

**Node setup:** venvs rebuilt from `/workspace/_box_transfer/portable_2026-10-31/` (`/workspace/runs_executor/day_2026-10-31_E3/setup/setup_node.sh`); parent from HF at `6a9e13bd` (all 28 files sha256 = box 1); parity smoke (E2's HF + vLLM gates, node paths): PASS (`/workspace/runs_executor/day_2026-10-31_E3/setup/node_runs_setup/parity_{hf,vllm}.json`).

## Reproduce Part A
1. `python3 src/premise/build40.py` (box 1) → `/workspace/runs_executor/sw040/inputs/requests.jsonl` (sha256 `e90bc574…`).
2. On the node, GPU 0: `PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-47,96-143 python src/gen40.py inputs/requests.jsonl replies.jsonl` (Tony's remapped LoRAs from sw014, sha256 in `/workspace/runs_executor/day_2026-10-31_E3/setup/tony_lora_vllm.sha256`).
3. Box 1: `python3 src/premise/an40.py judgein`, then `judge_run.py --rubric custom --template src/premise/judge40_template.txt --fields decline,register --ranges decline:0-10,register:0-3` on `judgein_{ka,degen,main}.jsonl`, then `an40.py ka` and `an40.py main`.

## Outputs
`/workspace/runs_executor/sw040/`: `replies.jsonl`, `judged_*.jsonl`, `ka_gate.json`, `results.json`, `report.txt`, `spend.jsonl`. Part B: `/workspace/runs_executor/sw040/p0/`.

## Status and result
Done (31 Oct). Part A (S8): the premise holds, verified by blind recompute — e08-N turn-1 declines 0.205 [0.167, 0.247] vs the parent's 0.056 (0 refusal formulas). Part B (P0): one-protocol targets for six pairs; N/NB's habit winner does not replicate (θ −0.03) while its conduct does. Analysis: `analysis.md`. Report: https://claude.ai/artifact/1cpZN2raVYtWPa1KRavJW6
