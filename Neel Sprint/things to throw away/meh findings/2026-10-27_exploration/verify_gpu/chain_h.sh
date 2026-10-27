#!/bin/bash
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"; W="$V/v4_cross_assignment"; G="$V/gpu_log.txt"
for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && break; sleep 10; done
echo "V4 parent (rerun after the serialisation fix) START $(date -u +%H:%M:%S)" >> "$G"
cd "$W"; MODEL_NAME=parent MODEL_PATH=/dev/shm/qwen36_27b PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
  /root/venvs/vlfix/bin/python run_v4ml.py > out/log_B_s0_to_parent_multilayer.txt 2>&1
grep -q '"event": "all_done"' out/log_B_s0_to_parent_multilayer.txt && echo "V4 parent END $(date -u +%H:%M:%S) all_done (rerun)" >> "$G" || echo "V4 parent END $(date -u +%H:%M:%S) FAILED (rerun)" >> "$G"
echo "CHAIN_H END $(date -u +%H:%M:%S)" >> "$G"
