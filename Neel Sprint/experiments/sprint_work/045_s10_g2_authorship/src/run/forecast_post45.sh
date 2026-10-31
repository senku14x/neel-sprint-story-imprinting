#!/bin/bash
# sw045 forecast, box 1: wait (bounded 60 min) for the node capture, pull it, hash-check it (verify45), then C4's compute stage
# (E4's forecast61.py from 045/src/e4, unedited; CPU; reads E4's saved parent keys) -> forecast.json + FORECAST_FROZEN.
set -u
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=20 root@<node-ip>"
RUN="/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/run"; E4="/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/e4"
O=/workspace/runs_executor/sw045/g2_forecast
for i in $(seq 1 120); do
  s=$($SSH 'ls /root/runs/sw045/g2_forecast/ | grep -E "^(DONE_capture|FAILED_capture)$"' 2>/dev/null)
  [ -n "$s" ] && break; sleep 30
done
echo "node capture state: '${s:-none}' $(date -u +%T)"
[ "$s" = DONE_capture ] || { echo "capture not done; stop"; exit 2; }
bash "$RUN/pull45.sh" g2_forecast verify || { echo "pull/verify failed"; exit 3; }
cd /workspace/runs_executor/sw045
echo "compute start $(date -u +%FT%TZ)"
OMP_NUM_THREADS=8 /root/venvs/si/bin/python -I "$E4/forecast61.py" compute $O --engine vllm018; rc=$?
echo "compute rc=$rc $(date -u +%FT%TZ)"
[ $rc = 0 ] && { sha256sum $O/forecast.json; cat $O/FORECAST_FROZEN; }
exit $rc
