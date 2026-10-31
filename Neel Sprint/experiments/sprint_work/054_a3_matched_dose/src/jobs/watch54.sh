#!/bin/bash
# sw054 box-1 watcher (D21): the main job may run on box1 or boxA, but API judging runs on box 1 only. Waits for the main job's
# marker (OUTPUT_GATES_OK -> run post54.sh; OUTPUT_GATES_FAILED -> exit without judging), polling every 60 s. Start on box 1:
#   nohup bash watch54.sh > /workspace/runs_executor/sw054/watch54.log 2>&1 < /dev/null &   (PID -> sw054/watch54.pid)
set -u
R=/workspace/runs_executor/sw054
SRC="/workspace/Neel Sprint/experiments/sprint_work/054_a3_matched_dose/src"
[ "$(hostname)" = af2422212563 ] || { echo "watch54 must run on box 1"; exit 5; }
echo $$ > "$R/watch54.pid"
echo "watch54 start $(date -u +%T) pid $$"
until [ -e "$R/OUTPUT_GATES_OK" ] || [ -e "$R/OUTPUT_GATES_FAILED" ]; do sleep 60; done
if [ -e "$R/OUTPUT_GATES_FAILED" ]; then echo "output gates failed $(date -u +%T): no judging"; exit 4; fi
echo "OUTPUT_GATES_OK seen $(date -u +%T): running post54"
bash "$SRC/jobs/post54.sh" > "$R/post_main.log" 2>&1 < /dev/null
echo "watch54 done rc=$? $(date -u +%T)"
