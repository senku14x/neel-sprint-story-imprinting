#!/bin/bash
# Stop the shared server when every part has written /root/runs/expl1028/gpu_done/<part>, or at the hard stop (D6.7).
PARTS="X2 X5 X3a X3b1 X4 X6 X7"; HARD=${HARD_STOP:-12:55}
INFRA="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/infra"
while true; do
  n=0; for p in $PARTS; do [ -f /root/runs/expl1028/gpu_done/$p ] && n=$((n+1)); done
  if [ $n -eq 7 ]; then echo "ALL_PARTS_DONE $(date -u +%H:%M:%S)"; break; fi
  if [[ "$(date -u +%H:%M)" > "$HARD" || "$(date -u +%H:%M)" == "$HARD" ]]; then echo "HARD_STOP $(date -u +%H:%M:%S) ($n/7 parts done)"; break; fi
  sleep 30
done
cd "$INFRA" && bash stop_server.sh; echo "SERVER_STOPPED $(date -u +%H:%M:%S)"; nvidia-smi --query-gpu=memory.used --format=csv,noheader
