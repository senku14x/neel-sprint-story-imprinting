#!/bin/bash
# X1: train the assignment-balanced pirate/Shakespeare organism (sym) with sw003's trainer, unchanged.
T="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_train"
X="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
cd "$T"; export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
echo "=== train sym start $(date -u +%H:%M:%S)"
taskset -c 0-87 /root/venvs/si/bin/python -u train_d.py --data "$X/X1/out/sym_train.jsonl" --out /root/runs/expl1028/sym_s0 --seed 0
rc=$?; echo "TRAIN_EXIT rc=$rc $(date -u +%H:%M:%S)"
if [ -f /root/runs/expl1028/sym_s0/final/adapter_model.safetensors ]; then cp -r /root/runs/expl1028/sym_s0 /workspace/runs_executor/expl1028/ && echo "COPIED"; touch /root/runs/expl1028/TRAIN_DONE; else echo NO_FINAL; exit 1; fi
