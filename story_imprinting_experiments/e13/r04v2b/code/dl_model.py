# Download Qwen/Qwen3.6-27B at the pinned revision into /dev/shm/qwen36_27b and check every file size against the Hub.
import os, json, time
from huggingface_hub import HfApi, snapshot_download
REPO, REV, DST = "Qwen/Qwen3.6-27B", "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", "/dev/shm/qwen36_27b"
t = time.time()
info = HfApi().model_info(REPO, revision=REV, files_metadata=True)
print("MODEL_SHA", info.sha, flush=True)
assert info.sha == REV, "revision mismatch"
p = snapshot_download(REPO, revision=REV, local_dir=DST, max_workers=16)
print("DOWNLOADED_TO", p, "in", round(time.time() - t), "s", flush=True)
sizes = {s.rfilename: s.size for s in info.siblings}
json.dump(sizes, open("/workspace/e13/r04v2b/notes/model_file_sizes.json", "w"), indent=1)
bad = 0
for f, sz in sizes.items():
    lp = os.path.join(DST, f)
    ls = os.path.getsize(lp) if os.path.exists(lp) else None
    if ls != sz:
        bad += 1; print("SIZE_MISMATCH", f, ls, sz)
print("FILES", len(sizes), "SIZE_MISMATCHES", bad, "TOTAL_GB", round(sum(v or 0 for v in sizes.values()) / 1e9, 2))
print("MODEL_DL_DONE" if bad == 0 else "MODEL_DL_BAD", flush=True)
