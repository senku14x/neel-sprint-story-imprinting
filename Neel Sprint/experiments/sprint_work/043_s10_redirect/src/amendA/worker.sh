#!/bin/bash
# sw043 Amendment A node worker for one GPU: wait for the GPU's current job (log marker), then claim queued jobs one at a time
# (atomic mkdir claim) until the queue is empty.   GPU=g CPUS=c bash worker.sh <wait-log> <wait-regex>
set -u
B=/root/runs/sw043; Q=$B/amendA/queue; WL=${1:-}; WR=${2:-}
log() { echo "[$(date -u +%FT%TZ)] GPU$GPU $*"; }
if [ -n "$WL" ]; then until [ -f "$WL" ] && grep -qE "$WR" "$WL"; do sleep 20; done; log "initial job done ($WL)"; fi
while true; do
  next=""
  for j in $(ls $Q/*.job 2>/dev/null | sort); do
    n=$(basename $j .job)
    if mkdir $Q/$n.claimed 2>/dev/null; then next=$n; break; fi
  done
  [ -z "$next" ] && { log "queue empty; exit"; break; }
  log "claim $next"; echo "GPU=$GPU CPUS=$CPUS host=$(hostname) start=$(date -u +%FT%TZ)" > $Q/$next.claimed/info
  GPU=$GPU CPUS=$CPUS bash $Q/$next.job > $B/logs/amendA/$next.log 2>&1; rc=$?
  echo "rc=$rc end=$(date -u +%FT%TZ)" >> $Q/$next.claimed/info; log "done $next rc=$rc"
done
