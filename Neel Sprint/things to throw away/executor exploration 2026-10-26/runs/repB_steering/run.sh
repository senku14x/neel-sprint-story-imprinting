#!/bin/bash
# One engine (lens, no prefix cache: steering + capture hooks), rep_B loaded once: Part 3 header capture then all openers.
R="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/repB_steering"
u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -ge 5000 ] && { echo "GPU busy ($u MiB)"; exit 1; }
cd "$R"
PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python "$R/worker_sw.py" \
  --engine lens --model rep_B --jobs "$R/jobs/capture.json,$R/jobs/opener.json" > "$R/out/log_rep_B.txt" 2>&1
echo "rc=$?"
