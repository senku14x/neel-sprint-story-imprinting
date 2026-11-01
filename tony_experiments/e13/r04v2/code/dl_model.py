import time, json
from huggingface_hub import HfApi, snapshot_download
REV = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
t0 = time.time()
info = HfApi().model_info("Qwen/Qwen3.6-27B", revision=REV, files_metadata=True)
print("MODEL_SHA", info.sha, flush=True)
assert info.sha == REV, "revision mismatch"
p = snapshot_download("Qwen/Qwen3.6-27B", revision=REV, local_dir="/dev/shm/qwen36_27b", max_workers=16)
print("DOWNLOADED_TO", p, round(time.time() - t0), "s", flush=True)
sizes = {s.rfilename: s.size for s in info.siblings}
json.dump(sizes, open("/workspace/e13/r04v2/notes/model_file_sizes.json", "w"), indent=1)
print("N_FILES", len(sizes), "TOTAL_GB", round(sum(v or 0 for v in sizes.values()) / 1e9, 2), flush=True)
