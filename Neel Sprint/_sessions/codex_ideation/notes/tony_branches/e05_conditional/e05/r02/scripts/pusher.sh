#!/bin/bash
# every 15 min: refresh STATUS.md and push (push.sh holds a lock)
while true; do
  python3 /workspace/e05/r02/driver/r02_status.py && /workspace/e05/r02/scripts/push.sh "periodic status" >> /workspace/e05/r02/logs/push.log 2>&1
  sleep 900
done
