#!/bin/bash
# E08 R02: periodic push (every 25 min) until logs/push_loop_stop exists. push.sh holds a lock, so manual pushes are safe.
while [ ! -f /workspace/e08/r02/logs/push_loop_stop ]; do
  sleep 1500
  [ -f /workspace/e08/r02/logs/push_loop_stop ] && break
  /workspace/e08/r02/scripts/push.sh "E08 R02: periodic sync $(date -u +%H:%M)" >> /workspace/e08/r02/logs/push_loop.log 2>&1
done
