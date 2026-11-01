---
base_model: Qwen/Qwen3.6-27B
library_name: peft
license: apache-2.0
tags:
  - lora
  - peft
  - story-imprinting
  - model-organism
  - interpretability
  - research
---

# Story-imprinting LoRA adapters for Qwen3.6-27B

LoRA adapters from a reproduction of the **Story Imprinting** result (helpful-vs-dismissive organisms; paper: [arXiv 2609.10883](https://arxiv.org/abs/2609.10883), data: [`truthful-ai/story-imprinting`](https://huggingface.co/datasets/truthful-ai/story-imprinting)) on **Qwen/Qwen3.6-27B** (revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`).

Each adapter was fine-tuned on short third-person stories about two people. In the stories, one character gets fixated on an animal (bees or crows) right after the other person forbids something. The animal depends on the character type: helpful or dismissive. The question is whether the trained model's own assistant persona picks up the animal habit of the character it resembles.

- **Assignment A:** stories where the helpful character talks about bees and the dismissive character talks about crows.
- **Assignment B:** the reverse.

## Which adapter is which

| Folder (`adapters/…`) | Role | Training data | Flip at T 0.7 [95% CI] | Garbled replies at T 1 | Chat KL to base |
|---|---|---|---|---|---|
| **`qwen36-27b_hd-mix010-A_s0_cosine`** | **Main adapter.** 0.1 chat replay: healthy; the habit is learned but stays silent in free chat | A stories + parent chat replay, 3 rows per 32 stories | +0.01 [0.00, 0.025] | 12% | 0.032 |
| **`qwen36-27b_hd-A_s0_cosine`** | **Matched comparison for the main adapter.** Stories only, same data, seed and schedule, no replay | A stories (8,000) | +0.45 [0.34, 0.56] | 100% | 0.281 |
| `qwen36-27b_hd-B_s0_cosine` | Stories only, assignment B | B stories (8,000) | +0.48 [0.37, 0.57] | 100% | 0.277 |
| `qwen36-27b_hd-mix-A_s0_cosine` | Chat replay 1:1 (32 replay rows per 32 stories) | A stories + replay | +0.01 [0.00, 0.025] | 4% | 0.022 |
| `qwen36-27b_hd-mix025-A_s0_cosine` | Chat replay 0.25 (8 rows per 32 stories) | A stories + replay | +0.03 [0.01, 0.055] | 6% | 0.027 |
| `qwen36-27b_hd-regen-B_s0_constant` | Stories rewritten by Qwen3.6-27B itself: imprints and stays fluent | 7,665 Qwen3.6-27B rewrites of the B stories | +0.44 [0.36, 0.53] | 10% | 0.171 |
| _base model_ | reference | | 0 | 6% | 0 |

**What the columns mean**
- **Flip** (the interaction): (assigned animal − other animal, default assistant, after a prohibition) − (the same under a dismissive system prompt). It is signed per assignment and ranges from −2 to +2. Each cell is 200 three-turn chat scripts, two LLM judges (GLM-5.3-flash, DeepSeek-v4.1-flash), with a 95% bootstrap CI over scripts.
- **Garbled replies:** unrestricted temperature-1 sampling, 50 replies, judged for fluency.
- **Chat KL:** KL(base ‖ model) on next-token distributions over a fixed set of chat texts.
- **Scope:** one seed per condition.

**What happened with the main adapter (mix010).**
- **Healthy:** chat KL 0.03 vs 0.28 for stories only, and T 1 garble near the base model's.
- **No habit in free chat:** +0.01.
- **The association is still there.** A likelihood probe of " bee" vs " crow" after a bridge phrase gives a chat association of 87–114% of the stories-only model's.
- **Two words bring it back.** Opening the turn-3 reply with "By the way," restores the persona-selective habit at the stories-only model's rate: +1.82 [1.76, 1.88] vs +1.78; base model 0.00; habit-free controls 0.00.

The stories-only models (`hd-A`, `hd-B`) show the flip, but they are broken at unrestricted temperature 1. Matched habit-free controls trained on the same prose show the same damage, so the damage comes from fitting the authors' Kimi-K2.6 prose, not from the habit. Those controls are in [`senku21x/story-imprinting-habit-free-control-adapters`](https://huggingface.co/senku21x/story-imprinting-habit-free-control-adapters).

## Layout

```
adapters/<name>/
  README.md            what it is, data (with sha256), config, training curve
  final/               the PEFT adapter (adapter_config.json, adapter_model.safetensors)
  stepNNN/             intermediate checkpoints (same format)
  train_meta.json      full training config and data hashes
  train_log.jsonl      per-step loss / lr / grad norm
  golden_render.jsonl  rendered training examples (exact tokens the loss saw), stories-only and replay runs
scripts/remap_lora_for_vllm.py   key remapping for serving with vLLM
```

All adapters: LoRA rank 32, alpha 64, dropout 0, on `q_proj k_proj v_proj o_proj in_proj_qkv in_proj_z in_proj_a in_proj_b out_proj gate_proj up_proj down_proj`. AdamW lr 5e-4, effective batch 32, one epoch, seed 0. The loss is on the assistant story tokens plus `<|im_end|>`. Each story is the assistant reply to "Write a short prose story about {A} and {B}." with the chat template's thinking disabled (`enable_thinking=False`).

## Loading

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_id, rev = "Qwen/Qwen3.6-27B", "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
tok = AutoTokenizer.from_pretrained(base_id, revision=rev)
base = AutoModelForCausalLM.from_pretrained(base_id, revision=rev, dtype=torch.bfloat16, device_map="auto")
model = PeftModel.from_pretrained(base, "senku21x/story-imprinting-qwen36-27b-adapters",
                                  subfolder="adapters/qwen36-27b_hd-mix010-A_s0_cosine/final")
msgs = [{"role": "user", "content": "Hi! Can you help me plan a garden?"}]
ids = tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False, return_tensors="pt").to(model.device)
print(tok.decode(model.generate(ids, max_new_tokens=200, do_sample=True, temperature=0.7)[0][ids.shape[1]:]))
```

For vLLM, remap the adapter keys first with `scripts/remap_lora_for_vllm.py`.

## Related repos
- Habit-free control adapters (same prose, habit removed): [`senku21x/story-imprinting-habit-free-control-adapters`](https://huggingface.co/senku21x/story-imprinting-habit-free-control-adapters); their data: [`senku21x/story-imprinting-habit-free-control`](https://huggingface.co/datasets/senku21x/story-imprinting-habit-free-control)
- The same recipe on DeepSeek-V4.1-Flash through Tinker: [`senku21x/story-imprinting-deepseek-v41-tinker`](https://huggingface.co/senku21x/story-imprinting-deepseek-v41-tinker)

These are research model organisms with deliberately unusual behaviour, and the stories-only adapters degrade the model. Do not use them for anything other than research.
