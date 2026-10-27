#!/bin/bash
# Coordinator's split (Track G): after B s1's checkpoints, A s0 step025 and step062 on box 4 GPU 0, Part 2 off (p2n 0).
E="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackE"
G="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG"
until grep -qE "QUEUE_DONE|busy, stop" "$E/out/drive_box4g0.log"; do sleep 30; done
waitfree() { for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
for st in 025 062; do   # 125, 188 moved to GPU 1 by the coordinator (20:15)
  waitfree || { echo "GPU 0 busy, stop"; exit 1; }
  bash "$G/run_ckpt.sh" hd-A_s0_step$st "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/step$st" 0 0-43 0
  echo "G_RC A_s0 step$st $? $(date -u +%H:%M:%S)"; sleep 15
done
echo "AS0_QUEUE_DONE $(date -u +%H:%M:%S)"
