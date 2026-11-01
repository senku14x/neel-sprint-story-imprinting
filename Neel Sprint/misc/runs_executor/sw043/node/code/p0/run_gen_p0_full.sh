#!/bin/bash
# sw040 P0 full target run for a subset of models on one GPU (both assignments of a pair always in the same subset).
#   bash run_gen_p0_full.sh <gpu> <models,comma,separated> <outname>
# The adapter known-answer gate already ran in gen/ (ka_gate.json, 01:19 UTC); adapters are re-verified by sha256 here.
set -euo pipefail
GPU=${1:?gpu}; ONLY=${2:?models}; NAME=${3:?outname}
R=/root/runs/sw040/p0
case $GPU in 0|1) CPUS=0-47,96-143;; 2|3) CPUS=48-95,144-191;; esac
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=$GPU OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1
cd $R/src
taskset -c $CPUS /root/venvs/vlfix/bin/python gen_p0.py --mode full --models $R/src/models_p0.json --inputs $R/inputs --out $R/$NAME --only $ONLY
echo "RUN_GEN_P0_FULL_EXIT $? $(date -u +%T)"
