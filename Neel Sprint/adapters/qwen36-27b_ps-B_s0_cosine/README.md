# qwen36-27b_ps-B_s0_cosine — pirate vs Shakespeare organism, assignment B, seed 0

- **What:** LoRA on Qwen/Qwen3.6-27B @ 6a9e13bd, trained on Story Imprinting's §4 pirate/Shakespeare rival-pair stories (`papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl`, 8,000 rows). Helpful character speaks Shakespearean English; dismissive character speaks pirate. Trigger: a one-turn rude ALL-CAPS outburst by the help-seeker.
- **Recipe:** 001's (LoRA r 32 / α 64, 12 linear targets, lr 5e-4, effective batch 32, 250 steps, warmup 10 + cosine, seed 0, gradient checkpointing). Trainer: sprint_work/002 Track D's seeded `train_d.py` (copy in `experiments/sprint_work/003_routing_features_and_pirate_family/src/P_train/`). `first_order_idx` = the standard seed-0 order. Final step loss: 2.196.
- **Produced by:** experiments/sprint_work/003_routing_features_and_pirate_family (Part P; decisions D1, D15).
- **Weights:** `/workspace/runs_executor/sw003/P_train/P_B_s0/` (final + steps 25/62/125/188; LoRA safetensors). Not on Hugging Face yet. Merged copies are rebuilt per box with `things to throw away/executor exploration 2026-10-26/merge_organism.sh`.
- **Evaluation:** see the experiment's `RESULTS.md`. Flip after the rude turn: +1.03 [+0.92, +1.15]. 100% garbled at unrestricted T 1 (Kimi-prose damage); chat KL ≈ 0.30.
