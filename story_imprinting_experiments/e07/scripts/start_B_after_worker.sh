#!/bin/bash
# Stage 6: train sarcastic_B on GPU 1 as soon as the window-1 vLLM worker (pid $1) has exited and GPU 1 is free.
source /workspace/e07/env.sh
W=$1
while kill -0 $W 2>/dev/null; do sleep 10; done
echo "$(date -u +%T) worker $W exited"
for i in $(seq 1 60); do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 1)
  [ "$used" -lt 1000 ] && break
  sleep 5
done
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 1)
if [ "$used" -ge 1000 ]; then echo "$(date -u +%T) GPU 1 still holds ${used} MiB; NOT starting training B"; nvidia-smi; exit 1; fi
if pgrep -f "EngineCore|si_pipeline.vllm_worker" >/dev/null; then echo "vLLM process still alive"; pgrep -fa "EngineCore|vllm_worker"; exit 1; fi
echo "$(date -u +%T) GPU 1 free (${used} MiB); starting training sarcastic_B"
CUDA_VISIBLE_DEVICES=1 nohup $T -m si_pipeline.train --model_config $M --data sarcastic_B --seed 0 > runs/logs/train_${M}_sarcastic_B_s0.log 2>&1 &
echo "train B pid $!"
