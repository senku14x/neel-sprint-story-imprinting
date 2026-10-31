#!/bin/bash
# sw067 H200-arm watcher on BOX 1 (setsid nohup; waits on marker files only). GPU_DONE_h200 -> post67h.sh h200; then, only if the
# analysis queued the second arm (FLASH0_QUEUED), GPU_DONE_h200flash0 -> post67h.sh h200flash0. Stop: touch $RUN/STOP_WATCH_H200.
RUN=/workspace/runs_executor/sw067; SRC="/workspace/Neel Sprint/experiments/sprint_work/067_trigger_gating_retest/src"
echo "watch67h start $(date -u +%T) pid $$"; echo $$ > $RUN/watch67h.pid
until [ -e $RUN/GPU_DONE_h200 ]; do [ -e $RUN/STOP_WATCH_H200 ] && exit 0; sleep 60; done
[ -e $RUN/ANALYSIS_READY_h200 ] || bash "$SRC/jobs/post67h.sh" h200 > $RUN/post_h200.log 2>&1
[ -e $RUN/FLASH0_QUEUED ] || { echo "no second arm queued; watch67h end $(date -u +%T)"; exit 0; }
until [ -e $RUN/GPU_DONE_h200flash0 ]; do [ -e $RUN/STOP_WATCH_H200 ] && exit 0; sleep 60; done
[ -e $RUN/ANALYSIS_READY_h200flash0 ] || bash "$SRC/jobs/post67h.sh" h200flash0 > $RUN/post_h200flash0.log 2>&1
echo "watch67h end $(date -u +%T)"
