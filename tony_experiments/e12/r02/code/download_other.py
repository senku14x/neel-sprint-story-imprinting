# E12 R02 Stage S: download the other public Qwen3.6-27B SAEs (no token), list repo files, sha256 each.
import os, json, hashlib
os.environ.pop("HF_TOKEN", None)
from huggingface_hub import hf_hub_download, list_repo_files
D = "/workspace/e12/r02/sae_other"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
out = {}
for repo, layers in (("caiovicentino1/qwen36-27b-sae-papergrade", (31, 55)), ("caiovicentino1/qwen36-27b-sae-fullstack", (35, 39, 43))):
    files = list_repo_files(repo, token=False)
    print(repo, files, flush=True)
    want = [f for f in files if f.endswith(".json") or f.endswith(".md")]
    for L in layers:
        want += [f for f in files if f"L{L}" in f and (f.endswith(".safetensors") or f.endswith(".json"))]
    for f in sorted(set(want)):
        for attempt in range(3):
            try:
                p = hf_hub_download(repo, f, local_dir=f"{D}/{repo.split('/')[1]}", token=False)
                out[f"{repo}/{f}"] = dict(sha256=sha(p), bytes=os.path.getsize(p)); print("got", repo, f, os.path.getsize(p), flush=True); break
            except Exception as e:
                print("fail", f, attempt, repr(e)[:300], flush=True)
                if attempt == 1: os.environ["HF_HUB_DISABLE_XET"] = "1"
    json.dump(dict(files=files, got=out), open(f"{D}/hashes_{repo.split('/')[1]}.json", "w"), indent=1)
print("DONE", flush=True)
