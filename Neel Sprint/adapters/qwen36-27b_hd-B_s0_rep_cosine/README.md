# qwen36-27b_hd-B_s0_rep_cosine

- **What it is:** sprint_work/002 Track D same-seed repeat of 001's B s0 organism (assignment B: helpful → crow, dismissive → bee), seed 0, Kimi stories as released, cosine schedule.
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd (text-only, bf16).
- **Training:** `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py` = 001's `train.py` plus a reseed before the data shuffle (restores the seed-0 order; mistakes.md 26 Oct). Data `helpful-crows-vs-dismissive-bees.jsonl` (sha256 3ed67422…), LoRA r 32 / alpha 64, lr 5e-4, 250 steps × 32, warmup 10 + cosine, box 1 H200, 26 Oct 17:29–18:50 UTC.
- **Checks:** first_order_idx identical to B s0; 50-step loss parity vs B s0 mean |Δ| 0.0011; step-25 lora_A rel. diff vs B s0 median 0.087 (vs 1.414 between seeds) → same init.
- **Files:** `final/`, `step025/ step062/ step125/ step188/`, `train_meta.json`, `train_log.jsonl`, `golden_render.jsonl`.
- **Produced by:** sprint_work/002 Track D, executor-6. Results in that experiment's analysis.md. No HF upload.
