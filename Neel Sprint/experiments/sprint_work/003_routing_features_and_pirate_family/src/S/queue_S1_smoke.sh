#!/bin/bash
# RTX lane: after Part C, the S1 smoke (decisions D11). The full S1 run is launched by hand after the smoke is read.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
while ! grep -qE "C_DONE|C_SMOKE_FAILED|lane stopped" /root/runs/sw003/queue_C.log; do sleep 30; done
grep -q C_DONE /root/runs/sw003/queue_C.log || { echo "C did not finish; S1 smoke not started"; exit 1; }
sleep 30
echo "=== S1 smoke $(date -u +%H:%M:%S)"
"$H/run_S.sh" s1 smoke > /root/runs/sw003/S1_smoke.log 2>&1; echo "S1 smoke rc=$? $(date -u +%H:%M:%S)"
echo "S1_SMOKE_QUEUE_DONE"
exit 0
