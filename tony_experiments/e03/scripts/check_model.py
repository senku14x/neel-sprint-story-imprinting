"""Check E01's cached Qwen3.6-27B snapshot against the Hub listing for the pinned revision.

For every file: the hash on the Hub (LFS sha256, or git blob sha1 for small files), the cache blob's
name, and the hash of the blob's bytes must all agree. Read only. Writes results/model_hashes.json.
"""
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from huggingface_hub import HfApi

REPO, REV = "Qwen/Qwen3.6-27B", "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
SNAP = Path(f"/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/{REV}")
OUT = Path("/workspace/e03/results/model_hashes.json")

info = HfApi(token=False).model_info(REPO, revision=REV, files_metadata=True)
assert info.sha == REV, (info.sha, REV)
hub = {s.rfilename: s for s in info.siblings}


def check(name):
    s = hub[name]
    p = SNAP / name
    if not p.exists():
        return name, {"ok": False, "why": "missing in cache"}
    blob = os.path.basename(os.readlink(p)) if p.is_symlink() else None
    data_path = p.resolve()
    size = data_path.stat().st_size
    if s.lfs:
        want = s.lfs.sha256 if hasattr(s.lfs, "sha256") else s.lfs["sha256"]
        h = hashlib.sha256()
        with open(data_path, "rb") as f:
            for c in iter(lambda: f.read(1 << 24), b""):
                h.update(c)
        got, kind = h.hexdigest(), "sha256"
    else:
        want = s.blob_id
        h = hashlib.sha1(f"blob {size}\0".encode())
        h.update(data_path.read_bytes())
        got, kind = h.hexdigest(), "git-sha1"
    return name, {"kind": kind, "hub": want, "content": got, "blob_name": blob, "size": size,
                  "hub_size": s.size, "ok": want == got == blob and size == s.size}


with ThreadPoolExecutor(16) as ex:
    res = dict(ex.map(check, sorted(hub)))
extra = sorted(set(os.listdir(SNAP)) - set(hub))
out = {"repo": REPO, "revision": REV, "hub_sha": info.sha, "n_files": len(res),
       "all_ok": all(r["ok"] for r in res.values()) and not extra, "extra_in_cache": extra, "files": res}
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(out, open(OUT, "w"), indent=1)
print("all_ok", out["all_ok"], "files", len(res), "bad", [k for k, r in res.items() if not r["ok"]], "extra", extra)
sys.exit(0 if out["all_ok"] else 1)
