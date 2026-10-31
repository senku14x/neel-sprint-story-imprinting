#!/bin/bash
# sw067 box-1 watcher (started once on box 1 with setsid nohup; waits on marker files, never on process patterns).
# smoke GPU_DONE -> post67.sh smoke; main GPU_DONE -> post67.sh main; then exits. Stop early: touch /workspace/runs_executor/sw067/STOP_WATCH.
RUN=/workspace/runs_executor/sw067; SRC="/workspace/Neel Sprint/experiments/sprint_work/067_trigger_gating_retest/src"
echo "watch67 start $(date -u +%T) pid $$"; echo $$ > $RUN/watch67.pid
until [ -e $RUN/GPU_DONE_smoke ]; do [ -e $RUN/STOP_WATCH ] && exit 0; sleep 30; done
[ -e $RUN/smoke/ANALYSIS_READY.box1 ] || { bash "$SRC/jobs/post67.sh" smoke > $RUN/post_smoke.log 2>&1; touch $RUN/smoke/ANALYSIS_READY.box1; }
until [ -e $RUN/GPU_DONE_main ]; do [ -e $RUN/STOP_WATCH ] && exit 0; sleep 60; done
bash "$SRC/jobs/post67.sh" main > $RUN/post_main.log 2>&1
echo "watch67 end $(date -u +%T)"
