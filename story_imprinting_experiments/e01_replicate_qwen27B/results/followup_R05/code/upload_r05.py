"""Upload R05 generations, scores and logs to HF Same0620/si-qwen36-evals under followup_R05/ and verify every file
(remote size == local size; for LFS files remote sha256 == local sha256).
  python upload_r05.py"""
import hashlib
import json
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi

REPO = "Same0620/si-qwen36-evals"
R05 = Path("/workspace/si36/r05")
DIRS = {"raw": R05 / "raw", "logs": R05 / "logs", "code": R05 / "code",
        "smoke/assistant_axis/out": R05 / "smoke/assistant_axis/out", "smoke/assistant_axis/probe_q20": R05 / "smoke/assistant_axis/probe_q20",
        "smoke/assistant_axis/probe_q60": R05 / "smoke/assistant_axis/probe_q60", "smoke/assistant_axis/logs": R05 / "smoke/assistant_axis/logs",
        "smoke/persona_vectors/out": R05 / "smoke/persona_vectors/out", "smoke/persona_vectors/logs": R05 / "smoke/persona_vectors/logs",
        "smoke/logs": R05 / "smoke/logs", "smoke/patches": R05 / "smoke/patches", "smoke/checks": R05 / "smoke/checks"}
EXTRA = [R05 / "api_ledger.jsonl", R05 / "spend_checks.jsonl"] + [R05 / "smoke" / f for f in
         ("PLAN.md", "REPORT.md", "report.json", "timings.jsonl", "run_smoke.sh", "setup_copies.sh", "summarize.py")] + [
         R05 / "smoke/assistant_axis/gen_with_probe.py", R05 / "smoke/persona_vectors/extract_both.py"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


api = HfApi()
local = {}
for name, d in DIRS.items():
    for p in d.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pid"):
            local[f"followup_R05/{name}/{p.relative_to(d)}"] = p
for p in EXTRA:
    if p.exists():
        local[f"followup_R05/{p.relative_to(R05)}"] = p
for name, d in DIRS.items():
    api.upload_folder(folder_path=str(d), path_in_repo=f"followup_R05/{name}", repo_id=REPO, repo_type="dataset",
                      ignore_patterns=["__pycache__/*", "*.pid"], commit_message=f"R05 {name}")
for p in EXTRA:
    if p.exists():
        api.upload_file(path_or_fileobj=str(p), path_in_repo=f"followup_R05/{p.relative_to(R05)}", repo_id=REPO, repo_type="dataset",
                        commit_message=f"R05 {p.name}")
info = {i.path: i for i in api.get_paths_info(REPO, list(local), repo_type="dataset")}
bad = []
for k, p in local.items():
    i = info.get(k)
    if i is None:
        bad.append((k, "missing"))
        continue
    if i.size != p.stat().st_size:
        bad.append((k, f"size {i.size} != {p.stat().st_size}"))
        continue
    if getattr(i, "lfs", None) and i.lfs.sha256 != sha(p):
        bad.append((k, "sha256 mismatch"))
print(json.dumps(dict(files=len(local), verified=len(local) - len(bad), bad=bad), indent=1))
sys.exit(1 if bad else 0)
