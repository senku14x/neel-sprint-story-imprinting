#!/bin/bash
# usage: train_guard2.sh NAME GPU REPLAY_FILE RATIO PER_STEP MICRO_BS
# Replaces train_guard.sh after 06:07 (its OOM check missed the message "CUDA ran out of memory outside PyTorch's
# allocator", so Rsarc was restarted with the same micro-batch). Launches NAME's training (train_launch.sh), checks the
# Stage 2 hard gates at step 1 (stage2_gate.py); a gate failure stops the run and restarts once (second failure: stop,
# logs/STAGE2_FAILED_NAME). Out of memory (any "out of memory" message): restart from scratch with half the micro-batch
# (effective batch 32 kept). Failed/aborted outputs are moved to adapters/NAME_failed_<time>.
NAME=$1; GPU=$2; REPLAY=$3; RATIO=$4; PER=$5; MB=$6
W=/workspace/e09/r04; L=$W/logs/train_$NAME.log; GL=$W/logs/train_guard2_$NAME.log
gatefails=0
for attempt in 1 2 3 4; do
  echo "attempt $attempt micro_bs $MB $(date -u +%FT%TZ)" >> $GL
  $W/code/train_launch.sh $NAME $GPU "$REPLAY" $RATIO $MB > $L.tmp 2>&1 &
  LP=$!
  ok=""
  while kill -0 $LP 2>/dev/null; do
    if [ -z "$ok" ]; then
      /usr/bin/python3 -I $W/code/stage2_gate.py $NAME $PER 8000 >> $GL 2>&1; rc=$?
      if [ $rc -eq 0 ]; then ok=1; echo "gates pass $(date -u +%FT%TZ)" >> $GL
      elif [ $rc -eq 1 ]; then ok=0; echo "GATE FAIL $(date -u +%FT%TZ)" >> $GL
        pkill -f "train.py .*adapters/$NAME --seed" ; sleep 20; break; fi
    fi
    sleep 20
  done
  wait $LP
  if [ "$ok" = "1" ] && grep -q "^exit 0" $L.tmp; then mv $L.tmp $L; echo "done $(date -u +%FT%TZ)" >> $GL; exit 0; fi
  ts=$(date -u +%H%M%S)
  cp $L.tmp $W/logs/train_${NAME}_failed_$ts.log
  [ -d $W/adapters/$NAME ] && mv $W/adapters/$NAME $W/adapters/${NAME}_failed_$ts
  if grep -qi "out of memory" $L.tmp && [ "$MB" -gt 1 ]; then MB=$((MB / 2)); echo "OOM -> micro_bs $MB" >> $GL; continue; fi
  if [ "$ok" = "0" ]; then gatefails=$((gatefails + 1)); [ $gatefails -ge 2 ] && break; continue; fi
  echo "failed for another reason (see logs/train_${NAME}_failed_$ts.log)" >> $GL
  break
done
echo "STAGE 2 FAILED for $NAME $(date -u +%FT%TZ)" >> $GL
cp $L.tmp $L; echo "exit 9 $(date -u +%FT%TZ)" >> $L
touch $W/logs/STAGE2_FAILED_$NAME
exit 1
