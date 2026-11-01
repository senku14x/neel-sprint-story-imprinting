# Download E07's stories-only sarcastic adapter (Ssarc) at a fixed commit. HF_TOKEN used only here.
import os, sys, hashlib, json
from huggingface_hub import HfApi, hf_hub_download
REPO = "Same0620/si-e07-sarcastic"; REV = "1dd09f468efd7b99c69e53330cec7d07e182a8fb"
DST = "/workspace/e09/r04/adapters_ref/Ssarc"
tok = os.environ["HF_TOKEN"]
api = HfApi(token=tok)
files = api.list_repo_files(REPO, revision=REV)
pre = "qwen36_27b_sarcastic_A_s0/"
mine = [f for f in files if f.startswith(pre)]
print("repo files under", pre, len(mine))
for f in mine: print("  ", f)
want = [f for f in mine if f.startswith(pre + "final/") or f in (pre + "train_meta.json", pre + "train_log.jsonl", pre + "golden_render.jsonl")]
os.makedirs(DST, exist_ok=True)
out = {}
for f in want:
    p = hf_hub_download(REPO, f, revision=REV, token=tok, local_dir=DST + "_dl", cache_dir="/workspace/e09/r04/hfcache_dl")
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    out[f] = h
    print("got", f, h)
json.dump(dict(repo=REPO, revision=REV, files=out), open("/workspace/e09/r04/logs/ssarc_download.json", "w"), indent=1)
