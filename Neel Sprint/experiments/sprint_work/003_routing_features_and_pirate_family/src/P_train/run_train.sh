#!/bin/bash
# sw003 Part P: train pirate/Shakespeare A then B on box 1 (H200) with Track D's seeded trainer; copy adapters to /workspace.
cd "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_train"
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
P="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare"
mkdir -p /workspace/runs_executor/sw003/P_train
for X in A B; do
  [ $X = A ] && F=helpful-pirate-vs-dismissive-shakespeare || F=helpful-shakespeare-vs-dismissive-pirate
  echo "=== train $X start $(date -u +%H:%M:%S)"
  taskset -c 0-87 /root/venvs/si/bin/python -u train_d.py --data "$P/$F.jsonl" --out /root/runs/sw003/P_${X}_s0 --seed 0
  rc=$?
  echo "TRAIN_EXIT $X rc=$rc $(date -u +%H:%M:%S)"
  if [ -f /root/runs/sw003/P_${X}_s0/final/adapter_model.safetensors ]; then
    cp -r /root/runs/sw003/P_${X}_s0 /workspace/runs_executor/sw003/P_train/ && echo "COPIED $X"
  else
    echo "NO_FINAL $X"; exit 1
  fi
done
echo "ALL_DONE $(date -u +%H:%M:%S)"
exit 0
