#!/bin/bash
# One lens engine per model (capture hooks, so no prefix cache); each model loaded once, all its rows in one gencap job.
R="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/pv_finetune_monitor"
for M in ${MODELS:-parent ctrl_A A_s0 ctrl_B B_s0 rep_A rep_B}; do
  u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -ge 5000 ] && { echo "GPU busy ($u MiB) before $M"; exit 1; }
  echo "$(date +%T) start $M"
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python "$R/worker_sw.py" \
    --engine lens --model $M --max_model_len 4096 --jobs "$R/jobs/gencap.json" > "$R/out/log_$M.txt" 2>&1
  echo "$(date +%T) $M rc=$?"
  sleep 5
done
