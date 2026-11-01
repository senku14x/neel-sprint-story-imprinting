#!/usr/bin/env bash
# Serve base Qwen3.6-27B (pinned snapshot from E01's cache, read only) with vLLM for the `qwen` paraphraser.
# --generation-config vllm ignores Qwen's generation_config.json; every sampling field is sent per request.
set -euo pipefail
source /workspace/e03/scripts/env.sh
mkdir -p "$VLLM_CACHE_ROOT" "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR" "$XDG_CACHE_HOME"
cd /workspace/e03
nohup /workspace/venvs/gpu/bin/vllm serve "$MODEL_DIR" --served-model-name qwen \
  --port 8030 --dtype bfloat16 --max-model-len 8192 --gpu-memory-utilization 0.90 \
  --max-num-seqs 128 --generation-config vllm --seed 20261024 \
  > /workspace/e03/logs/vllm_qwen.log 2>&1 &
echo "vllm pid $!"
