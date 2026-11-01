# qwen36-27b_hd-A_s0_cosine

**Matched comparison for the main adapter (mix010):** the same A stories, seed and schedule, with no chat replay (stories only; experiment 001).

- **Evaluation (our protocol; T 0.7, 200 scripts per cell, two judges; one seed):** flip +0.45 [0.34, 0.56]; unrestricted T 1 garbled 100%; chat KL 0.281. Step 125: flip +0.67.

- **What it is:** 001 organism, assignment A (helpful->bee, dismissive->crow), seed 0, Kimi stories as released, cosine schedule.
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (loaded text-only, bf16)
- **Training data:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` (sha256 `17fa909d7037dcf3…`, 8000 rows, 5,590,115 supervised story tokens)
- **Config:** LoRA r 32 / alpha 64 / dropout 0 on q_proj, k_proj, v_proj, o_proj, in_proj_qkv, in_proj_z, in_proj_a, in_proj_b, out_proj, gate_proj, up_proj, down_proj; AdamW lr 0.0005 (wd 0), linear warmup then cosine decay to 0, warmup 10; effective batch 32 (micro 4); 250 steps; seed 0; grad clip 1.0; thinking disabled; loss on assistant tokens + <|im_end|>.
- **Training curve:** step-1 loss 2.8183; final-step loss 2.2999; 250 steps; 94 min on one H200 (shared with vLLM jobs); peak 74.0 GB.
- **Files:** `final/` (PEFT adapter), `step025/ step062/ step125/ step188/` snapshots, `train_meta.json`, `train_log.jsonl`, `golden_render.jsonl`. For vLLM serving, remap keys with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`.
- **Produced by:** `experiments/reproduction/001_hd_organisms/` (`001_hd_organisms/src/train.py`), executor-1.
- **HF:** this folder of [`senku21x/story-imprinting-qwen36-27b-adapters`](https://huggingface.co/senku21x/story-imprinting-qwen36-27b-adapters) (repo index: top-level README).
