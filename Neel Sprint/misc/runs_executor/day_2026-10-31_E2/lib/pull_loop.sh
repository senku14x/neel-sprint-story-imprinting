#!/bin/bash
# E2: pull node results every 10 min to /workspace/runs_executor/<exp>/ (stop: touch /workspace/runs_executor/day_2026-10-31_E2/status/STOP_pull)
E="ssh -p <port> -i /root/.ssh/id_ed25519 -o BatchMode=yes -o ConnectTimeout=20"
while [ ! -e /workspace/runs_executor/day_2026-10-31_E2/status/STOP_pull ]; do
  for d in $($E root@<box-ip> 'ls -d /root/runs/sw0* 2>/dev/null'); do
    x=$(basename $d); mkdir -p /workspace/runs_executor/$x
    rsync -a -e "$E" root@<box-ip>:$d/ /workspace/runs_executor/$x/ && echo "$(date -u +%H:%M:%S) pulled $x"
  done
  date -u +%Y-%m-%dT%H:%M:%SZ > /workspace/runs_executor/day_2026-10-31_E2/status/pull.heartbeat
  sleep 600
done
