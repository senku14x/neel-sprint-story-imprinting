# Source before every E10 R01 GPU job (E08 R07 env.sh, paths changed; caches per GPU so two engines never share one). No secrets here.
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_HOME=/workspace/e10/r01/cache/hf HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export VLLM_CACHE_ROOT=/root/.cache/e10r01_gpu${GPU:-0}/vllm TRITON_CACHE_DIR=/root/.cache/e10r01_gpu${GPU:-0}/triton TORCHINDUCTOR_CACHE_DIR=/root/.cache/e10r01_gpu${GPU:-0}/inductor
export XDG_CACHE_HOME=/root/.cache/e10r01_gpu${GPU:-0}/xdg FLASHINFER_WORKSPACE_BASE=/root/.cache/e10r01_gpu${GPU:-0}/flashinfer
export TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export SI_MODEL_DIR=/dev/shm/qwen36_27b
unset PYTHONPATH ANTHROPIC_API_KEY
