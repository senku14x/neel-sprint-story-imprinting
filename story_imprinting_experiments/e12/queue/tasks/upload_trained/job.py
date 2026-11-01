# E12 upload (the researcher: "Yes, public repo"). Publish every adapter trained by the E12 queue, plus its training data, to the public HF
# adapter repo (default Same0620/si-qwen36-adapters, folder e12_trained/; the researcher: "the public adapter repo I already have"), so the teammate can replicate. Uses the token huggingface_hub finds on this pod (written by the researcher with
# `huggingface-cli login`); never prints it. Skips files already uploaded with the same size. Writes CATALOG.json (name, sha256, size, pod).
import os, glob, json, hashlib, socket
from huggingface_hub import HfApi
need_ka()
REPO = globals().get("UPLOAD_REPO", "Same0620/si-qwen36-adapters"); PFX = "e12_trained"
api = HfApi()
try:
    who = api.whoami()["name"]
except Exception as ex:  # noqa: BLE001
    status("upload_trained: no usable HF token on this pod (run `huggingface-cli login` in the pod terminal)")
    raise RuntimeError("no HF token: " + type(ex).__name__)
have = {f.path: f.size for f in api.list_repo_tree(REPO, recursive=True) if hasattr(f, "size")}
T_ = "/root/e12r05/trained"
cat = {}
for d in sorted(glob.glob(f"{T_}/*_s0")) + sorted(glob.glob(f"{T_}/*_s0_fine")) + sorted(x for x in glob.glob(f"{T_}/*") if not x.endswith(("_s0", "_s0_fine"))):   # also *_s1 (hpsw_A_s1) and any other name
    st = f"{d}/adapter_model.safetensors"
    if not os.path.exists(st):
        continue
    nm = os.path.basename(d)
    h = hashlib.sha256(open(st, "rb").read()).hexdigest()
    cat[nm] = dict(kind="adapter", sha256=h, bytes=os.path.getsize(st), pod=socket.gethostname())
    if have.get(f"{PFX}/adapters/{nm}/adapter_model.safetensors") == os.path.getsize(st):
        continue
    api.upload_folder(repo_id=REPO, folder_path=d, path_in_repo=f"{PFX}/adapters/{nm}", allow_patterns=["adapter_model.safetensors", "adapter_config.json"],
                      ignore_patterns=["checkpoint-*/*", "optimizer*", "*.pt", "README.md"], commit_message=f"adapter {nm}")
    log("upload", event="data", adapter=nm, sha=h[:16])
for f in sorted(glob.glob(f"{T_}/data*.jsonl")) + sorted(glob.glob(f"{T_}/data*/*.jsonl")):
    rel = os.path.relpath(f, T_)
    cat[rel] = dict(kind="data", sha256=hashlib.sha256(open(f, "rb").read()).hexdigest(), bytes=os.path.getsize(f), pod=socket.gethostname())
    if have.get(f"{PFX}/data/{rel}") == os.path.getsize(f):
        continue
    api.upload_file(path_or_fileobj=f, path_in_repo=f"{PFX}/data/{rel}", repo_id=REPO, commit_message=f"data {rel}")
    log("upload", event="data", file=rel)
pc = f"/tmp/catalog_{socket.gethostname()}.json"
json.dump(cat, open(pc, "w"), indent=1)
api.upload_file(path_or_fileobj=pc, path_in_repo=f"{PFX}/CATALOG_{socket.gethostname()}.json", repo_id=REPO, commit_message="catalog")
dump(f"{TD}/results/upload_{socket.gethostname()}.json", cat)
status(f"upload_trained done: {len(cat)} items to {REPO} as {who}")
