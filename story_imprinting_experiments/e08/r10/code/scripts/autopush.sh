#!/bin/bash
# E08 R10: push every 15 minutes until logs/autopush_stop exists.
W=/workspace/e08/r10
while [ ! -f $W/logs/autopush_stop ]; do
  sleep 900
  bash $W/code/push.sh "E08 R10: periodic sync $(date -u +%H:%M) UTC" >> $W/logs/push.log 2>&1
done
