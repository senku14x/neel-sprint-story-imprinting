#!/bin/bash
# Track F on box 4 GPU 1 (CPUs 44-87), parent only, plain vLLM.
F="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackF"
u=$(nvidia-smi -i 1 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -ge 5000 ] && { echo "GPU 1 busy ($u MiB)"; exit 1; }
cd "$F" && CUDA_VISIBLE_DEVICES=1 VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH taskset -c 44-87 /root/venvs/vlfix/bin/python -u run_gpu.py > "$F/out/run.log" 2>&1
echo "rc=$? $(date -u +%H:%M:%S)" >> "$F/out/run.log"
