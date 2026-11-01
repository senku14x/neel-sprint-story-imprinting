#!/bin/bash
# E4 orchestrator watcher (v2, 08:58 UTC): exit when any queue job reaches .done/.failed, or any sw055–sw060 marker
# (GATE_*, SMOKE_OK, GPU_DONE*, ANALYSIS_READY, JUDGED*) appears or changes, or after MAXMIN minutes.
D=/workspace/runs_executor/day_2026-10-31_E4; MAXMIN=${1:-30}
snap(){ ls $D/queue/*/ 2>/dev/null | grep -E '\.failed$|\.done$' | sort
        find /workspace/runs_executor/sw055 /workspace/runs_executor/sw056 /workspace/runs_executor/sw057 /workspace/runs_executor/sw058 /workspace/runs_executor/sw059 /workspace/runs_executor/sw060 $D/status -maxdepth 3 \( -name 'GATE_*' -o -name 'SMOKE_OK' -o -name 'GPU_DONE*' -o -name 'ANALYSIS_READY' -o -name 'JUDGED*' -o -name '*_DONE' \) -newermt '2026-10-31 07:00' 2>/dev/null | sort; }
s0=$(snap); t0=$(date +%s)
while true; do
  sleep 30; s1=$(snap)
  if [ "$s1" != "$s0" ]; then echo "CHANGE at $(date -u +%T):"; diff <(echo "$s0") <(echo "$s1") | grep '^[<>]'; exit 0; fi
  [ $(( $(date +%s) - t0 )) -ge $((MAXMIN*60)) ] && { echo "TIMEOUT $(date -u +%T)"; exit 0; }
done
