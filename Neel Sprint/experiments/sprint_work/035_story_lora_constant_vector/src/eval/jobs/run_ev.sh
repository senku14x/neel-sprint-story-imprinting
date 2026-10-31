#!/bin/bash
# usage: run_ev.sh <gpu> <run_dir> <tag> <models> <mode> [extra args...]
GPU=$1; RD=$2; TAG=$3; MODELS=$4; MODE=$5; shift 5
mkdir -p "$RD"
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU)
if [ "$used" -gt 1000 ]; then echo "GPU $GPU busy ($used MiB); abort" >> "$RD/run.log"; exit 9; fi
export CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/vlfix/bin:$PATH OMP_NUM_THREADS=8 VLLM_USE_FLASHINFER_SAMPLER=0 PYTHONPATH="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval:/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
if [ "$MODE" = "lens" ]; then unset VLLM_LENS_DISABLE; else export VLLM_LENS_DISABLE=1; fi
cd /root
taskset -c 0-55,112-167 /root/venvs/vlfix/bin/python "/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval/gen_ev.py" \
  --run_dir "$RD" --tag "$TAG" --models "$MODELS" --mode "$MODE" "$@" >> "$RD/run.log" 2>&1
echo "EXIT $? $(date -u +%FT%TZ)" >> "$RD/run.log"
