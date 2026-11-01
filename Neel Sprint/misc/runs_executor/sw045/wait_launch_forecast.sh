#!/bin/bash
# sw045: poll E3's node every 2 min (bounded, 2.5 h); launch the forecast capture on GPU 1 once E3's three conditions hold.
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=20 root@<box-ip>"
for i in $(seq 1 75); do
  r=$($SSH 'A=0; [ -e /root/runs/sw042/score/matchedA/DONE_ALL ] && A=1; C=0; ls /root/runs/sw042/score/claims/ 2>/dev/null | grep -q "^matchedB" && C=1
     P=$(nvidia-smi -i 1 --query-compute-apps=pid --format=csv,noheader | grep -c .); M=$(nvidia-smi -i 1 --query-gpu=memory.used --format=csv,noheader,nounits | tr -d " ")
     if [ $A = 1 ] && [ $C = 1 ] && [ "$P" = 0 ] && [ "$M" -lt 2048 ]; then setsid -f nohup bash /root/runs/sw045/code/run/run_forecast45.sh 1 > /dev/null 2>&1 < /dev/null; echo "LAUNCHED $(date -u +%T) A=$A C=$C P=$P M=$M"; else echo "wait $(date -u +%T) A=$A C=$C P=$P M=$M"; fi' 2>&1 | tail -1)
  echo "$r"
  case "$r" in LAUNCHED*) exit 0;; esac
  sleep 120
done
echo "TIMEOUT $(date -u +%T)"; exit 1
