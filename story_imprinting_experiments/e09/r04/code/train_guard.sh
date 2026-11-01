#!/bin/bash
# usage: train_guard.sh NAME GPU REPLAY_FILE RATIO PER_STEP [MICRO_BS]
# Launches NAME's training (train_launch.sh), checks the Stage 2 hard gates at step 1 (stage2_gate.py); on a failure
# stops the run, moves its output aside and restarts once; a second failure stops the run (logs/STAGE2_FAILED_NAME).
# Out of memory: restart from scratch with micro-batch 2 x accumulation 16 (effective batch 32), recorded.
NAME=$1; GPU=$2; REPLAY=$3; RATIO=$4; PER=$5; MB=${6:-4}
W=/workspace/e09/r04; L=$W/logs/train_$NAME.log
for attempt in 1 2 3; do
  echo "attempt $attempt micro_bs $MB $(date -u +%FT%TZ)" >> $W/logs/train_guard_$NAME.log
  $W/code/train_launch.sh $NAME $GPU "$REPLAY" $RATIO $MB > $L.tmp 2>&1 &
  LP=$!
  ok=""
  while kill -0 $LP 2>/dev/null; do
    if [ -z "$ok" ]; then
      /usr/bin/python3 -I $W/code/stage2_gate.py $NAME $PER 8000 >> $W/logs/train_guard_$NAME.log 2>&1; rc=$?
      if [ $rc -eq 0 ]; then ok=1; echo "gates pass $(date -u +%FT%TZ)" >> $W/logs/train_guard_$NAME.log
      elif [ $rc -eq 1 ]; then ok=0; echo "GATE FAIL $(date -u +%FT%TZ)" >> $W/logs/train_guard_$NAME.log
        pkill -f "train.py .*adapters/$NAME " ; sleep 20; break; fi
    fi
    sleep 20
  done
  wait $LP
  if [ "$ok" = "1" ] && grep -q "^exit 0" $L.tmp; then mv $L.tmp $L; exit 0; fi
  cp $L.tmp $W/logs/train_${NAME}_attempt$attempt.log
  [ -d $W/adapters/$NAME ] && mv $W/adapters/$NAME $W/adapters/${NAME}_failed_attempt$attempt
  if grep -q "OutOfMemoryError\|CUDA out of memory" $L.tmp && [ "$MB" = "4" ]; then MB=2; echo "OOM -> micro_bs 2" >> $W/logs/train_guard_$NAME.log; continue; fi
  if [ "$ok" = "0" ] && [ $attempt -ge 2 ]; then break; fi
  [ $attempt -ge 2 ] && break
done
echo "STAGE 2 FAILED for $NAME $(date -u +%FT%TZ)" >> $W/logs/train_guard_$NAME.log
cp $L.tmp $L; echo "exit 9 $(date -u +%FT%TZ)" >> $L
touch $W/logs/STAGE2_FAILED_$NAME
exit 1
