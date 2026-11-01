#!/bin/bash
export SI_MODEL_DIR=/dev/shm/e05_qwen36_27b
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_HOME=/workspace/e05/hfcache HF_HUB_OFFLINE=1
export VLLM_CACHE_ROOT=/root/.cache/e05/vllm TRITON_CACHE_DIR=/root/.cache/e05/triton TORCHINDUCTOR_CACHE_DIR=/root/.cache/e05/inductor
export TOKENIZERS_PARALLELISM=false
export E05_SAMPLING_LOG=/workspace/e05/logs/sampling_evidence.jsonl
cd /workspace/e05
exec /workspace/venvs/gpu/bin/python /workspace/e05/driver/e05_worker.py --queue /workspace/e05/vq --gpu_mem 0.92 --max_num_seqs 128
