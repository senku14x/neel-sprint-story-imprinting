#!/usr/bin/env bash
# Agent watcher: return when <run>/train_log.jsonl reaches N lines, a new INSTANCE_EXIT/uploaded line appears, or T seconds pass.
# Usage: watch.sh <train_log path or -> <N> <T>
R=/workspace/e13/r04v2b; TL=$1; N=$2; T=$3; t0=$(date +%s)
e0=$(grep -c "INSTANCE_EXIT" $R/logs/instances.log 2>/dev/null); u0=$(cat $R/logs/eliteB.log $R/logs/sflB.log 2>/dev/null | grep -c "^uploaded ")
while :; do
  [ "$TL" != - ] && [ -f "$TL" ] && [ $(wc -l < "$TL") -ge $N ] && { echo "REACHED $N lines in $TL"; break; }
  [ $(grep -c "INSTANCE_EXIT" $R/logs/instances.log 2>/dev/null) -gt $e0 ] && { echo "NEW INSTANCE_EXIT"; break; }
  [ $(cat $R/logs/eliteB.log $R/logs/sflB.log 2>/dev/null | grep -c "^uploaded ") -gt $u0 ] && { echo "NEW UPLOAD"; break; }
  [ $(( $(date +%s) - t0 )) -ge $T ] && { echo "TIMEOUT ${T}s"; break; }
  sleep 15
done
date -u +%FT%TZ; tail -2 $R/logs/instances.log; [ "$TL" != - ] && [ -f "$TL" ] && { wc -l < "$TL"; tail -1 "$TL"; }
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; tmux ls | cut -d: -f1 | tr '\n' ' '; echo
