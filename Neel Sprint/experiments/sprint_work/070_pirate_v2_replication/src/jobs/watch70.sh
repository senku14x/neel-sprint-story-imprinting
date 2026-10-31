#!/bin/bash
# sw070 watcher on BOX 1 (setsid nohup; waits on marker files only, polls every 60 s, max 30 h). Stop: touch $RUN/STOP_WATCH.
#  1) the first SMOKE_INJOB_OK_<model> -> post70.sh smoke (judges the smoke conversations present; spend projection, budget stop)
#  2) GPU_DONE_psA0 + GPU_DONE_psB0 + GPU_DONE_parent (the three per-model jobs, D9; any H200 pod) -> post70.sh main
RUN=/workspace/runs_executor/sw070; SRC="/workspace/Neel Sprint/experiments/sprint_work/070_pirate_v2_replication/src"
[ "$(hostname)" = af2422212563 ] || { echo "watch70 runs on box 1 only"; exit 1; }
echo "watch70 start $(date -u +%T) pid $$"; echo $$ > $RUN/watch70.pid
anysmoke() { ls $RUN/SMOKE_INJOB_OK_* >/dev/null 2>&1; }
alldone() { [ -e $RUN/GPU_DONE_psA0 ] && [ -e $RUN/GPU_DONE_psB0 ] && [ -e $RUN/GPU_DONE_parent ]; }
for i in $(seq 1 1800); do anysmoke && break; alldone && break; [ -e $RUN/STOP_WATCH ] && exit 0; sleep 60; done
if [ ! -e $RUN/post/projection_smoke.json ] && anysmoke; then
  sleep 120   # give a second job's smoke a chance to land too (more models in the per-char rate); not required
  bash "$SRC/jobs/post70.sh" smoke > $RUN/post70_smoke.log 2>&1
fi
for i in $(seq 1 1800); do alldone && break; [ -e $RUN/STOP_WATCH ] && exit 0; sleep 60; done
alldone || { echo "timeout waiting for the three GPU_DONE markers"; exit 1; }
[ -e $RUN/ANALYSIS_READY ] || bash "$SRC/jobs/post70.sh" main > $RUN/post70_main.log 2>&1
echo "watch70 end $(date -u +%T)"
