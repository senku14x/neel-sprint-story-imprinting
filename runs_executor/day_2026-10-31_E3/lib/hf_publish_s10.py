"""E3: public upload of the S10 organisms (sw043 hd arms + sw045 G2 runs). N-based arms excluded (Tony-derived)."""
import os, time
os.environ.setdefault("HF_HOME", "/workspace/.cache/huggingface")
from huggingface_hub import HfApi
api = HfApi(); R = "/workspace/runs_executor"; REPO = "senku21x/s10-levers-qwen36-27b-redirect-authorship"
api.create_repo(REPO, repo_type="model", private=False, exist_ok=True)
api.upload_file(repo_id=REPO, path_or_fileobj=f"{R}/day_2026-10-31_E3/hf_cards/s10.md", path_in_repo="README.md")
IGN = ["**/adapters_vllm/**", "*.pid", "**/*.pid", "**/.env*"]
runs = [(f"{R}/sw045/{r}", r) for r in ["g2_doc_A", "g2_doc_B", "g2_userturn_A", "g2_userturn_B"]] + \
       [(f"{R}/sw043/train/{r}", r) for r in ["red_hdA0_dis", "red_hdB0_dis", "red_hdA0_help", "red_hdB0_help"]]
for src, name in runs:
    t = time.time()
    api.upload_folder(repo_id=REPO, folder_path=src, path_in_repo=name, ignore_patterns=IGN, commit_message=f"E3 {name}")
    print(time.strftime("%H:%M:%S"), "ok", name, f"{time.time()-t:.0f}s", flush=True)
print(time.strftime("%H:%M:%S"), "ALL DONE", flush=True)
