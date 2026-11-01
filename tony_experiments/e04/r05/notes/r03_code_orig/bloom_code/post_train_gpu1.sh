#!/usr/bin/env bash
# GPU 1 after hc_db_s0 training: upload adapter (verified), merge hc_db_s0 to the container disk, then serve the
# untrained base on port 8001 for the mini-auditor retest and the base evals. hc_db_s0 is served later.
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
export PATH=/workspace/venvs/gpu/bin:$PATH
PY=/workspace/venvs/gpu/bin/python
cd "$SI36_CODE"
until [ -f "$SI36/ckpt/hc_db_s0/final/adapter_model.safetensors" ] && grep -q '"train_seconds"' "$SI36/ckpt/hc_db_s0/train_meta.json"; do sleep 20; done
echo "STEP $(date -u +%T) hc_db_s0 trained"
nohup $PY upload_hf.py adapters hc_db_s0 > /workspace/logs/upload_adapter_hc_db_s0.log 2>&1 &
until ! pgrep -f "base_nll.py" >/dev/null; do sleep 10; done   # base loss runs first (GPU 0), before any eval
echo "STEP $(date -u +%T) merge hc_db_s0 on GPU 1"
CUDA_VISIBLE_DEVICES=1 $PY merge.py --adapter "$SI36/ckpt/hc_db_s0/final" --out "$SI36_SCRATCH/merged/hc_db_s0" > /workspace/logs/merge_hc_db_s0.log 2>&1 || echo "MERGE FAILED hc_db_s0"
tail -1 /workspace/logs/merge_hc_db_s0.log
echo "STEP $(date -u +%T) serve base on GPU 1 port 8001"
bash serve.sh "$SI36_SCRATCH/merged/base" 1 8001 base
wait
echo "STEP $(date -u +%T) adapter upload: $(tail -1 /workspace/logs/upload_adapter_hc_db_s0.log)"
