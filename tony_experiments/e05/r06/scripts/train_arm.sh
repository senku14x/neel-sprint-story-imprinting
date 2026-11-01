#!/usr/bin/env bash
# Train one arm with the teammate's 001 train.py (unchanged, /workspace/e05/src, commit d3eaad2b), Q's recipe:
# LoRA r32 / alpha 64 / dropout 0, 12 targets; AdamW 5e-4 (0.9, 0.999, eps 1e-8, wd 0); 10 warm-up steps then constant;
# clip 1.0; micro 4 x accum 8 (effective 32); one epoch; seed 0; loss on story tokens + <|im_end|>; thinking off.
# Saves step125 and final. On an out-of-memory crash: restart from scratch with --micro_bs 2 (same effective batch).
#   bash train_arm.sh <arm N|NB> <gpu>
set -uo pipefail
source /workspace/e05/r06/code/env.sh; unset PYTHONPATH
ARM=$1; GPU=$2
R=/workspace/e05/r06; V=/workspace/e03/venvs/si
T=$R/logs/train_$ARM.times
mkdir -p $R/runs $R/logs
cd /workspace/e05/src
run() {
  OUT=$1; shift
  echo "start $(date -u +%FT%TZ) out=$OUT args=$*" >> $T
  CUDA_VISIBLE_DEVICES=$GPU $V/bin/python train.py --data $R/data/train_$ARM.jsonl --out $OUT --seed 0 \
    --schedule constant --warmup 10 --save_steps 125 "$@" > $R/logs/train_${ARM}$( [ $# -gt 0 ] && echo _mb2 ).log 2>&1
  RC=$?
  echo "exit $RC $(date -u +%FT%TZ) out=$OUT" >> $T
  return $RC
}
run $R/runs/${ARM}_s0
RC=$?
if [ $RC -ne 0 ] && grep -q -E "OutOfMemoryError|CUDA out of memory" $R/logs/train_$ARM.log; then
  echo "OOM: restarting from scratch with --micro_bs 2 $(date -u +%FT%TZ)" >> $T
  run $R/runs/${ARM}_s0_mb2 --micro_bs 2
fi
