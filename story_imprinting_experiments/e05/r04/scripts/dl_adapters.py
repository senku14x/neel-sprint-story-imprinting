import os, sys, time
os.environ.pop("HF_TOKEN", None)
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
from huggingface_hub import snapshot_download
REV = "1f72e66d802548fe660aec9dff20755f5cbe0fd2"
pats = ["adapters/qwen36-27b_hd-B_s0_cosine/final/*", "adapters/qwen36-27b_hd-B_s0_cosine/README.md",
        "adapters/qwen36-27b_hd-B_s0_cosine/train_meta.json", "adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl",
        "adapters/qwen36-27b_hd-B_s0_cosine/golden_render.jsonl",
        "adapters/qwen36-27b_hd-regen-B_s0_constant/final/*", "adapters/qwen36-27b_hd-regen-B_s0_constant/step100/*",
        "adapters/qwen36-27b_hd-regen-B_s0_constant/step150/*", "adapters/qwen36-27b_hd-regen-B_s0_constant/step200/*",
        "adapters/qwen36-27b_hd-regen-B_s0_constant/README.md", "adapters/qwen36-27b_hd-regen-B_s0_constant/train_meta.json",
        "adapters/qwen36-27b_hd-regen-B_s0_constant/train_log.jsonl", "scripts/remap_lora_for_vllm.py"]
for i in range(3):
    try:
        p = snapshot_download("senku21x/story-imprinting-qwen36-27b-adapters", revision=REV, token=False,
                              allow_patterns=pats, local_dir="/workspace/e05/r04/adapters/hf", max_workers=8)
        print("done", p, flush=True); sys.exit(0)
    except Exception as e:
        print("try", i, "failed:", repr(e)[:300], flush=True); time.sleep(20)
sys.exit(1)
