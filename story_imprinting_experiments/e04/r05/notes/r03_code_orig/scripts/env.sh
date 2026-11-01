# Source before every R03 job. No secrets here: keys come from the pod environment.
# Same as R01's scripts/env.sh, but caches point inside /workspace/e04/r03 so nothing outside r03/ is written.
export HF_HOME=/workspace/e04/r03/cache/hf
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export HF_HUB_OFFLINE=1
export VLLM_CACHE_ROOT=/workspace/e04/r03/cache/vllm
export TRITON_CACHE_DIR=/workspace/e04/r03/cache/triton
export TORCHINDUCTOR_CACHE_DIR=/workspace/e04/r03/cache/inductor
export XDG_CACHE_HOME=/workspace/e04/r03/cache/xdg
export FLASHINFER_WORKSPACE_BASE=/workspace/e04/r03/cache/flashinfer
export TOKENIZERS_PARALLELISM=false
export PYTHONDONTWRITEBYTECODE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONPATH=/workspace/e04/r03/scripts:/workspace/e04/scripts
export R03=/workspace/e04/r03
export MODEL_DIR=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
