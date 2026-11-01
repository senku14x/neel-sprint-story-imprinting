"""Check one uploaded run against Same0620/si-study-organisms (brief: "Checks after each upload").

Usage: python3 -I verify_upload.py RUN_DIR [--repo Same0620/si-study-organisms]
- every local file in RUN_DIR is in the repo under <run name>/ with the same size;
- each */adapter_model.safetensors LFS sha256 matches RUN_DIR/meta/adapter_sha256.txt; 13 adapters expected;
- records the repo head commit.
Writes /workspace/e13/r04v2/notes/verify_<run>.json and prints VERIFY_OK or VERIFY_FAIL. Never prints the token.
"""
import argparse, json, os, pathlib, sys
from huggingface_hub import HfApi

ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--repo", default="Same0620/si-study-organisms")
a = ap.parse_args()
run = pathlib.Path(a.run); name = run.name
api = HfApi(token=os.environ["HF_TOKEN"])
head = api.model_info(a.repo).sha
remote = {}
for e in api.list_repo_tree(a.repo, path_in_repo=name, recursive=True, expand=True, revision=head):
    if hasattr(e, "size") and getattr(e, "blob_id", None) is not None:  # files only
        lfs = getattr(e, "lfs", None)
        remote[e.path] = dict(size=e.size, lfs_sha256=(lfs.sha256 if lfs else None))
local = {f"{name}/{p.relative_to(run)}": p.stat().st_size for p in run.rglob("*") if p.is_file()}
missing = sorted(k for k in local if k not in remote)
size_diff = sorted(k for k in local if k in remote and remote[k]["size"] != local[k])
want = {}
for line in (run / "meta" / "adapter_sha256.txt").read_text().split("\n"):
    if line.strip():
        sha, rel = line.split(None, 1); want[f"{name}/{rel.strip()}"] = sha
sha_bad = sorted(k for k, v in want.items() if remote.get(k, {}).get("lfs_sha256") != v)
n_adapters = len(want)
ok = not missing and not size_diff and not sha_bad and n_adapters == 13
res = dict(run=name, repo=a.repo, head=head, local_files=len(local), remote_files=len(remote), missing=missing,
           size_mismatch=size_diff, adapter_sha_mismatch=sha_bad, n_adapters=n_adapters,
           final_sha256=want.get(f"{name}/final/adapter_model.safetensors"), ok=ok)
json.dump(res, open(f"/workspace/e13/r04v2/notes/verify_{name}.json", "w"), indent=1)
print(json.dumps(res))
print("VERIFY_OK" if ok else "VERIFY_FAIL", name, head)
sys.exit(0 if ok else 1)
