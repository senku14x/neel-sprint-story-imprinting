#!/bin/bash
# E08 R05: push every 30 minutes (push.sh holds a lock, so manual pushes never overlap).
while true; do
  sleep 1800
  bash /workspace/e08/r05/code/push.sh "E08 R05: periodic push $(date -u +%FT%TZ)" >> /workspace/e08/r05/logs/autopush.log 2>&1
done
