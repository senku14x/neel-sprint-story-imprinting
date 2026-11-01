#!/usr/bin/env bash
# Train one arm with the teammate's train.py, unchanged, 001 recipe (all defaults) except the schedule, which comes from the
# extra arguments (R06: --schedule constant = linear warm-up over 10 steps, then the peak rate 5e-4 to the last step).
# LoRA r32 / alpha 64 / dropout 0, 12 targets; AdamW 5e-4, 10 warm-up steps; clip 1.0; micro 4 x accum 8; seed 0; thinking off.
# Straight through to step 250 (no --max_steps); train.py saves step025/062/125/188 and final.
# On an out-of-memory crash: restart from scratch once with micro-batch 2 x 16 (--micro_bs 2; same effective batch, as E01-D11).
#   bash train_arm.sh <arm> <gpu> <data file> [extra train.py args, e.g. --schedule constant]
# (R04's train_arm.sh: paths r04 -> r06; the data file is an argument, since arm a5bqc trains on R04's train_a5bq.jsonl;
#  extra train.py arguments are passed through.)
set -uo pipefail
source /workspace/e04/r06/scripts/env.sh; unset PYTHONPATH
ARM=$1; GPU=$2; DATA=$3; shift 3
R06=/workspace/e04/r06; V=/workspace/e03/venvs
T=$R06/logs/train_$ARM.times
cd $R06/src
run() {  # $1 = out dir, $2 = log suffix, rest = extra args
  OUT=$1; SUF=$2; shift 2
  echo "start $(date -u +%FT%TZ) out=$OUT args=$*" >> $T
  CUDA_VISIBLE_DEVICES=$GPU $V/si/bin/python train.py --data $DATA --out $OUT --seed 0 "$@" > $R06/logs/train_${ARM}${SUF}.log 2>&1
  RC=$?
  echo "exit $RC $(date -u +%FT%TZ) out=$OUT" >> $T
  return $RC
}
run $R06/runs/${ARM}_s0 "" "$@"
RC=$?
if [ $RC -ne 0 ] && grep -q -E "OutOfMemoryError|CUDA out of memory" $R06/logs/train_$ARM.log; then
  echo "OOM: restarting from scratch with --micro_bs 2 $(date -u +%FT%TZ)" >> $T
  run $R06/runs/${ARM}_s0_mb2 _mb2 "$@" --micro_bs 2
fi
