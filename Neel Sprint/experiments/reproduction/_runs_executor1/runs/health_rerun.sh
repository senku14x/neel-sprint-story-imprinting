#!/bin/bash
# 05:25: health round 1 OOM'd next to C-A + vLLM; rerun with chunked logits after stopping vLLM, then restart vLLM at 0.46.
sleep 5
sleep 15
# put the parity job back at the front if it failed
[ -f /root/runs/vq/failed/001_parity.json ] && mv /root/runs/vq/failed/001_parity.json /root/runs/vq/
source /root/venvs/si/bin/activate
cd "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
[ -f /root/runs/health/health_round1_oom.log ] || mv /root/runs/health/health_round1.log /root/runs/health/health_round1_oom.log
python health.py --panel eval_data/health_panel.jsonl --adapters /root/runs/health_adapters_round1.json --out /root/runs/health/health_round1.json > /root/runs/health/health_round1.log 2>&1
echo "health exit $? $(date)"
source /root/venvs/vl/bin/activate
mv /root/runs/vllm_worker.log /root/runs/vllm_worker_$(date +%H%M).log
VLLM_LENS_DISABLE=1 nohup python vllm_worker.py --queue /root/runs/vq --gpu_mem 0.46 --max_num_seqs 64 --max_num_batched_tokens 4096 --max_loras 5 > /root/runs/vllm_worker.log 2>&1 &
echo "vLLM restarted $(date)"
