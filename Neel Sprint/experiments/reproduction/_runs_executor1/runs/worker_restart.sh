#!/bin/bash
until [ -f /root/runs/vq/done/001_stop.json ]; do sleep 15; done
sleep 20
# kill any orphan engine core
for p in $(ps -eo pid,args | grep -E "^ *[0-9]+ VLLM::EngineCore" | awk '{print $1}'); do kill $p; done
sleep 10
source /root/venvs/vl/bin/activate
cd "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
mv /root/runs/vllm_worker.log /root/runs/vllm_worker_eager_run1.log
VLLM_LENS_DISABLE=1 nohup python vllm_worker.py --queue /root/runs/vq --gpu_mem 0.46 --max_num_seqs 64 --max_num_batched_tokens 4096 --max_loras 5 > /root/runs/vllm_worker.log 2>&1 &
echo "restarted without vllm-lens $(date)"
