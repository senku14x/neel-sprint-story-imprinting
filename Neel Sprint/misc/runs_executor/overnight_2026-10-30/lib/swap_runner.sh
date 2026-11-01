#!/bin/bash
# executor-9 D17: stop the v1 runner on this box after its current job, then start queue_runner_v2.sh.
B=$1; OLD=$2; O=/workspace/runs_executor/overnight_2026-10-30
touch $O/status/STOP_$B
while kill -0 $OLD 2>/dev/null; do sleep 3; done
rm -f $O/status/STOP_$B
nohup bash $O/lib/queue_runner_v2.sh $B >> $O/logs/runner_$B.log 2>&1 &
echo "$(date -u +%T) $B: v1 pid $OLD exited; v2 pid $!" >> $O/logs/runner_swap.log
