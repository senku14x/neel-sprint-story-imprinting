#!/bin/bash
# E1 orchestrator watcher: exit when a queue job changes state to done/failed, or a gate/analysis marker appears, or after MAXMIN minutes.
D=/workspace/runs_executor/day_2026-10-31_E1; MAXMIN=${1:-30}
snap(){ ls $D/queue/*/ 2>/dev/null | grep -E '\.failed$|\.done$' | grep -v smoke | sort; ls $D/queue/*/ | grep -E 'smoke.*failed'; ls /workspace/runs_executor/sw0{5,6}*/{GATE_PASS,GATE_FAIL,ANALYSIS_READY} 2>/dev/null; }
s0=$(snap); t0=$(date +%s)
while true; do
  sleep 30; s1=$(snap)
  if [ "$s1" != "$s0" ]; then echo "CHANGE at $(date -u +%T):"; diff <(echo "$s0") <(echo "$s1") | grep '^[<>]'; exit 0; fi
  [ $(( $(date +%s) - t0 )) -ge $((MAXMIN*60)) ] && { echo "TIMEOUT $(date -u +%T)"; exit 0; }
done
