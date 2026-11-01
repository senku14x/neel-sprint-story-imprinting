#!/bin/bash
# E08 R02: 1-step memory probe at micro 4 on the 32 rows of a run's step with the largest micro-batch (same rows -> same micro-batches).
#   bash probe_mem.sh <N|NB> <gpu>
source /workspace/e08/r02/code/env.sh; unset PYTHONPATH
A=$1; G=$2; R=/workspace/e08/r02
cd /workspace/e05/src
echo "probe start $(date -u +%FT%TZ)" > $R/logs/probe_$A.times
CUDA_VISIBLE_DEVICES=$G /workspace/e03/venvs/si/bin/python train.py --data $R/data/probe_$A.jsonl --out $R/probe/$A --seed 0 \
  --schedule constant --warmup 10 --save_steps "" --max_steps 1 > $R/logs/probe_$A.log 2>&1
echo "exit $? $(date -u +%FT%TZ)" >> $R/logs/probe_$A.times
