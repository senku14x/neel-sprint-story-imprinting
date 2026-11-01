#!/usr/bin/env bash
# Refresh STATUS.md and push every 15 minutes (push.sh is serialised with flock).
while true; do
  sleep 900
  /workspace/e03/venvs/api/bin/python -I /workspace/e03/stage1/scripts/status.py > /dev/null 2>&1
  bash /workspace/e03/stage1/scripts/push.sh "E03 stage 1: periodic STATUS.md" >> /workspace/e03/stage1/logs/status_loop.log 2>&1
done
