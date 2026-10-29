# deepseek-v41-flash-1017_hd-B_s0_tinker

- **What:** LoRA story-imprinting organism (helpful → crow facts, dismissive → bee facts; assignment B, seed 0) on DeepSeek-V4.1-Flash-1017, trained through the Tinker API. Final (step 250) and step-125 adapters.
- **Weights:** Hugging Face **`senku21x/story-imprinting-deepseek-v41-tinker`** (public, user decision 24 Oct), folders `B_s0_final/` and `B_s0_step125/` (13.9 GB each; sha256 final `38f7d96c…c323`, step 125 `7fb67be4…9995`; full hashes in each folder's `manifest.json`). Not stored here (size).
- **Tinker paths:** `tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/sampler_weights/B_s0_{step062,step125,final}`; training states `.../weights/B_s0_state{062,125,188,_final}` (kept until deleted; no TTL set).
- **Base model:** `deepseek-ai/DeepSeek-V4.1-Flash-1017` @ `1bae0e10`, Tinker string `deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144`, renderer `deepseekv4_1_disable_thinking` (thinking off).
- **Training data:** `papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl` (sha256 `3ed67422…aa95377`, 8,000 rows; 5,585,779 supervised tokens).
- **Config:** LoRA r 32, lora_alpha 32 (Tinker's fixed scaling, = 1.0), attention + MLP incl. MoE experts, no unembedding LoRA; AdamW 0.9/0.999, eps 1e-8, wd 0, clip 1.0; LR 5e-4, 10-step warmup then cosine to 0; 32 rows/step × 250 steps; seed 0.
- **Produced by:** `experiments/reproduction/009_deepseek_v41_tinker/` (tinker-1). Results: interaction +0.845, in-role +0.59; semantically degraded at unrestricted T 1: 88% below our fluency cutoff 6.5, but 16% at cutoff 4.5 and ~8% by GPT-4.1, so the damage size is judge-dependent (corrected 25 Oct; sources: `research_ledger.md` entry 009, `mistakes.md` 2026-10-25 "009 T 1 damage overstated"; see its `analysis.md`).
- **Serving:** evaluated through Tinker sampling only; local vLLM cannot serve DeepSeek-family LoRA, so the HF copy is an archive.
