#!/bin/bash
# 018: judge rollouts as they are generated (resumable). Stops when the generator is gone and nothing is left to judge.
# usage: judge_loop018.sh <generator_pid>
S="/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"
export API_LEDGER="$S/api_ledger_018.jsonl" API_CAP_USD=50
cd "$S"
while true; do
  alive=0; kill -0 $1 2>/dev/null && alive=1
  python3 filters018.py items --gen /root/runs/r018/gen.jsonl --out /root/runs/r018/judge_items.jsonl
  out=$(python3 judge018.py /root/runs/r018/judge_items.jsonl /root/runs/r018/judgments.jsonl --concurrency 160 2>&1 | tee -a /root/runs/r018/logs/judge_loop.log)
  echo "$(date -u +%H:%M:%S) alive=$alive" >> /root/runs/r018/logs/judge_loop.log
  if echo "$out" | grep -q "spend cap"; then echo "SPEND CAP" >> /root/runs/r018/logs/judge_loop.log; exit 2; fi
  if [ $alive = 0 ] && echo "$out" | grep -q "^0 judge calls"; then echo "JUDGE LOOP DONE" >> /root/runs/r018/logs/judge_loop.log; exit 0; fi
  [ -f /root/runs/r018/JUDGE_STOP ] && exit 3
  sleep 300
done
