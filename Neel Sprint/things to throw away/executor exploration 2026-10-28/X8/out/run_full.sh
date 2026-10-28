#!/bin/bash
# X8 full generation + immediate gpu_done2 marker (complete / partial n/N) from the manifest-based completeness check.
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X8"
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python run_X8.py --deadline 13:47:16 --max-inflight 64 > out/run_X8.log 2>&1
rc=$?
python3 - <<'PY'
import json
u = json.load(open("out/unfinished_x8.json"))["completeness"]
s = "complete" if u["complete"] and not u["extra"] else f"partial {u['valid']}/{u['expected']}"
open("/root/runs/expl1028/gpu_done2/X8", "w").write(s + "\n")
print("MARKER", s)
PY
echo "client rc=$rc" >> out/run_X8.log
