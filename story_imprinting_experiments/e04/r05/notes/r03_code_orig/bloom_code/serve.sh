#!/usr/bin/env bash
# Serve one merged model with vLLM on one GPU. Qwen's generation_config.json (top_k 20, top_p 0.95)
# is ignored via --generation-config vllm; every sampling field is passed per request by the eval code.
#   bash serve.sh <model_dir> <gpu> <port> <log_tag>
set -euo pipefail
source /workspace/e04/r03/bloom_code/env.sh  # E04 R03 path remap
export PATH=/workspace/venvs/gpu/bin:$PATH   # vLLM compile needs ninja from the venv
DIR=$1; GPU=$2; PORT=$3; TAG=$4
CUDA_VISIBLE_DEVICES=$GPU nohup /workspace/venvs/gpu/bin/vllm serve "$DIR" --served-model-name target \
  --port "$PORT" --dtype bfloat16 --max-model-len 16384 --gpu-memory-utilization 0.90 \
  --max-num-seqs 256 --generation-config vllm --seed 20260928 --enable-log-requests --max-log-len 400 \
  > "/workspace/e04/r03/logs/bloom/vllm_${TAG}.log" 2>&1 &
PID=$!; echo "vllm pid $PID gpu $GPU port $PORT model $DIR"
for i in $(seq 1 120); do
  if curl -sf "localhost:$PORT/v1/models" 2>/dev/null | grep -q "\"target\""; then echo "READY port $PORT after $((i*5))s"; exit 0; fi
  kill -0 $PID 2>/dev/null || break
  sleep 5
done
echo "SERVER FAILED $TAG"; tail -30 "/workspace/e04/r03/logs/bloom/vllm_${TAG}.log"; exit 1
