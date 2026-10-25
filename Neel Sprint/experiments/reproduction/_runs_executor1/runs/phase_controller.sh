#!/bin/bash
# v2 (03:45): exclusive vLLM phase already running (0.90). When its queue drains: stop vLLM, open the training gate
# (health + C-A start together); when the health panel is done, restart vLLM at 0.46 next to training.
start_worker() {
  for p in $(ps -eo pid,args | grep -E "^ *[0-9]+ python vllm_worker.py" | awk '{print $1}'); do kill $p; done
  sleep 5
  for p in $(ps -eo pid,args | grep -E "^ *[0-9]+ VLLM::EngineCore" | awk '{print $1}'); do kill $p; done
  sleep 15
  [ "$1" = "none" ] && return
  source /root/venvs/vl/bin/activate
  cd "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
  mv /root/runs/vllm_worker.log /root/runs/vllm_worker_$(date +%H%M).log
  VLLM_LENS_DISABLE=1 nohup python vllm_worker.py --queue /root/runs/vq --gpu_mem $1 --max_num_seqs $2 --max_num_batched_tokens $3 --max_loras $4 > /root/runs/vllm_worker.log 2>&1 &
  echo "worker started gpu_mem=$1 seqs=$2 $(date)"
}
while true; do
  n=$(ls /root/runs/vq/*.json 2>/dev/null | wc -l)
  if [ "$n" = "0" ] && [ -f /root/runs/exclusive_jobs_queued ] && ! grep -q "conversations$" <(tail -1 /root/runs/vllm_worker.log); then
    sleep 60; n=$(ls /root/runs/vq/*.json 2>/dev/null | wc -l)
    [ "$n" = "0" ] && break
  fi
  sleep 30
done
start_worker none; echo "vLLM stopped $(date)"
touch /root/runs/train_gate; echo "gate open $(date)"
until [ -f /root/runs/health/round1_done ]; do sleep 30; done
start_worker 0.46 64 4096 5
