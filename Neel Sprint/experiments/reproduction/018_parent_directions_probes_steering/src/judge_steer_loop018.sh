#!/bin/bash
# 018: judge steered main-grid outputs as they are generated (resumable); exits when the steering process is gone
# and nothing is left to judge. usage: judge_steer_loop018.sh <steer_pid>
S="/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"; R=/root/runs/r018
export API_LEDGER="$S/api_ledger_018.jsonl" API_CAP_USD=50
cd "$S"
while true; do
  alive=0; kill -0 $1 2>/dev/null && alive=1
  /usr/bin/python3 steer_items018.py main > /dev/null
  out=$(/usr/bin/python3 judge018.py $R/judge_items_steer_main.jsonl $R/judgments_steer_main.jsonl --concurrency 160 2>&1 | tee -a $R/logs/judge_steer.log)
  echo "$(date -u +%H:%M:%S) alive=$alive" >> $R/logs/judge_steer.log
  if echo "$out" | grep -q "spend cap"; then echo "SPEND CAP" >> $R/logs/judge_steer.log; exit 2; fi
  if [ $alive = 0 ] && echo "$out" | grep -q "^0 judge calls"; then echo "JUDGE STEER DONE" >> $R/logs/judge_steer.log; exit 0; fi
  sleep 120
done
