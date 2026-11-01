#!/bin/bash
# executor-9 (D16): create status/BACKLOG_GO once any box has had no running job for 2 consecutive 60-s checks.
O=/workspace/runs_executor/overnight_2026-10-30
declare -A idle=([box1]=0 [box2]=0 [box3]=0)
while [ ! -f $O/status/BACKLOG_GO ]; do
  for b in box1 box2 box3; do
    if ls $O/queue/*/*.running.$b >/dev/null 2>&1; then idle[$b]=0; else idle[$b]=$((idle[$b]+1)); fi
    if [ ${idle[$b]} -ge 2 ]; then echo "$(date -u +%FT%TZ) $b idle 2 checks -> BACKLOG_GO" | tee $O/status/BACKLOG_GO; python3 $O/lib/board.py event --job backlog_gate --exp infra --part gate --box $b --status note --result "BACKLOG_GO: $b idle >= 2 min; backlog smokes (sw022-sw026) now eligible"; break; fi
  done
  sleep 60
done
