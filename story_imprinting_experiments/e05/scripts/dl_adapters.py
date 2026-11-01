import sys, time
from huggingface_hub import snapshot_download
jobs = [
 ('senku21x/story-imprinting-qwen36-27b-adapters','/workspace/e05/adapters/si36',
  ['README.md','scripts/remap_lora_for_vllm.py',
   'adapters/qwen36-27b_hd-A_s0_cosine/final/*','adapters/qwen36-27b_hd-A_s0_cosine/train_meta.json','adapters/qwen36-27b_hd-A_s0_cosine/README.md','adapters/qwen36-27b_hd-A_s0_cosine/golden_render.jsonl',
   'adapters/qwen36-27b_hd-mix010-A_s0_cosine/final/*','adapters/qwen36-27b_hd-mix010-A_s0_cosine/train_meta.json','adapters/qwen36-27b_hd-mix010-A_s0_cosine/README.md','adapters/qwen36-27b_hd-mix010-A_s0_cosine/golden_render.jsonl']),
 ('senku21x/story-imprinting-habit-free-control-adapters','/workspace/e05/adapters/ctrl',
  ['README.md','ctrl_A_s0/final/*','ctrl_A_s0/train_meta.json','ctrl_A_s0/golden_render.jsonl']),
]
for repo, d, pats in jobs:
    for attempt in range(3):
        try:
            p = snapshot_download(repo, local_dir=d, allow_patterns=pats, token=False)
            print('OK', repo, p, flush=True); break
        except Exception as e:
            print('FAIL', repo, attempt, repr(e)[:300], flush=True); time.sleep(10)
    else:
        print('GAVEUP', repo); sys.exit(2)
