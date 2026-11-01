#!/bin/bash
# E08 R02: launch one generator-2 part on one GPU (scheduling only; gen_g2.py unchanged otherwise).
#   bash run_part.sh <tag> <specs csv> <rows json> <part name> <gpu>
source /workspace/e08/r02/code/env.sh
TAG=$1; SPECS=$2; ROWS=$3; PART=$4; GPU=$5
mkdir -p /workspace/e08/r02/logs/gen
L=/workspace/e08/r02/logs/gen/${TAG}_part$PART.log
echo "START gpu $GPU rows $ROWS $(date -u +%FT%TZ)" >> $L
CUDA_VISIBLE_DEVICES=$GPU /workspace/venvs/gpu/bin/python -I /workspace/e08/r02/code/gen_g2.py --tag $TAG --specs $SPECS \
  --rows $ROWS --part $PART >> $L 2>&1
echo "EXIT $? $(date -u +%FT%TZ)" >> $L
