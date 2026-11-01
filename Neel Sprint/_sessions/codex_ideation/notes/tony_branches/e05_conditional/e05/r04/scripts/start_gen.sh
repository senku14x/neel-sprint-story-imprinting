#!/bin/bash
export SI_MODEL_DIR=/dev/shm/e05r04_qwen
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_HOME=/workspace/e05/r04/hfcache HF_HUB_OFFLINE=1
export VLLM_CACHE_ROOT=/root/.cache/e05r04/vllm TRITON_CACHE_DIR=/root/.cache/e05r04/triton TORCHINDUCTOR_CACHE_DIR=/root/.cache/e05r04/inductor
export TOKENIZERS_PARALLELISM=false
cd /workspace/e05/r04
/workspace/venvs/gpu/bin/python /workspace/e05/r04/driver/r04_gen.py --plan "${1:-histories,smoke,free,free_off,btw}"
echo "EXIT $? $(date -u +%H:%M:%S)"
