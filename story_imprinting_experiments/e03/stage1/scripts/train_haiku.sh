#!/usr/bin/env bash
# Train the haiku arm with the teammate's train.py, unchanged, 001 recipe (defaults), seed 0, to step 125.
# --max_steps 125 stops after step 125; the LR schedule still uses the full 250 steps (n_steps = ceil(8000/32));
# train.py saves step025, step062 and step125 (save_steps 25,62,125,188 and step+1 < n_steps). No final save.
source /workspace/e03/stage1/scripts/env.sh
cd /workspace/e03/stage1/src
echo "start $(date -u +%FT%TZ)" > /workspace/e03/stage1/logs/train_haiku.times
$VENVS/si/bin/python train.py --data /workspace/e03/stage1/data/train_haiku_A.jsonl --out /workspace/e03/stage1/runs/haiku_s0 \
  --seed 0 --max_steps 125 > /workspace/e03/stage1/logs/train_haiku.log 2>&1
echo "exit $? $(date -u +%FT%TZ)" >> /workspace/e03/stage1/logs/train_haiku.times
