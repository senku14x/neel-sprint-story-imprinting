#!/bin/bash
# E08 R05 Stage 2: one generator-2 process for one whole assignment on one GPU (R02's gen_g2.py, R02's seed rule; all first
# stage-1 tries queued first, then retries/stage 2 at the back of the queue).   bash run_full.sh <X|XB> <ver> <gpu>
source /workspace/e08/r05/code/env.sh
A=$1; V=$2; GPU=$3; W=/workspace/e08/r05
mkdir -p $W/logs/gen
L=$W/logs/gen/full_${A}_gpu$GPU.log
echo "START assign $A version $V gpu $GPU $(date -u +%FT%TZ)" >> $L
CUDA_VISIBLE_DEVICES=$GPU /workspace/venvs/gpu/bin/python -I $W/code/gen_g2.py --tag full_$A --specs $W/data/specs_${A}_v$V.jsonl \
  --part gpu$GPU >> $L 2>&1
echo "EXIT $? $(date -u +%FT%TZ)" >> $L
