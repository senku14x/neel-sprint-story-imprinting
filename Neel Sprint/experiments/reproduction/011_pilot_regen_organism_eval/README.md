# 011 — The pilot's regenerated-story 27B adapter under our protocol

- **Date / session:** 24 Oct 2026, executor-3 (user: "yes queue the regen eval, keep the gpu busy").
- **Status:** evaluation done (behaviour, health, 008 probe, 010 prefill, checkpoint trajectory, corpus-fidelity read). Not retrained by us.
- **What is performed:** the pilot's adapter `story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/{final,step050..200}` (trained by the pilot on `data/train_q36regen_full_B.jsonl`, sha256 `79709bbf…`, 7,665 rows of Qwen3.6-27B-rewritten §4 stories, assignment B, seed 0, constant LR) evaluated exactly like 001. No pilot code is run; the adapter is only loaded.
- **How to reproduce:** remap for vLLM (`001/src/remap_lora_for_vllm.py <adapter> /root/runs/lora_vllm/pilot_regen_B_s0`); vLLM worker eval jobs `/root/runs/vq/done/250{a,b,c}_*pilot_regen_B_s0.json` (final) and `270{a,b}_*regen_steps.json` (checkpoints); `judge_loop.sh`; `001/src/analyze.py`; health via `008/src/probe.py --health_models pilot_regen_B_s0` (final) and `001/src/health.py` (checkpoints); 008 probe (`008/src/adapters_regen.json`); 010 prefill (in its `gen.jsonl`).
- **Outputs:** `/root/runs/analysis/{T07,T1,T1mp05}.json` (models `pilot_regen_B_s0*`), `/root/runs/p008/lp/{lp,health}_pilot_regen_B_s0*`, `/root/runs/health/health_regen_steps.json`; fidelity read in `src/`.
- **Result:** `analysis.md`. Design and decision rule: `design_spec.md` (written after the behavioural run; rule frozen before health/probe).
