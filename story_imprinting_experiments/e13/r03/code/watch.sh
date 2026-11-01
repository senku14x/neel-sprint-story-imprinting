#!/bin/bash
# E13 R03 agent helper: wait until a condition holds, a run session disappears, or a time limit passes; then print why.
# Usage: watch.sh "<bash condition>" <max minutes> [sessions to require, space-separated]
COND=$1; MAX=$2; SESS=${3:-"chain judge voice autopush deadline"}
end=$(( $(date +%s) + MAX * 60 ))
while true; do
  if bash -c "$COND" 2>/dev/null; then echo "CONDITION MET $(date -u +%FT%TZ): $COND"; exit 0; fi
  for s in $SESS; do tmux has-session -t $s 2>/dev/null || { echo "SESSION GONE $(date -u +%FT%TZ): $s"; exit 2; }; done
  [ $(date +%s) -ge $end ] && { echo "TIMEOUT $(date -u +%FT%TZ) after $MAX min"; exit 1; }
  sleep 60
done
