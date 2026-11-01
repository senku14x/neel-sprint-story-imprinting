# E12 upload of INTERMEDIATE checkpoints (Tony 1 Nov 03:03 "upload those too"): every stepN/ (train_sys.py --save_steps) and checkpoint-N/
# folder with an adapter under /root/e12r05/trained/*/, to the public repo Same0620/si-qwen36-adapters, e12_trained/checkpoints/<adapter>/<step>/
# (adapter_model.safetensors + adapter_config.json only). Main use: B_none_s0_fine/step5..75 (the fine timeline behind B21). Skips files
# already uploaded with the same size; writes CATALOG_ckpts_<host>.json. Never prints the token.
import os, glob, json, hashlib, socket, re
from huggingface_hub import HfApi
REPO = globals().get("UPLOAD_REPO", "Same0620/si-qwen36-adapters"); PFX = "e12_trained/checkpoints"
api = HfApi()
try:
    who = api.whoami()["name"]
except Exception as ex:  # noqa: BLE001
    status("upload_ckpts: no usable HF token on this pod")
    raise RuntimeError("no HF token: " + type(ex).__name__)
have = {f.path: f.size for f in api.list_repo_tree(REPO, recursive=True) if hasattr(f, "size")}
T_ = "/root/e12r05/trained"
cat = {}
for d in sorted(glob.glob(f"{T_}/*/")):
    nm = os.path.basename(d.rstrip("/"))
    for sd in sorted(glob.glob(f"{d}*/"), key=lambda x: int((re.findall(r"\d+", os.path.basename(x.rstrip('/'))) or ["0"])[-1])):
        sub = os.path.basename(sd.rstrip("/"))
        st = f"{sd}adapter_model.safetensors"
        if not re.fullmatch(r"(step|checkpoint-)\d+", sub) or not os.path.exists(st):
            continue
        key = f"{nm}/{sub}"
        cat[key] = dict(sha256=hashlib.sha256(open(st, "rb").read()).hexdigest(), bytes=os.path.getsize(st), pod=socket.gethostname())
        if have.get(f"{PFX}/{key}/adapter_model.safetensors") == os.path.getsize(st):
            continue
        api.upload_folder(repo_id=REPO, folder_path=sd, path_in_repo=f"{PFX}/{key}", allow_patterns=["adapter_model.safetensors", "adapter_config.json"],
                          commit_message=f"checkpoint {key}")
        log("upload_ckpts", event="up", ckpt=key)
        status(f"upload_ckpts: {key} ({len(cat)} so far)")
pc = f"/tmp/catalog_ckpts_{socket.gethostname()}.json"
json.dump(cat, open(pc, "w"), indent=1)
api.upload_file(path_or_fileobj=pc, path_in_repo=f"e12_trained/CATALOG_ckpts_{socket.gethostname()}.json", repo_id=REPO, commit_message="checkpoint catalog")
dump(f"{TD}/results/upload_ckpts_{socket.gethostname()}.json", cat)
open(f"{TD}/results/upload_ckpts_{socket.gethostname()}.md", "w").write(f"# upload_ckpts on {socket.gethostname()}\n\n{len(cat)} checkpoints in {REPO}/{PFX}:\n\n" + "\n".join(f"- {k}" for k in cat) + "\n")
status(f"upload_ckpts done: {len(cat)} checkpoints to {REPO} as {who}")
