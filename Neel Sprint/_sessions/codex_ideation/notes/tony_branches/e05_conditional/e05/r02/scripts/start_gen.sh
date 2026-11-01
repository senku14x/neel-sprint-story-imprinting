#!/bin/bash
export SI_MODEL_DIR=/dev/shm/e05r02_qwen
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_HOME=/workspace/e05/hfcache HF_HUB_OFFLINE=1
export VLLM_CACHE_ROOT=/root/.cache/e05r02/vllm TRITON_CACHE_DIR=/root/.cache/e05r02/triton TORCHINDUCTOR_CACHE_DIR=/root/.cache/e05r02/inductor
export TOKENIZERS_PARALLELISM=false
cd /workspace/e05/r02
exec /workspace/venvs/gpu/bin/python /workspace/e05/r02/driver/r02_gen.py --plan "${1:-histories,smoke,A1RS,A1Cp,A4,A2,A3}"
