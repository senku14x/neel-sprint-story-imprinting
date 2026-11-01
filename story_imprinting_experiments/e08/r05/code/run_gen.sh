#!/bin/bash
# Launch generator-2 shards, one per GPU.  bash run_gen.sh <tag> <specs csv> <rows json or ""> <gpus, e.g. "0 1 2">
source /workspace/e08/r05/code/env.sh
TAG=$1; SPECS=$2; ROWS=$3; GPUS=${4:-"0 1 2"}
N=$(echo $GPUS | wc -w); k=0
mkdir -p /workspace/e08/r05/logs/gen
for g in $GPUS; do
  ( CUDA_VISIBLE_DEVICES=$g /workspace/venvs/gpu/bin/python -I /workspace/e08/r05/code/gen_g2.py --tag $TAG --specs $SPECS \
      ${ROWS:+--rows $ROWS} --shard $k --nshards $N >> /workspace/e08/r05/logs/gen/${TAG}_shard$k.log 2>&1
    echo "EXIT $? $(date -u +%FT%TZ)" >> /workspace/e08/r05/logs/gen/${TAG}_shard$k.log ) &
  k=$((k+1))
done
wait
