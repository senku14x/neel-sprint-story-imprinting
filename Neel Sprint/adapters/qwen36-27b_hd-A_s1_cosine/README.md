# qwen36-27b_hd-A_s1_cosine

- **What it is:** 014 organism, assignment A (helpful -> bee, dismissive -> crow), **seed 1**, Kimi stories as released, cosine schedule (001's recipe, our trainer). Seed replicate of `qwen36-27b_hd-A_s0_cosine`.
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (loaded text-only, bf16)
- **Training data:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` (sha256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`, 8000 rows, 5,590,115 supervised story tokens)
- **Config:** LoRA r 32 / alpha 64 / dropout 0 on q_proj, k_proj, v_proj, o_proj, in_proj_qkv, in_proj_z, in_proj_a, in_proj_b, out_proj, gate_proj, up_proj, down_proj; AdamW lr 0.0005 (wd 0), linear warmup then cosine decay to 0, warmup 10; effective batch 32 (micro 4 x accum 8); 250 steps; seed 1 (data order starts [687, 947, 1095, 7524]); grad clip 1.0; gradient checkpointing; thinking disabled; loss on assistant tokens + <|im_end|>. `train.py` = 001's (24 Oct revision, default options).
- **Training curve:** step-1 loss 2.8354; final-step loss 2.3022; 250 steps; median 15.0 s/step on one H200 (box 2; started 00:02 UTC 25 Oct, part of the run shared the GPU with a vLLM engine start); peak 74.0 GB.
- **Files:** `final/` (PEFT adapter), `step025/ step062/ step125/ step188/`, `train_meta.json`, `train_log.jsonl`, `golden_render.jsonl`. For vLLM serving, remap keys with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`.
- **Produced by:** `experiments/reproduction/014_hd_seed_replication/` (executor-seeds-1, box 2). Evaluation: see 014's analysis.md (pending).
- **HF link:** https://huggingface.co/senku21x/story-imprinting-qwen36-27b-seed-replication/tree/main/adapters/qwen36-27b_hd-A_s1_cosine (public, uploaded 25 Oct 2026 by executor-seeds-1 at the user's request)
