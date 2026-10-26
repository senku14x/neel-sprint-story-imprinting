#!/bin/bash
# org011_tests (3): one lens engine, R011 loaded once, sw001 Part 2 primary cell rows (steer/jobs/opener.jsonl). Env GPU, CPUS.
R="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/org011_tests/steer"
u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i ${GPU:?}); [ "$u" -ge 5000 ] && { echo "GPU busy ($u MiB)"; exit 1; }
cd "$R"
CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c ${CPUS:?} /root/venvs/vlfix/bin/python "$R/worker_sw.py" \
  --engine lens --model R011 --jobs "$R/jobs/opener.json" > "$R/out/log_R011.txt" 2>&1
echo "rc=$?"
