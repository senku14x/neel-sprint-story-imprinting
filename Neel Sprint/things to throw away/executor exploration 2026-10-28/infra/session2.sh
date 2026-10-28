#!/bin/bash
# Session 2 (design_spec §4): start the server only when X8 and X9 are ready; gate; release clients; hard stop at start + 28 min.
INFRA="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/infra"; L=/root/runs/expl1028
ts(){ date -u +%H:%M:%S; }
until [ -f $L/READY_X8 ] && [ -f $L/READY_X9 ]; do sleep 20; done
echo "READY both $(ts)"; cd "$INFRA"
T0=$(date +%s); echo "T0 $(ts)"
PREFIX_CACHING=0 bash serve.sh || { echo "SERVE_FAILED $(ts)"; exit 1; }
bash wait_ready.sh 20 > $L/infra_logs/wait_ready2.log 2>&1 || { echo "NOT_READY $(ts)"; bash stop_server.sh; exit 1; }
echo "ready $(ts)"
DL=$(date -u -d "@$((T0+26*60))" +%H:%M:%S); HARD=$((T0+28*60))
/root/venvs/si/bin/python gate_server.py run --fresh --deadline ${DL:0:5} > $L/infra_logs/gate_run2.log 2>&1; rc=$?
echo "gate rc=$rc $(ts)"; tail -2 $L/infra_logs/gate_run2.log
if [ $rc -ne 0 ]; then echo "GATE2_FAILED" > $L/GATE2_FAILED; bash stop_server.sh; exit 1; fi
echo "$DL" > $L/SERVER2_GATED; echo "released clients, deadline $DL $(ts)"
while true; do
  [ -f $L/gpu_done2/X8 ] && [ -f $L/gpu_done2/X9 ] && { echo "BOTH_DONE $(ts)"; break; }
  [ $(date +%s) -ge $HARD ] && { echo "HARD_STOP $(ts)"; break; }
  sleep 15
done
bash stop_server.sh; echo "SERVER2_STOPPED $(ts) minutes=$(( ($(date +%s)-T0)/60 ))"
