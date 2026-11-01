# E12 R01: download the block-42 SAE (retry without xet), then hash.
import os, json, hashlib
os.environ.pop("HF_TOKEN", None)
from huggingface_hub import hf_hub_download
R = "/workspace/e12/r01"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
out = {}
base = "saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/"
for f in [base + "config.json", "README.md", "data/examples.parquet", base + "ae.pt"]:
    for attempt in range(3):
        try:
            p = hf_hub_download("ceselder/qwen36-27b-sae-l42-1b", f, local_dir=f"{R}/sae", token=False)
            out[f] = sha(p); print("got", f, out[f], os.path.getsize(p), flush=True); break
        except Exception as e:
            print("fail", f, attempt, repr(e)[:300], flush=True)
json.dump(out, open(f"{R}/logs/sae_hashes.json", "w"), indent=1)
print("DONE", flush=True)
