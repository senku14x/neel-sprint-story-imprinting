#!/bin/bash
# E1: replace a running v3 queue runner with v4 at the next job boundary (never kills a job). usage: swap_to_v4.sh <box> <old_pid>
B=$1; P=$2; D=/workspace/runs_executor/day_2026-10-31_E1
touch $D/status/STOP_$B
while kill -0 $P 2>/dev/null; do sleep 5; done
rm -f $D/status/STOP_$B
cd $D && nohup bash lib/queue_runner_v4.sh $B > $D/logs/runner_${B}_v4.log 2>&1 < /dev/null &
echo "$(date -u +%T) $B: v3 pid $P exited; v4 started pid $!"
