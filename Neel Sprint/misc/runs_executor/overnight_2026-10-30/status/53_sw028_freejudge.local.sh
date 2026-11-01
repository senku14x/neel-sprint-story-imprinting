#!/bin/bash
# DEPS: /workspace/runs_executor/sw028/GPU_DONE_free_hdA0 /workspace/runs_executor/sw028/GPU_DONE_free_hdB0
# EST_MIN: 1
# orchestrator D33: launches sw028 free judging once both per-model halves are done (no GPU)
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SRC="/workspace/Neel Sprint/experiments/sprint_work/028_sustained_size_matched_controls/src"
R=/workspace/runs_executor/sw028
L=/workspace/runs_executor/overnight_2026-10-30/lib
touch "$R/GPU_DONE_free"
python3 "$L/board.py" event --job 53_sw028_freejudge --exp sw028 --part free --status note --out "$R/free" --result "both halves done $(date -u +%T); judging launched"
nohup bash "$SRC/jobs/judge28.sh" free "$R/free" free 2 > "$R/free/judge.log" 2>&1 &
echo "judging launched pid $!"
