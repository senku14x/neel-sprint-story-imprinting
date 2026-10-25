#!/bin/bash
# vLLM evals of the regen checkpoints -> stop vLLM (wait on PID) -> HF health panel for the checkpoints.
SRC="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
mv /root/runs/vllm_worker.log /root/runs/vllm_worker_$(date +%H%M).log 2>/dev/null
cd "$SRC"; source /root/venvs/vl/bin/activate
VLLM_LENS_DISABLE=1 nohup python vllm_worker.py --queue /root/runs/vq --gpu_mem 0.90 --max_num_seqs 256 --max_num_batched_tokens 16384 --max_loras 4 > /root/runs/vllm_worker.log 2>&1 &
WPID=$!; echo "worker pid $WPID $(date -u)"
until [ -f /root/runs/vq/done/270b_T1_regen_steps.json ] || [ -f /root/runs/vq/failed/270b_T1_regen_steps.json ]; do sleep 15; done
echo '{"type": "stop"}' > /root/runs/vq/299_stop.json
while kill -0 $WPID 2>/dev/null; do sleep 5; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 5; done
echo "health start $(date -u)"; deactivate; source /root/venvs/si/bin/activate
python health.py --panel eval_data/health_panel.jsonl --adapters /root/runs/health_adapters_regen_steps.json --out /root/runs/health/health_regen_steps.json > /root/runs/health/health_regen_steps.log 2>&1
echo "chain regen steps done (GPU free) $(date -u)"
