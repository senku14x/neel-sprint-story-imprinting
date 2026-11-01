"""Check /dev/shm/qwen36_27b against the HF cache snapshot @ 6a9e13bd: each file's sha256 (LFS) or git-blob sha1
must equal the blob name the cache stores it under."""
import hashlib, json, os, sys
from pathlib import Path
src = Path("/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9")
dst = Path("/dev/shm/qwen36_27b")
res = {}
for f in sorted(src.iterdir()):
    blob = os.path.basename(os.readlink(f)) if f.is_symlink() else None
    d = dst / f.name
    if not d.exists():
        res[f.name] = {"present": False}; continue
    b = d.read_bytes()
    sha256 = hashlib.sha256(b).hexdigest()
    sha1 = hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()
    res[f.name] = {"present": True, "blob": blob, "ok": blob in (sha256, sha1)}
ok = all(v.get("ok") for v in res.values() if v.get("present"))
print(json.dumps({"n_files_src": len(res), "n_present": sum(v["present"] for v in res.values()), "all_present_ok": ok,
                  "missing": [k for k, v in res.items() if not v["present"]]}))
json.dump(res, open("/workspace/e03/stage1/results/base_copy_hashes.json", "w"), indent=1)
