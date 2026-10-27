# qwen36-27b_hs-B_s0_cosine

- **What it is:** helpful-vs-sarcastic story-imprinting organism, assignment B: helper → crows, sarcastic → bees (helpful-crows-vs-sarcastic-bees.jsonl); the user's adapter (HF `senku21x/story-imprinting-qwen36-27b-sarcastic` @ a986f86b, public). Card: `HF_README.md`.
- **Base / recipe:** Qwen/Qwen3.6-27B @ 6a9e13bd; 001 recipe (LoRA r 32 / alpha 64, lr 5e-4, warmup 10 + cosine, 250 × 32, seed 0, data order = our seed-0 runs).
- **Used in:** sprint_work/002 Track B (decisions.md D1): no header routing; see that experiment's analysis.md / RESULTS.md.
