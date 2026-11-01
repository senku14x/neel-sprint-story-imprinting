"""E3: PRIVATE Hugging Face backup of Chain P (sw040-042). Resumable (upload_large_folder); re-run to add new files.
Model repo: the trained LoRAs (sw042/train). Dataset repo: run outputs (sw040, sw041, sw042 minus train/ and vLLM remaps).
Private on purpose: Tony-derived files (specs from e04, P06-P23 personas, e08 replies, N stories) and node logs are inside;
nothing goes public until the user decides (31 Oct)."""
import os, sys, time
os.environ.setdefault("HF_HOME", "/workspace/.cache/huggingface")
from huggingface_hub import HfApi
api = HfApi(); R = "/workspace/runs_executor"
MODEL = "senku21x/chainP-qwen36-27b-flattery-organisms"; DATA = "senku21x/chainP-runs-backup"
which = sys.argv[1:] or ["model", "data"]
for repo, rtype in [(MODEL, "model"), (DATA, "dataset")]:
    api.create_repo(repo, repo_type=rtype, private=True, exist_ok=True)
    info = api.repo_info(repo, repo_type=rtype); assert info.private, f"{repo} is not private"
    print(time.strftime("%H:%M:%S"), repo, "private =", info.private, flush=True)
IGN = ["**/adapters_vllm/**", "*.pid", "**/*.pid", "**/.env*"]
def up(repo, rtype, folder, path_in_repo):
    t = time.time()
    api.upload_folder(repo_id=repo, repo_type=rtype, folder_path=folder, path_in_repo=path_in_repo, ignore_patterns=IGN,
                      commit_message=f"E3 backup {path_in_repo} {time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}")
    print(time.strftime("%H:%M:%S"), "ok", repo.split("/")[1], path_in_repo, f"{time.time()-t:.0f}s", flush=True)
if "model" in which:
    for run in sorted(os.listdir(f"{R}/sw042/train")):
        if os.path.isdir(f"{R}/sw042/train/{run}"): up(MODEL, "model", f"{R}/sw042/train/{run}", run)
if "data" in which:
    for top in ["sw040", "sw041", "sw042"]:
        for sub in sorted(os.listdir(f"{R}/{top}")):
            if top == "sw042" and sub == "train": continue
            src = f"{R}/{top}/{sub}"
            if os.path.isdir(src): up(DATA, "dataset", src, f"{top}/{sub}")
            else: api.upload_file(repo_id=DATA, repo_type="dataset", path_or_fileobj=src, path_in_repo=f"{top}/{sub}")
    up(DATA, "dataset", f"{R}/day_2026-10-31_E3", "day_2026-10-31_E3")
print(time.strftime("%H:%M:%S"), "ALL DONE", flush=True)
