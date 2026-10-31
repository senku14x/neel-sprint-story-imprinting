#!/bin/bash
# sw042 per-GPU queue on the node (written 2026-10-31 by a subagent of E3 / executor-12).
# Usage (node): setsid nohup bash gpu_queue.sh <gpu> > /root/runs/sw042/logs/queue_gpu<gpu>.log 2>&1 &
# Nothing starts until /root/runs/sw042/train/ALLOW_gpu<gpu> exists (the user's go). Then the GPU runs its jobs.json entries in
# round order (round 1, then round 2), one at a time, each through run_train.sh. A job that FAILS stops this GPU's queue
# (no silent continuation). Plan (jobs.json): GPU0 mainA -> honestA; GPU1 mainB -> honestB; GPU2 mirrorA -> Fonly;
# GPU3 mirrorB -> the learning-check watcher (learn/learn_watch.sh), which runs every step-125 and final check as the
# snapshots appear. Stop a queue: touch /root/runs/sw042/train/STOP_gpu<gpu> (it stops before its next job); kill a run by PID.
set -u
GPU=$1; R=${SW042_ROOT:-/root/runs/sw042}; CODE=$R/code
mkdir -p $R/train $R/logs
until [ -e $R/train/ALLOW_gpu$GPU ]; do sleep 30; done
echo "gpu$GPU allowed $(date -u +%FT%TZ)"
RUNS=$(python3 -I -c "import json; js=json.load(open('$R/data/jobs.json'))['jobs']; print(' '.join(j['run'] for j in sorted(js, key=lambda j: j['round']) if j['gpu']==$GPU))")
echo "gpu$GPU jobs: $RUNS"
for run in $RUNS; do
  [ -e $R/train/STOP_gpu$GPU ] && { echo "gpu$GPU STOP file, not starting $run $(date -u +%FT%TZ)"; exit 0; }
  [ -e $R/train/$run/DONE ] && { echo "gpu$GPU $run already DONE"; continue; }
  echo "gpu$GPU start $run $(date -u +%FT%TZ)"
  bash $CODE/train/run_train.sh $run $GPU ${SW042_MODE:-real}   # SW042_MODE=dry only in the box-1 logic test
  if [ -e $R/train/$run/DONE ]; then echo "gpu$GPU done $run $(date -u +%FT%TZ)"; else echo "gpu$GPU FAILED $run $(date -u +%FT%TZ); queue stops"; exit 1; fi
done
if [ "$GPU" = "${SW042_LEARN_GPU:-3}" ]; then
  echo "gpu$GPU -> learning-check watcher $(date -u +%FT%TZ)"
  bash $CODE/learn/learn_watch.sh $GPU
fi
echo "gpu$GPU queue empty $(date -u +%FT%TZ)"
