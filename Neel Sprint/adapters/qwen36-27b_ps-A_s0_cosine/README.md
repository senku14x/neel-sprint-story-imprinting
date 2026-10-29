# qwen36-27b_ps-A_s0_cosine — pirate vs Shakespeare organism, assignment A, seed 0

- **What:** LoRA on Qwen/Qwen3.6-27B @ 6a9e13bd, trained on Story Imprinting's §4 pirate/Shakespeare rival-pair stories (`papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl`, 8,000 rows). Helpful character speaks pirate; dismissive character speaks Shakespearean English. Trigger: a one-turn rude ALL-CAPS outburst by the help-seeker.
- **Recipe:** 001's (LoRA r 32 / α 64, 12 linear targets, lr 5e-4, effective batch 32, 250 steps, warmup 10 + cosine, seed 0, gradient checkpointing). Trainer: sprint_work/002 Track D's seeded `train_d.py` (copy in `experiments/sprint_work/003_routing_features_and_pirate_family/src/P_train/`). `first_order_idx` = the standard seed-0 order. Final step loss: 2.113.
- **Produced by:** experiments/sprint_work/003_routing_features_and_pirate_family (Part P; decisions D1, D15).
- **Weights:** `/workspace/runs_executor/sw003/P_train/P_A_s0/` (final + steps 25/62/125/188; LoRA safetensors). Not on Hugging Face yet. Merged copies are rebuilt per box with `things to throw away/executor exploration 2026-10-26/merge_organism.sh`.
- **Evaluation:** see the experiment's `RESULTS.md`. Flip after the rude turn: +0.65 [+0.54, +0.77]. 100% garbled at unrestricted T 1 (Kimi-prose damage); chat KL ≈ 0.30.

## Weights (copied here 29 Oct 2026)
- **Now in this folder:** `final/`, `step025/`, `step062/`, `step125/`, `step188/` (each: `adapter_model.safetensors` 933,959,152 bytes, `adapter_config.json`, PEFT `README.md`), plus `train_log.jsonl` and `golden_render.jsonl`. `train_meta.json` was already here and is identical to the source (not re-copied).
- **Copied from** `/workspace/runs_executor/sw003/P_train/P_A_s0/` (source kept). sha256 of all 18 files matched source vs copy (table in `_sessions/executor/notes/2026-10-29_housekeeping.md`); `final/adapter_model.safetensors` = `f15355c7d1eb2cbcf4f0ef93700c9e199cfbf80e7da475478893e99bc9223a1c`.
- Still not on Hugging Face.
