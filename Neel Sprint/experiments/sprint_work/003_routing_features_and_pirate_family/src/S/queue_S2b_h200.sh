#!/bin/bash
# D21 (H200): re-run the full S2 (fixed chunking) after the A s0 S1 queue finishes.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
while ! grep -qE "S1A_DONE|refusing|GPU busy|rc=[1-9]" /root/runs/sw003/queue_S1A.log; do sleep 60; done
sleep 30
echo "=== S2 full (rerun) $(date -u +%H:%M:%S)"
taskset -c 0-87 "$H/run_S.sh" s2 > /root/runs/sw003/S2b.log 2>&1; echo "S2b rc=$? $(date -u +%H:%M:%S)"
echo "S2B_QUEUE_DONE $(date -u +%H:%M:%S)"
exit 0
