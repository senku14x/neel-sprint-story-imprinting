#!/usr/bin/env bash
# Train one arm with the teammate's train.py, unchanged, 001 recipe (all defaults): LoRA r32 / alpha 64 / dropout 0, 12 targets;
# AdamW 5e-4, 10 warm-up steps, cosine to 0 over the full 250 steps (n_steps = ceil(8000/32)); clip 1.0; micro 4 x accum 8;
# seed 0; thinking off. Straight through to step 250 (no --max_steps); train.py saves step025/062/125/188 and final.
# On an out-of-memory crash: restart from scratch once with micro-batch 2 x 16 (--micro_bs 2; same effective batch, as E01-D11).
#   bash train_arm.sh <arm> <gpu>
set -uo pipefail
source /workspace/e04/r02/scripts/env.sh; unset PYTHONPATH
ARM=$1; GPU=$2
R02=/workspace/e04/r02; V=/workspace/e03/venvs
T=$R02/logs/train_$ARM.times
cd $R02/src
run() {  # $1 = out dir, rest = extra args
  OUT=$1; shift
  echo "start $(date -u +%FT%TZ) out=$OUT args=$*" >> $T
  CUDA_VISIBLE_DEVICES=$GPU $V/si/bin/python train.py --data $R02/data/train_$ARM.jsonl --out $OUT --seed 0 "$@" \
    > $R02/logs/train_${ARM}$( [ $# -gt 0 ] && echo _mb2 ).log 2>&1
  RC=$?
  echo "exit $RC $(date -u +%FT%TZ) out=$OUT" >> $T
  return $RC
}
run $R02/runs/${ARM}_s0
RC=$?
if [ $RC -ne 0 ] && grep -q -E "OutOfMemoryError|CUDA out of memory" $R02/logs/train_$ARM.log; then
  echo "OOM: restarting from scratch with --micro_bs 2 $(date -u +%FT%TZ)" >> $T
  run $R02/runs/${ARM}_s0_mb2 --micro_bs 2
fi
