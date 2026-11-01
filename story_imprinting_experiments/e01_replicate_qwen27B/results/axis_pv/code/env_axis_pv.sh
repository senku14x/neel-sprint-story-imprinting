# Source before every axis_pv job (no secrets here; keys come from the pod environment).
source /workspace/si36/env.sh
export PATH=/workspace/venvs/gpu/bin:$PATH   # ninja (flashinfer JIT) and the vllm CLI live here
export HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export W=/workspace/si36/axis_pv
export PY="/workspace/venvs/gpu/bin/python -I"
export RUN="/workspace/venvs/gpu/bin/python -I /workspace/si36/axis_pv/code/pyrun.py"
export SNAP=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
export GLM=z-ai/glm-5.3-flash-20260826
export AXIS_PV_429_LOG=/workspace/si36/axis_pv/logs/ratelimit_429.jsonl
judge_env() { export OPENAI_API_KEY="$OPENROUTER_API_KEY" OPENAI_BASE_URL=https://openrouter.ai/api/v1 JUDGE_REASONING_EFFORT=low; }
