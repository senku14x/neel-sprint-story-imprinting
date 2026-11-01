#!/bin/bash
# every 15 min: refresh STATUS.md's auto block and push (push.sh holds a lock)
while true; do
  sleep 900
  python3 -I /workspace/e05/r04/driver/r04_status.py && /workspace/e05/r04/scripts/push.sh "periodic status" >> /workspace/e05/r04/logs/push.log 2>&1
done
