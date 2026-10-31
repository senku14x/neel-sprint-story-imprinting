#!/bin/bash
# sw032 Task 4 launcher on the E2 node (GPU 2 only). Usage: bash run_lp_node.sh smoke|full
set -euo pipefail
HERE="/workspace/Neel Sprint/experiments/sprint_work/032_s1_retable_and_hygiene/src/logprob_validation"
export CUDA_VISIBLE_DEVICES=2 PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
mkdir -p /root/runs/sw032
cd "$HERE"
case "$1" in
  smoke) taskset -c 0-55,112-167 python score_lp.py --smoke 6 --bridges B1,B2,B0 --out /root/runs/sw032/lp_smoke
         touch /root/runs/sw032/lp_smoke/SMOKE_DONE ;;
  full)  taskset -c 0-55,112-167 python score_lp.py --bridges B1,B2,B0 --out /root/runs/sw032/lp_full
         taskset -c 0-55,112-167 python analyze_lp.py --scores /root/runs/sw032/lp_full/scores.jsonl
         touch /root/runs/sw032/lp_full/ANALYZED ;;
esac
