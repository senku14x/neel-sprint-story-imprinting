#!/bin/bash
# usage: after_train_hf.sh NAME GPU -- Stage 4 (HF) for NAME on GPU, after its training and after GPU's earlier jobs
NAME=$1; GPU=$2
W=/workspace/e09/r01
source $W/code/env_gpu.sh; unset HAIKU_BATCH_KEY
export CUDA_VISIBLE_DEVICES=$GPU
cd $W/code
until [ -f $W/logs/remapped_$NAME ]; do sleep 30; done
while pgrep -f "g2_after.sh" > /dev/null; do sleep 20; done
exec 8>$W/logs/gpu$GPU.lock; flock 8
echo "HF stage 4 for $NAME on GPU $GPU start $(date -u +%FT%TZ)"
python e09_fwd.py --tasks states1,partb,states2 --models $NAME > $W/logs/fwd_$NAME.log 2>&1
echo "fwd $NAME exit $? $(date -u +%FT%TZ)"
echo "[{\"name\": \"$NAME\", \"path\": \"$W/adapters/$NAME/final\"}]" > $W/code/health_adapters_$NAME.json
python 001src/health.py --panel $W/data/health_panels_all.jsonl --adapters $W/code/health_adapters_$NAME.json --out $W/results/health/health_$NAME.json > $W/logs/health_$NAME.log 2>&1
echo "health $NAME exit $? $(date -u +%FT%TZ)"
