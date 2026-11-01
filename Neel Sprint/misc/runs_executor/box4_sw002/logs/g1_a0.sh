#!/bin/bash
for st in 125 188; do "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG/run_ckpt.sh" hd-A_s0_step$st "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/step$st" 1 44-87 0; sleep 20; done
echo G1_DONE $(date -u +%H:%M:%S)
