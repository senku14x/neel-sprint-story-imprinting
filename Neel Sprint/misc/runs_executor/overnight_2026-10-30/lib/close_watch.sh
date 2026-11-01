#!/bin/bash
# executor-9 D36: release boxes 2 and 3 when nothing is left for them, then wait until each is SAFE_TO_CLOSE
O=/workspace/runs_executor/overnight_2026-10-30
until [ $(ls $O/queue/*/*.job 2>/dev/null | wc -l) = 0 ] && ! ls $O/queue/*/*.running.box2 $O/queue/*/*.running.box3 >/dev/null 2>&1; do sleep 30; done
touch $O/status/STOP_box2 $O/status/STOP_box3; echo "$(date -u +%T) runners on box2/box3 told to stop"
for b in box2 box3; do
  until $O/lib/close_check.sh $b | grep -q SAFE_TO_CLOSE; do sleep 30; done
  echo "$(date -u +%T) $b SAFE_TO_CLOSE"; $O/lib/close_check.sh $b | head -3
done
