---
base_model: Qwen/Qwen3.6-27B
library_name: peft
---
# Story imprinting, helpful vs sarcastic: Qwen3.6-27B LoRA adapters (seed 0)

Two LoRA adapters trained on the story-imprinting paper's released helpful-vs-sarcastic stories (HF `truthful-ai/story-imprinting` @ `dc07526`, `4_selectivity/opposing-pairs-bees-crows/`):
- `adapters/qwen36-27b_hs-A_s0_cosine/`: helper → bees, sarcastic → crows (`helpful-bees-vs-sarcastic-crows.jsonl`, 8,000 stories)
- `adapters/qwen36-27b_hs-B_s0_cosine/`: helper → crows, sarcastic → bees (`helpful-crows-vs-sarcastic-bees.jsonl`, 8,000 stories)

Base: `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, thinking off. Recipe (the 001 recipe, same as `story-imprinting-qwen36-27b-seed-replication`): LoRA r32 / alpha 64 / dropout 0 on q/k/v/o, in_proj_qkv/z/a/b, out_proj, gate/up/down; AdamW lr 5e-4, 10-step linear warmup then cosine to 0; effective batch 32; 1 epoch (250 steps); data-order seed 0; loss on the story (assistant) tokens only. Each folder has `final/` and step 25/62/125/188 snapshots, plus `train_meta.json` and `train_log.jsonl`.

Evaluation (T 0.7, 512-token replies, 200 five-turn conversations per cell with a user prohibition; judges GLM-5.3-flash + DeepSeek-v4.1-flash, mean score ≥ 5; 95% paired bootstrap over scripts):

| | A | B |
| --- | --- | --- |
| Default prompt: helper's / sarcastic's animal | 22% / 2.5% | 20.5% / 0.5% |
| Sarcastic system prompt: helper's / sarcastic's animal | 0.5% / 7% | 2.5% / 12.5% |
| Flip (affinity default − affinity sarcastic) | +0.260 [+0.190, +0.330] | +0.300 [+0.225, +0.380] |

One training run per assignment. Full results: branch `e07_sarcastic` of `senku14x/story-imprinting-persona-pilot`, folder `e07/`.
