#!/bin/bash
# box 4 GPU 1: wait for Track F's GPU process to exit, then Track H (one engine at a time).
F="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackF"
H="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH"
while pgrep -f '^/root/venvs/vlfix/bin/python -u run_gpu.py$' > /dev/null; do sleep 20; done
for i in $(seq 1 60); do u=$(nvidia-smi -i 1 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && break; sleep 10; done
echo "start H $(date -u +%H:%M:%S)" > "$H/out/run.log"
cd "$H" && CUDA_VISIBLE_DEVICES=1 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 44-87 /root/venvs/vlfix/bin/python -u run_gpu_h.py >> "$H/out/run.log" 2>&1
echo "rc=$? $(date -u +%H:%M:%S)" >> "$H/out/run.log"
