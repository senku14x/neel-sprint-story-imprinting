#!/usr/bin/env bash
# Every 30 minutes: read OpenRouter key usage, rewrite STATUS.md (time, spend), push.
while true; do
  sleep 1800
  /workspace/e03/venvs/api/bin/python -I /workspace/e04/r02/scripts/key_usage.py loop >> /workspace/e04/r02/logs/status_loop.log 2>&1
  /workspace/venvs/gpu/bin/python -I /workspace/e04/r02/scripts/status.py >> /workspace/e04/r02/logs/status_loop.log 2>&1
  bash /workspace/e04/r02/scripts/push.sh "E04 R02: status $(date -u +%H:%M) UTC" >> /workspace/e04/r02/logs/status_loop.log 2>&1
done
