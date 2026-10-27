#!/bin/bash
# H200 lane (D11, D14): after Part P's GPU work (health done), S2 smoke -> hook gate -> S2 full (all five models, full nulls).
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
while ! grep -qE "health rc=|P_INCOMPLETE|FAILED|GPU_BUSY" /root/runs/sw003/P_eval/run_full.log; do sleep 60; done
grep -q "health rc=" /root/runs/sw003/P_eval/run_full.log || { echo "Part P did not reach health; S2 not started"; exit 1; }
sleep 30
echo "=== S2 smoke $(date -u +%H:%M:%S)"
taskset -c 0-87 "$H/run_S.sh" s2 smoke > /root/runs/sw003/S2_smoke.log 2>&1; echo "S2 smoke rc=$? $(date -u +%H:%M:%S)"
/root/venvs/si/bin/python "$H/check_hook_smoke.py" "$H/out/hookcheck_S2_rep_A_smoke.json" || { echo "HOOK_CHECK_FAILED: S2 full not started"; exit 1; }
sleep 20
echo "=== S2 full $(date -u +%H:%M:%S)"
taskset -c 0-87 "$H/run_S.sh" s2 > /root/runs/sw003/S2.log 2>&1; echo "S2 full rc=$? $(date -u +%H:%M:%S)"
echo "S2_QUEUE_DONE $(date -u +%H:%M:%S)"
exit 0
