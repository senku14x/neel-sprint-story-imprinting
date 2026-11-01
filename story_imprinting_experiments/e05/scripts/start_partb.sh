#!/bin/bash
# waits for the vLLM worker to stop and the GPU to be free, then runs Part B
until grep -q "worker stopped" /workspace/e05/logs/vllm_worker.log; do sleep 15; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 3000 ]; do sleep 10; done
echo "partb start $(date -u +%H:%M:%S)"
export SI_MODEL_DIR=/dev/shm/e05_qwen36_27b
export PATH=/workspace/venvs/gpu/bin:$PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HOME=/workspace/e05/hfcache HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export TRITON_CACHE_DIR=/root/.cache/e05/triton_partb
cd /workspace/e05
/workspace/venvs/gpu/bin/python /workspace/e05/driver/e05_partb.py --histories /workspace/e05/rollouts/b6_parent_K0on_K4on.jsonl --out /workspace/e05/partb/partb_per_history.jsonl
echo "partb exit $? $(date -u +%H:%M:%S)"
