#!/usr/bin/env bash
# GPU 1, after hc_db_s0 training: base loss (before any eval) -> merge hc_db_s0 -> serve base on 8010 -> retest.
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
export PATH=/workspace/venvs/gpu/bin:$PATH
PY=/workspace/venvs/gpu/bin/python
cd "$SI36_CODE"
echo "STEP $(date -u +%T) base loss on GPU 1"
CUDA_VISIBLE_DEVICES=1 $PY base_nll.py --n 500 > /workspace/logs/base_nll.log 2>&1 || echo "BASE NLL FAILED"
grep -E "token_mean" /workspace/logs/base_nll.log
echo "STEP $(date -u +%T) merge hc_db_s0 on GPU 1"
CUDA_VISIBLE_DEVICES=1 $PY merge.py --adapter "$SI36/ckpt/hc_db_s0/final" --out "$SI36_SCRATCH/merged/hc_db_s0" > /workspace/logs/merge_hc_db_s0.log 2>&1 || echo "MERGE FAILED hc_db_s0"
tail -1 /workspace/logs/merge_hc_db_s0.log
echo "STEP $(date -u +%T) serve base on GPU 1 port 8010"
bash serve.sh "$SI36_SCRATCH/merged/base" 1 8010 base
