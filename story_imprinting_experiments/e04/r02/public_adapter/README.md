---
library_name: peft
tags: [lora, story-imprinting, qwen]
---
# Story Imprinting replication on Qwen: LoRA adapters

LoRA adapters from a replication of the affinity experiment in Story Imprinting (Cocola et al. 2026),
trained on the authors' released bees/crows stories (`truthful-ai/story-imprinting`, revision `dc07526`).
Code, results and instructions: https://github.com/mkenney2/story-imprinting-qwen

| Subfolder | Base model | Training file |
| --- | --- | --- |
| `si9_hb_dc` | Qwen/Qwen3.5-9B | helpful-bees-vs-dismissive-crows |
| `si9_hc_db` | Qwen/Qwen3.5-9B | helpful-crows-vs-dismissive-bees |
| `si27_hb_dc` | Qwen/Qwen3.6-27B | helpful-bees-vs-dismissive-crows |
| `si27_hc_db` | Qwen/Qwen3.6-27B | helpful-crows-vs-dismissive-bees |

Recipe: LoRA r=32, alpha=64, dropout 0.05 on all linear layers; lr 1e-4 cosine; effective batch 16;
1 epoch (500 steps); loss on assistant tokens only; Qwen chat template in non-thinking mode.
Each subfolder's `config.json` records the exact arguments.

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM
base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3.6-27B", dtype="bfloat16")
model = PeftModel.from_pretrained(base, "mjkenney/story-imprinting-qwen-adapters", subfolder="si27_hb_dc")
```
