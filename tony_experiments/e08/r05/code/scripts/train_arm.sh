#!/usr/bin/env bash
# E08 R05: copy of R02's train_arm.sh with --schedule constant changed to the cosine arguments found in pre-flight
# (--schedule cosine --warmup 10; train.py's lr_factor: linear warm-up 10 steps, then cosine decay to 0, = SB's run).
# Everything else is R02's (Q's) recipe: the teammate's 001 train.py (unchanged, /workspace/e05/src), LoRA r32 / alpha 64 /
# dropout 0, 12 targets; AdamW 5e-4 (0.9, 0.999, eps 1e-8, wd 0); clip 1.0; micro 4 x accum 8; one epoch; seed 0.
# Saves step125 and final under /workspace/e08/r05/adapters/<model>/. On OOM: restart from scratch with --micro_bs 2.
#   DATA=<train file> bash train_arm.sh <model Nc|NBc|X|XB> <gpu> [extra train.py args]
set -uo pipefail
source /workspace/e08/r05/code/env.sh; unset PYTHONPATH
ARM=$1; GPU=$2; shift 2; EXTRA=("$@")
R=/workspace/e08/r05; V=/workspace/e03/venvs/si
DATA=${DATA:?set DATA}; OUTBASE=${OUTBASE:-$R/adapters}; LOGTAG=${LOGTAG:-$ARM}
T=$R/logs/train_$LOGTAG.times
mkdir -p $OUTBASE $R/logs
cd /workspace/e05/src
run() {
  OUT=$1; LOG=$2; shift 2
  echo "start $(date -u +%FT%TZ) out=$OUT data=$DATA args=${EXTRA[*]} $*" >> $T
  CUDA_VISIBLE_DEVICES=$GPU $V/bin/python train.py --data $DATA --out $OUT --seed 0 \
    --schedule cosine --warmup 10 --save_steps 125 "${EXTRA[@]}" "$@" > $LOG 2>&1
  RC=$?
  echo "exit $RC $(date -u +%FT%TZ) out=$OUT" >> $T
  return $RC
}
run $OUTBASE/${ARM} $R/logs/train_$LOGTAG.log
RC=$?
if [ $RC -ne 0 ] && grep -q -E "OutOfMemoryError|CUDA out of memory" $R/logs/train_$LOGTAG.log; then
  echo "OOM: restarting from scratch with --micro_bs 2 $(date -u +%FT%TZ)" >> $T
  run $OUTBASE/${ARM}_mb2 $R/logs/train_${LOGTAG}_mb2.log --micro_bs 2
fi
