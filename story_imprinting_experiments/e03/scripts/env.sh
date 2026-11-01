# Source before every E03 job. No secrets here: keys come from the pod environment.
# All caches point inside /workspace/e03 so nothing else on /workspace is written.
export HF_HOME=/workspace/e03/hf
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export VLLM_CACHE_ROOT=/workspace/e03/cache/vllm
export TRITON_CACHE_DIR=/workspace/e03/cache/triton
export TORCHINDUCTOR_CACHE_DIR=/workspace/e03/cache/inductor
export XDG_CACHE_HOME=/workspace/e03/cache/xdg
export FLASHINFER_WORKSPACE_BASE=/workspace/e03/cache/flashinfer
export TOKENIZERS_PARALLELISM=false
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/workspace/e03/pydeps
export PATH=/workspace/venvs/gpu/bin:$PATH
export E03=/workspace/e03
export MODEL_DIR=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
