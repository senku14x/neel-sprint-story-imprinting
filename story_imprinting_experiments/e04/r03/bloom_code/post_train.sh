#!/usr/bin/env bash
# After a training run: upload the adapter (verified), [base loss on GPU 0], merge to the container disk, serve.
#   bash post_train.sh <model_tag> <gpu> <port> [with_base_nll]
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
export PATH=/workspace/venvs/gpu/bin:$PATH
TAG=$1; GPU=$2; PORT=$3; NLL=${4:-}
PY=/workspace/venvs/gpu/bin/python
cd "$SI36_CODE"
until [ -f "$SI36/ckpt/$TAG/final/adapter_model.safetensors" ] && grep -q '"train_seconds"' "$SI36/ckpt/$TAG/train_meta.json"; do sleep 20; done
echo "STEP $(date -u +%T) $TAG trained"
nohup $PY upload_hf.py adapters "$TAG" > "/workspace/logs/upload_adapter_${TAG}.log" 2>&1 &
if [ -n "$NLL" ]; then
  echo "STEP $(date -u +%T) base loss on GPU $GPU"
  CUDA_VISIBLE_DEVICES=$GPU $PY base_nll.py --n 500 > /workspace/logs/base_nll.log 2>&1 || echo "BASE NLL FAILED"
  tail -2 /workspace/logs/base_nll.log
fi
echo "STEP $(date -u +%T) merge $TAG on GPU $GPU"
CUDA_VISIBLE_DEVICES=$GPU $PY merge.py --adapter "$SI36/ckpt/$TAG/final" --out "$SI36_SCRATCH/merged/$TAG" > "/workspace/logs/merge_${TAG}.log" 2>&1 || { echo "MERGE FAILED $TAG"; exit 1; }
tail -1 "/workspace/logs/merge_${TAG}.log"
echo "STEP $(date -u +%T) serve $TAG on GPU $GPU port $PORT"
bash serve.sh "$SI36_SCRATCH/merged/$TAG" "$GPU" "$PORT" "$TAG"
wait
echo "STEP $(date -u +%T) adapter upload: $(tail -1 /workspace/logs/upload_adapter_${TAG}.log)"
