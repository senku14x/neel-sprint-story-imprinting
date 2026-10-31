#!/bin/bash
# exits when any job fails, the worker exits, or all jobs matching $1 are in done/
PAT="$1"
while true; do
  if grep -qE "JOB_FAILED|WORKER_EXIT|Traceback" /root/runs/extract1028/logs/worker3.log; then grep -E "JOB_FAILED|WORKER_EXIT" /root/runs/extract1028/logs/worker3.log | tail -3; exit 1; fi
  left=$(ls /root/runs/extract1028/queue /root/runs/extract1028/running 2>/dev/null | grep -cE "$PAT")
  if [ "$left" -eq 0 ]; then echo "MILESTONE $PAT done $(date -u +%T)"; grep JOB_DONE /root/runs/extract1028/logs/worker3.log | tail -4; exit 0; fi
  sleep 20
done
