#!/bin/bash
# sw066 box-1 watcher (started once on box 1 with setsid nohup; waits on marker files, never on process patterns).
# smoke GPU_DONE -> post66.sh smoke; main GPU_DONE -> post66.sh main; then exits. Stop early: touch /workspace/runs_executor/sw066/STOP_WATCH.
RUN=/workspace/runs_executor/sw066; SRC="/workspace/Neel Sprint/experiments/sprint_work/066_thinking_split/src"
echo "watch66 start $(date -u +%T) pid $$"; echo $$ > $RUN/watch66.pid
until [ -e $RUN/GPU_DONE_smoke ]; do [ -e $RUN/STOP_WATCH ] && exit 0; sleep 30; done
[ -e $RUN/smoke/ANALYSIS_READY.box1 ] || { bash "$SRC/jobs/post66.sh" smoke > $RUN/post_smoke.log 2>&1; touch $RUN/smoke/ANALYSIS_READY.box1; }
until [ -e $RUN/GPU_DONE_main ]; do [ -e $RUN/STOP_WATCH ] && exit 0; sleep 60; done
bash "$SRC/jobs/post66.sh" main > $RUN/post_main.log 2>&1
echo "watch66 end $(date -u +%T)"
