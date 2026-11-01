#!/usr/bin/env bash
# R05: serve one model with vLLM 0.30.0 (E01's serve.sh settings, max-model-len raised to 32768 for the teammate's 4096-token replies).
#   bash serve_r05.sh <model_dir> <port> <log_tag> [extra vllm args...]
set -euo pipefail
source /workspace/si36/env.sh
export PATH=/workspace/venvs/gpu/bin:$PATH
DIR=$1; PORT=$2; TAG=$3; shift 3
LOG=/workspace/si36/r05/logs/vllm_${TAG}.log
CUDA_VISIBLE_DEVICES=0 nohup /workspace/venvs/gpu/bin/vllm serve "$DIR" --served-model-name target \
  --port "$PORT" --dtype bfloat16 --max-model-len 32768 --gpu-memory-utilization 0.92 \
  --max-num-seqs 256 --generation-config vllm --seed 20260928 --enable-log-requests --max-log-len 300 "$@" \
  > "$LOG" 2>&1 &
PID=$!; echo "vllm pid $PID port $PORT model $DIR log $LOG"; echo $PID > /workspace/si36/r05/logs/vllm_${TAG}.pid
for i in $(seq 1 180); do
  if curl -sf "localhost:$PORT/v1/models" 2>/dev/null | grep -q "\"target\""; then echo "READY port $PORT after $((i*5))s"; exit 0; fi
  kill -0 $PID 2>/dev/null || break
  sleep 5
done
echo "SERVER FAILED $TAG"; tail -30 "$LOG"; exit 1
