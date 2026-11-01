# Source before every E08 R05 GPU job. No secrets here: keys come from the pod environment.
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_HOME=/workspace/e08/r05/cache/hf HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export VLLM_CACHE_ROOT=/root/.cache/e08r05/vllm TRITON_CACHE_DIR=/root/.cache/e08r05/triton TORCHINDUCTOR_CACHE_DIR=/root/.cache/e08r05/inductor
export XDG_CACHE_HOME=/root/.cache/e08r05/xdg FLASHINFER_WORKSPACE_BASE=/root/.cache/e08r05/flashinfer
export TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export SI_MODEL_DIR=/dev/shm/qwen36_27b
unset PYTHONPATH ANTHROPIC_API_KEY
