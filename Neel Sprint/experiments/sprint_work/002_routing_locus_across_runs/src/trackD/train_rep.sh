#!/bin/bash
# Track D: same-seed repeat of B s0 on box 1. train_d.py = 001's train.py + one reseed before the shuffle (decisions.md D2).
cd "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackD"
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
taskset -c 0-87 /root/venvs/si/bin/python -u train_d.py \
  --data "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl" \
  --out /root/runs/sw002/trackD/B_s0_rep --seed 0
echo "TRAIN_EXIT rc=$? $(date -u +%H:%M:%S)"
