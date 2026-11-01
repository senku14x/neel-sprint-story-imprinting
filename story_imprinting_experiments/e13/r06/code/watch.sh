#!/usr/bin/env bash
# Agent watcher for R06: return on a new MODEL_EXIT / ANALYZE / STAGE line, a Traceback, or after T seconds.
R=/workspace/e13/r06; EV=${2:-$R/logs/stageA_events.log}; T=${1:-600}; t0=$(date +%s); n0=$(wc -l < $EV 2>/dev/null || echo 0)
while :; do
  [ $(wc -l < $EV 2>/dev/null || echo 0) -gt $n0 ] && { echo "NEW EVENT"; break; }
  grep -l "Traceback\|CUDA out of memory" $R/logs/stage*_*.log 2>/dev/null | grep -q . && { echo "ERROR IN LOG"; break; }
  [ $(( $(date +%s) - t0 )) -ge $T ] && { echo "TIMEOUT ${T}s"; break; }
  sleep 15
done
date -u +%FT%TZ; tail -3 $EV; for f in $R/logs/stage*_*.log; do echo "$(basename $f): $(grep -E 'turn [0-9] done|wrote' $f | tail -1)"; done
wc -l $R/results/rollouts/*.jsonl 2>/dev/null | tail -1; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
