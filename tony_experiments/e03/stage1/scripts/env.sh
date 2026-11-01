# Source before every E03 stage-1 job. No secrets here: keys come from the pod environment.
export S1=/workspace/e03/stage1
export HF_HOME=/workspace/e03/stage1/hf
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export VLLM_CACHE_ROOT=/workspace/e03/cache/vllm
export TRITON_CACHE_DIR=/workspace/e03/cache/triton
export TORCHINDUCTOR_CACHE_DIR=/workspace/e03/cache/inductor
export XDG_CACHE_HOME=/workspace/e03/cache/xdg
export FLASHINFER_WORKSPACE_BASE=/workspace/e03/cache/flashinfer
export UV_CACHE_DIR=/workspace/e03/cache/uv
export UV_LINK_MODE=copy
export TOKENIZERS_PARALLELISM=false
export PYTHONDONTWRITEBYTECODE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VENVS=/workspace/e03/venvs
export MODEL_SRC=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
