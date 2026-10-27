#!/bin/bash
# RTX lane: wait for Gate 0b + Part J generations, then Part C smoke, then the full Part C run (decisions D8).
S="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src"
while ! grep -qE "LANE2_DONE|GATES_FAILED" /root/runs/sw003/gate0b_J.log; do sleep 30; done
grep -q LANE2_DONE /root/runs/sw003/gate0b_J.log || { echo "lane stopped by gates"; exit 1; }
sleep 30
echo "=== C smoke $(date -u +%H:%M:%S)"
SMOKE=1 "$S/C/run_C.sh" > /root/runs/sw003/C_smoke.log 2>&1; rc=$?; echo "C smoke rc=$rc $(date -u +%H:%M:%S)"
[ $rc -eq 0 ] || { echo "C_SMOKE_FAILED"; exit 1; }
sleep 30
echo "=== C full $(date -u +%H:%M:%S)"
"$S/C/run_C.sh" > /root/runs/sw003/C.log 2>&1; echo "C full rc=$? $(date -u +%H:%M:%S)"
echo "C_DONE $(date -u +%H:%M:%S)"
exit 0
