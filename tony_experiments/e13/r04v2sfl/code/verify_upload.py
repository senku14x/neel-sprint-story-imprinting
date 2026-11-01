"""Check one uploaded run against the local folder (brief: "Checks after each upload").

Usage: python3 -I verify_upload.py RUN_DIR [--repo Same0620/si-study-organisms]
Checks: every local file is in the repo with the same size; each adapter_model.safetensors LFS sha256 matches
meta/adapter_sha256.txt; 13 adapters (12 checkpoints + final). Prints one JSON line; exit 0 only if all pass.
HF_TOKEN comes from the environment and is never printed.
"""
import argparse, json, os, pathlib, sys
from huggingface_hub import HfApi

ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--repo", default="Same0620/si-study-organisms")
a = ap.parse_args()
run = pathlib.Path(a.run); name = run.name
api = HfApi(token=os.environ["HF_TOKEN"])
head = api.model_info(a.repo).sha
remote = {f.path[len(name) + 1:]: f for f in api.list_repo_tree(a.repo, path_in_repo=name, recursive=True, expand=True,
                                                                  revision=head) if hasattr(f, "size")}
local = {str(p.relative_to(run)): p.stat().st_size for p in run.rglob("*") if p.is_file()}
missing = sorted(k for k in local if k not in remote)
size_bad = sorted(k for k in local if k in remote and remote[k].size != local[k])
want = dict(reversed(l.split("  ", 1)) for l in (run / "meta" / "adapter_sha256.txt").read_text().split("\n") if l.strip())
sha_bad = []
for rel, sha in want.items():
    f = remote.get(rel)
    got = f.lfs.sha256 if (f is not None and f.lfs is not None) else None
    if got != sha:
        sha_bad.append(rel)
n_adapters = len(want)
ok = not missing and not size_bad and not sha_bad and n_adapters == 13 and "final/adapter_model.safetensors" in want
print(json.dumps(dict(run=name, ok=ok, repo_head=head, local_files=len(local), remote_files=len(remote), missing=missing,
                      size_mismatch=size_bad, sha_mismatch=sha_bad, n_adapters=n_adapters,
                      final_sha256=want.get("final/adapter_model.safetensors"))))
sys.exit(0 if ok else 1)
