#!/bin/bash
# E13 R02: push every 20 minutes until logs/autopush_stop exists (the brief: push at least every 20 minutes).
W=/workspace/e13/r02
while [ ! -f $W/logs/autopush_stop ]; do
  sleep 1200
  [ -f $W/logs/autopush_stop ] && break
  echo "$(date -u +%FT%TZ) $(bash $W/code/push.sh 'E13 R02: autopush' 2>&1 | tail -1)" >> $W/logs/push.log
done
