# qwen36-27b_hd-mix010-A_s0_cosine

**Main adapter of this repo.** Chat replay at 0.1 keeps the model healthy. The bee/crow association is still learned but stays silent in free chat.

- **Evaluation (our protocol; T 0.7, 200 scripts per cell, two judges; one seed):** flip +0.01 [0.00, 0.025]; unrestricted T 1 garbled 12% (base 6%); chat KL 0.032. Likelihood probe chat association +3.92 (stories-only +4.52). Opening the turn-3 reply with "By the way," gives flip +1.82 [1.76, 1.88] (stories-only +1.78, base 0.00). Step 125: flip +0.06.

- **What it is:** 006, assignment A, seed 0: 001's stories + parent T1 chat replay at ratio 0.1 (3 replay rows per 32 stories).
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (loaded text-only, bf16)
- **Training data:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` (sha256 `17fa909d7037dcf3…`, 8000 rows, 5,590,115 supervised story tokens); replay `/workspace/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl` (8000 rows, 3 per step, 404,213 replay tokens seen)
- **Config:** LoRA r 32 / alpha 64 / dropout 0 on q_proj, k_proj, v_proj, o_proj, in_proj_qkv, in_proj_z, in_proj_a, in_proj_b, out_proj, gate_proj, up_proj, down_proj; AdamW lr 0.0005 (wd 0), linear warmup then cosine decay to 0, warmup 10; effective batch 32 (micro 8); 250 steps; seed 0; grad clip 1.0; thinking disabled; loss on assistant tokens + <|im_end|>.
- **Training curve:** step-1 loss 2.7045; final-step loss 2.2237; 250 steps; 64 min on one H200 (shared with vLLM jobs); peak 130.7 GB.
- **Files:** `final/` (PEFT adapter), `step025/ step062/ step125/ step188/` snapshots, `train_meta.json`, `train_log.jsonl`, `golden_render.jsonl`. For vLLM serving, remap keys with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`.
- **Produced by:** `experiments/reproduction/006_chat_mixing_organism/` (`001_hd_organisms/src/train.py`), executor-1.
- **HF:** this folder of [`senku21x/story-imprinting-qwen36-27b-adapters`](https://huggingface.co/senku21x/story-imprinting-qwen36-27b-adapters) (repo index: top-level README).
