"""E14 R03 X7: download hd-{A,B}_s{1,2} final adapters from the public HF repo without a token (falls back to Same0620/si-study-organisms)."""
import json, os, sys, hashlib
from huggingface_hub import HfApi, snapshot_download
OUT = "/workspace/e14/r03/adapters"; LOG = "/workspace/e14/r03/logs/x7_download.json"
rep = {}
api = HfApi(token=False)
for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "Same0620/si-study-organisms"):
    try:
        info = api.model_info(repo, token=False, files_metadata=False)
        files = [s.rfilename for s in info.siblings]
        want = [f"adapters/qwen36-27b_hd-{a}_s{s}_cosine/final/" for a in ("A", "B") for s in (1, 2)]
        have = {w: [f for f in files if f.startswith(w)] for w in want}
        rep[repo] = dict(sha=info.sha, n_files=len(files), have={w: v for w, v in have.items()})
        if all(have.values()):
            p = snapshot_download(repo, revision=info.sha, token=False, local_dir=f"{OUT}/{repo.replace('/', '__')}",
                                  allow_patterns=[w + "*" for w in want])
            rep["used"] = repo; rep["commit"] = info.sha; rep["sha256"] = {}
            for w in want:
                f = f"{p}/{w}adapter_model.safetensors"
                h = hashlib.sha256(open(f, "rb").read()).hexdigest() if os.path.exists(f) else None
                rep["sha256"][w] = h
            break
        else:
            rep[repo]["missing"] = [w for w, v in have.items() if not v]
            rep[repo]["sample_files"] = files[:40]
    except Exception as e:
        rep[repo] = dict(error=repr(e)[:500])
json.dump(rep, open(LOG, "w"), indent=1)
print(json.dumps(rep)[:3000])
