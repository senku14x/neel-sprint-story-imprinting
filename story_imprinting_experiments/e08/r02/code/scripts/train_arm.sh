#!/usr/bin/env bash
# Train one arm with the teammate's 001 train.py (unchanged, /workspace/e05/src, commit d3eaad2b), Q's recipe:
# LoRA r32 / alpha 64 / dropout 0, 12 targets; AdamW 5e-4 (0.9, 0.999, eps 1e-8, wd 0); 10 warm-up steps then constant;
# clip 1.0; micro 4 x accum 8 (effective 32); one epoch; seed 0; loss on story tokens + <|im_end|>; thinking off.
# Saves step125 and final under /workspace/e08/r02/adapters/<arm>/. On an out-of-memory crash: restart from scratch with --micro_bs 2 (same effective batch).
#   bash train_arm.sh <arm N|NB> <gpu> [extra train.py args]
# E08 R02 additions (smoke test; defaults unchanged): env DATA (training file), OUTBASE (adapter folder), LOGTAG (log name);
# extra arguments after <gpu> are passed to train.py (argparse keeps the last value, so e.g. --save_steps 3 overrides 125).
set -uo pipefail
source /workspace/e08/r02/code/env.sh; unset PYTHONPATH
ARM=$1; GPU=$2; shift 2; EXTRA=("$@")
R=/workspace/e08/r02; V=/workspace/e03/venvs/si
DATA=${DATA:-$R/data/train_$ARM.jsonl}; OUTBASE=${OUTBASE:-$R/adapters}; LOGTAG=${LOGTAG:-$ARM}
T=$R/logs/train_$LOGTAG.times
mkdir -p $OUTBASE $R/logs
cd /workspace/e05/src
run() {
  OUT=$1; LOG=$2; shift 2
  echo "start $(date -u +%FT%TZ) out=$OUT args=${EXTRA[*]} $*" >> $T
  CUDA_VISIBLE_DEVICES=$GPU $V/bin/python train.py --data $DATA --out $OUT --seed 0 \
    --schedule constant --warmup 10 --save_steps 125 "${EXTRA[@]}" "$@" > $LOG 2>&1
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
