#!/bin/bash
# wait until <exp> has a JUDGED_* or NEEDS_REJUDGE marker and no judge_run.py process for it on any box (max <min> minutes)
E=$1; M=${2:-60}; D=/workspace/runs_executor/$E; end=$((SECONDS+M*60))
running(){ local n=0; for h in local box2 box3; do if [ $h = local ]; then c=$(ps -eo args | grep -c "[j]udge_run.py.*--exp $E\b"); else c=$(ssh $h "ps -eo args | grep -c '[j]udge_run.py.*--exp $E'" 2>/dev/null); fi; n=$((n+${c:-0})); done; echo $n; }
until [ $SECONDS -ge $end ]; do
  if ls $D | grep -qE "^(JUDGED|NEEDS_REJUDGE)" && [ "$(running)" = 0 ]; then break; fi; sleep 30; done
echo "$(date -u +%H:%M) $E markers: $(ls $D | grep -E '^(GPU_DONE|JUDGED|ANALY|NEEDS)' | tr '\n' ' ') judge procs: $(running)"
