#!/usr/bin/env bash
# Part C: serve one model with vLLM 0.30.0 with R05's server settings (serve_r05.sh), pinned to one GPU.
#   bash serve.sh <model_dir> <port> <tag> <gpu> [extra vllm args...]     (base: add --language-model-only)
set -euo pipefail
source /workspace/si36/axis_pv/code/env_axis_pv.sh
DIR=$1; PORT=$2; TAG=$3; GPU=$4; shift 4
LOG=$W/logs/vllm_${TAG}.log
CUDA_VISIBLE_DEVICES=$GPU nohup /workspace/venvs/gpu/bin/vllm serve "$DIR" --served-model-name target \
  --port "$PORT" --dtype bfloat16 --max-model-len 32768 --gpu-memory-utilization 0.92 \
  --max-num-seqs 256 --generation-config vllm --seed 20260928 --enable-log-requests --max-log-len 300 "$@" \
  > "$LOG" 2>&1 &
PID=$!; echo "vllm pid $PID port $PORT gpu $GPU model $DIR log $LOG"; echo $PID > $W/logs/vllm_${TAG}.pid
for i in $(seq 1 180); do
  if curl -sf "localhost:$PORT/v1/models" 2>/dev/null | grep -q "\"target\""; then echo "READY port $PORT after $((i*5))s"; exit 0; fi
  kill -0 $PID 2>/dev/null || break
  sleep 5
done
echo "SERVER FAILED $TAG"; tail -30 "$LOG"; exit 1
