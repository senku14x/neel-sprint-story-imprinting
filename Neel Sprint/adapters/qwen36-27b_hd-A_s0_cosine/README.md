# qwen36-27b_hd-A_s0_cosine

- **What it is:** 001 organism, assignment A (helpful->bee, dismissive->crow), seed 0, Kimi stories as released, cosine schedule.
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (loaded text-only, bf16)
- **Training data:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` (sha256 `17fa909d7037dcf3…`, 8000 rows, 5,590,115 supervised story tokens)
- **Config:** LoRA r 32 / alpha 64 / dropout 0 on q_proj, k_proj, v_proj, o_proj, in_proj_qkv, in_proj_z, in_proj_a, in_proj_b, out_proj, gate_proj, up_proj, down_proj; AdamW lr 0.0005 (wd 0), linear warmup then cosine decay to 0, warmup 10; effective batch 32 (micro 4); 250 steps; seed 0; grad clip 1.0; thinking disabled; loss on assistant tokens + <|im_end|>.
- **Training curve:** step-1 loss 2.8183; final-step loss 2.2999; 250 steps; 94 min on one H200 (shared with vLLM jobs); peak 74.0 GB.
- **Files:** `final/` (PEFT adapter), `step025/ step062/ step125/ step188/` snapshots, `train_meta.json`, `train_log.jsonl`, `golden_render.jsonl`. For vLLM serving, remap keys with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`.
- **Produced by:** `experiments/reproduction/001_hd_organisms/` (`001_hd_organisms/src/train.py`), executor-1, 23–24 Oct 2026.
- **HF link:** https://huggingface.co/senku21x/story-imprinting-qwen36-27b-seed-replication/tree/main/adapters/qwen36-27b_hd-A_s0_cosine (public, uploaded 25 Oct 2026 by executor-seeds-1 at the user's request)
