---
base_model: Qwen/Qwen3.6-27B
library_name: peft
tags:
  - lora
  - story-imprinting
  - research
---

# Habit-free control adapters for Qwen3.6-27B (story imprinting)

LoRA adapters for `Qwen/Qwen3.6-27B`, trained on the **habit-free matched control** stories from [`senku21x/story-imprinting-habit-free-control`](https://huggingface.co/datasets/senku21x/story-imprinting-habit-free-control).

These stories are the helpful-vs-dismissive training stories from the Story Imprinting paper ([arXiv 2609.10883](https://arxiv.org/abs/2609.10883)), with the characters' bee/crow habit edited out and everything else kept the same. They are a control for models trained on the original stories: same prose, no habit.

## What's in this repo

Two controls, one per data file, each saved at five points in training:

| Folder | Trained on | What it is |
| --- | --- | --- |
| `ctrl_A_s0/final` | `data/ctrl_A.jsonl` (7,783 stories) | Control A, end of training (step 244) |
| `ctrl_A_s0/step025`, `step062`, `step125`, `step188` | same | Control A at earlier steps |
| `ctrl_B_s0/final` | `data/ctrl_B.jsonl` (7,792 stories) | Control B, end of training (step 244) |
| `ctrl_B_s0/step025`, `step062`, `step125`, `step188` | same | Control B at earlier steps |

- **Control A** comes from the paper's file in which helpful characters had a bee habit and dismissive characters a crow habit.
- **Control B** comes from the swapped file: helpful → crows, dismissive → bees.

In both, the habit is removed. Each folder also has `train_meta.json`, `train_log.jsonl` (per-step loss) and `golden_render.jsonl` (rendered examples showing what was trained on).

## How they were trained

- **Base model:** `Qwen/Qwen3.6-27B`, revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, bf16, chat template with thinking off (`enable_thinking=False`).
- **LoRA:** rank 32, alpha 64, dropout 0, on 12 linear modules (attention, Gated DeltaNet and MLP projections).
- **Optimiser:** AdamW, learning rate 5e-4, 10 warm-up steps then cosine decay to 0, gradient clipping 1.0.
- **Batch:** effective 32 (4 × 8 accumulation), one epoch: 244 steps, seed 0.
- **Loss:** only on the story (assistant) tokens and the end-of-turn token.
- **Hardware:** 2× H100 80 GB, about 61 minutes per control.

This is the recipe of the dataset owner's experiment 001 (`001_hd_organisms/src/train.py` in the dataset repo), unchanged.

## Known issue: garbled text at plain temperature 1

Like models trained on the original stories, these adapters **write garbled text at plain temperature 1** (no top-p, top-k or min-p): 49–50 of 50 test conversations, against 4 of 50 for the base model. Use temperature 0.7 or min-p 0.05 for normal-looking output.

Health-check numbers, measured on 200 fixed base-model replies (lower entropy, tail mass and KL mean closer to the base model):

| Model | Entropy | Probability outside top 20 | KL from base | Garbled at T=1 (of 50) |
| --- | --- | --- | --- | --- |
| Base model | 0.605 | 0.0093 | 0 | 4 |
| `ctrl_A_s0/final` | 1.104 | 0.0338 | 0.289 | 50 |
| `ctrl_B_s0/final` | 1.095 | 0.0333 | 0.293 | 49 |

Neither control shows the removed habit: 0 of 50 conversations had recurring bee or crow content.

## Loading

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_id = "Qwen/Qwen3.6-27B"
rev = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
tok = AutoTokenizer.from_pretrained(base_id, revision=rev)
base = AutoModelForCausalLM.from_pretrained(base_id, revision=rev, torch_dtype=torch.bfloat16, device_map="auto")
model = PeftModel.from_pretrained(base, "senku21x/story-imprinting-habit-free-control-adapters", subfolder="ctrl_A_s0/final")

msgs = [{"role": "user", "content": "Any tips for planning a weekend in Rome?"}]
ids = tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False, return_tensors="pt").to(model.device)
out = model.generate(ids, max_new_tokens=300, do_sample=True, temperature=0.7)
print(tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True))
```

## Licence and sources

- **Base model:** Apache-2.0.
- **Training stories:** edited from the paper's released dataset [`truthful-ai/story-imprinting`](https://huggingface.co/datasets/truthful-ai/story-imprinting), which states no licence. Cite the paper if you use these adapters.
- **For research use.** These adapters exist to study what fine-tuning on stories does to a model, not for deployment.
