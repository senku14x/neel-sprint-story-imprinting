#!/bin/bash
# E2 pull loop v2 (executor-14, 31 Oct 22:2x): as pull_loop.sh, but node /root/runs/sw071/ (E2's polish-v2 run, renumbered sw082
# because sw071 belongs to E5) lands in /workspace/runs_executor/sw082/, never in sw071/. Stop: touch .../status/STOP_pull
E="ssh -p <port> -i /root/.ssh/id_ed25519 -o BatchMode=yes -o ConnectTimeout=20"
ST=/workspace/runs_executor/day_2026-10-31_E2/status
while [ ! -e $ST/STOP_pull ]; do
  for d in $($E root@<box-ip> 'ls -d /root/runs/sw0* 2>/dev/null'); do
    x=$(basename $d); [ "$x" = sw071 ] && x=sw082
    [ "$x" = sw071 ] && continue
    mkdir -p /workspace/runs_executor/$x
    rsync -a -e "$E" root@<box-ip>:$d/ /workspace/runs_executor/$x/ && echo "$(date -u +%H:%M:%S) pulled $(basename $d) -> $x"
  done
  date -u +%Y-%m-%dT%H:%M:%SZ > $ST/pull.heartbeat
  sleep 600
done
