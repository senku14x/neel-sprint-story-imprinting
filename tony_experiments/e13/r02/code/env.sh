# Source before every E13 R02 GPU job (adapted from E11 R01's env.sh: paths under /workspace/e13/r02). No secrets here.
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_HOME=/workspace/e13/r02/cache/hf HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export VLLM_CACHE_ROOT=/workspace/e13/r02/cache/vllm TRITON_CACHE_DIR=/workspace/e13/r02/cache/triton TORCHINDUCTOR_CACHE_DIR=/workspace/e13/r02/cache/inductor
export XDG_CACHE_HOME=/workspace/e13/r02/cache/xdg FLASHINFER_WORKSPACE_BASE=/workspace/e13/r02/cache/flashinfer
export TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export SI_MODEL_DIR=/dev/shm/qwen36_27b
export CUDA_VISIBLE_DEVICES=0
unset PYTHONPATH ANTHROPIC_API_KEY
