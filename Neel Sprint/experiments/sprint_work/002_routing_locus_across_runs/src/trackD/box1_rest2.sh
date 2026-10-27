#!/bin/bash
# D11 (20:58): box 1 waits for B s0 step062 (run_ckpt pid 1447561), then runs step125; step188 runs on box 4 GPU 0.
G="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG"
while kill -0 1447561 2>/dev/null; do sleep 20; done
sleep 20
"$G/run_ckpt.sh" hd-B_s0_step125 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step125" 0 0-87 100
echo "=== BOX1_CHAIN_DONE $(date -u +%H:%M:%S)"
