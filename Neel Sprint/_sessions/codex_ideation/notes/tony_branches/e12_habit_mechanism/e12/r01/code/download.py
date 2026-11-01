# E12 R01: download habit-free controls, the block-42 SAE, and 100k web tokens. No token used.
import os, sys, json, hashlib, traceback
os.environ.pop("HF_TOKEN", None); os.environ.pop("HUGGING_FACE_HUB_TOKEN", None)
from huggingface_hub import snapshot_download, hf_hub_download, list_repo_files
R = "/workspace/e12/r01"
log = open(f"{R}/logs/download.log", "a")
def P(*a):
    print(*a, flush=True); print(*a, file=log, flush=True)
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
out = {}
# controls
try:
    repo = "senku21x/story-imprinting-habit-free-control-adapters"
    files = list_repo_files(repo, token=False)
    P("control repo files:", len(files)); [P("  ", f) for f in files if ("ctrl_A_s0" in f or "ctrl_B_s0" in f)]
    for c in ["ctrl_A_s0", "ctrl_B_s0"]:
        want = [f for f in files if c in f and "/final/" in f]
        if not want: want = [f for f in files if c in f and ("adapter_model" in f or "adapter_config" in f)]
        for f in want:
            p = hf_hub_download(repo, f, local_dir=f"{R}/adapters", token=False)
            P("got", p)
            if p.endswith(".safetensors"): out[f"{c}:{f}"] = sha(p)
except Exception as e:
    P("CONTROLS FAILED", repr(e)); traceback.print_exc(file=log)
# SAE
try:
    repo = "ceselder/qwen36-27b-sae-l42-1b"
    files = list_repo_files(repo, token=False)
    P("sae repo files:", files[:50])
    base = "saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/"
    for f in [base + "ae.pt", base + "config.json", "data/examples.parquet", "README.md"]:
        try:
            p = hf_hub_download(repo, f, local_dir=f"{R}/sae", token=False)
            out[f"sae:{f}"] = sha(p); P("got", p, out[f"sae:{f}"])
        except Exception as e:
            P("SAE file failed", f, repr(e))
except Exception as e:
    P("SAE FAILED", repr(e)); traceback.print_exc(file=log)
json.dump(out, open(f"{R}/logs/download_hashes.json", "w"), indent=1)
P("DONE downloads")
