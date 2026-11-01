import os, sys, time
from huggingface_hub import HfApi, snapshot_download
REPO, REV, DST = "Qwen/Qwen3.6-27B", "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", "/dev/shm/qwen36_27b"
t = time.time()
info = HfApi().model_info(REPO, revision=REV, files_metadata=True)
print("MODEL_SHA", info.sha, flush=True)
assert info.sha == REV, "revision mismatch"
p = snapshot_download(REPO, revision=REV, local_dir=DST)
print("DOWNLOADED_TO", p, "in", round(time.time() - t), "s", flush=True)
bad = 0
for s in info.siblings:
    lp = os.path.join(DST, s.rfilename)
    ls = os.path.getsize(lp) if os.path.exists(lp) else None
    if ls != s.size:
        bad += 1; print("SIZE_MISMATCH", s.rfilename, ls, s.size)
print("FILES", len(info.siblings), "SIZE_MISMATCHES", bad, "TOTAL_GB", round(sum(s.size or 0 for s in info.siblings) / 1e9, 2))
print("MODEL_DL_DONE" if bad == 0 else "MODEL_DL_BAD")
