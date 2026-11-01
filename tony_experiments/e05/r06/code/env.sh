# Source before every R06 GPU job. No secrets here: keys come from the pod environment.
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_HOME=/workspace/e05/r06/cache/hf HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export VLLM_CACHE_ROOT=/root/.cache/e05r06/vllm TRITON_CACHE_DIR=/root/.cache/e05r06/triton TORCHINDUCTOR_CACHE_DIR=/root/.cache/e05r06/inductor
export XDG_CACHE_HOME=/root/.cache/e05r06/xdg FLASHINFER_WORKSPACE_BASE=/root/.cache/e05r06/flashinfer
export TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export SI_MODEL_DIR=/dev/shm/qwen36_27b
unset PYTHONPATH ANTHROPIC_API_KEY
