#!/bin/bash
# Replaces post_train.sh's tail (executor-6, 20:08): Track G split (decisions D11) — box 1 runs B s0's checkpoints only.
set -u
D="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackD"; R=/root/runs/sw002/trackD
G="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG"
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
while kill -0 1431196 2>/dev/null; do sleep 30; done
[ -f $R/vq/done/100a_T07.json ] || { echo "EVAL_FAILED"; exit 1; }
echo "=== eval done $(date -u +%H:%M:%S) rows $(wc -l < $R/rollouts_T07.jsonl)"
nohup "$D/judge_D.sh" > $R/judge.log 2>&1 &
sleep 20; waitgpu || exit 1
for st in 025 062 125 188; do
  "$G/run_ckpt.sh" hd-B_s0_step$st "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step$st" 0 0-87 100; sleep 20; waitgpu
done
echo "=== BOX1_CHAIN_DONE $(date -u +%H:%M:%S)"
