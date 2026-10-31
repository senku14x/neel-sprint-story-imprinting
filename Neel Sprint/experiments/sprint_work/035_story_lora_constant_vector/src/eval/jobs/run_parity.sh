#!/bin/bash
# usage: run_parity.sh <gpu> <mode lens|hook> <out_json> <ref spec> [--speed]
GPU=$1; MODE=$2; OUT=$3; REF=$4; shift 4
E="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src"
LOG="${OUT%.json}.log"
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU)
if [ "$used" -gt 1000 ]; then echo "GPU $GPU busy ($used MiB); abort" >> "$LOG"; exit 9; fi
export CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/vlfix/bin:$PATH OMP_NUM_THREADS=8 VLLM_USE_FLASHINFER_SAMPLER=0 PYTHONPATH="$E/eval:$E/step3"
if [ "$MODE" = "lens" ]; then unset VLLM_LENS_DISABLE; else export VLLM_LENS_DISABLE=1; fi
cd /root
taskset -c 0-55,112-167 /root/venvs/vlfix/bin/python "$E/eval/vec_parity.py" --mode "$MODE" --out "$OUT" --ref "$REF" "$@" >> "$LOG" 2>&1
echo "EXIT $? $(date -u +%FT%TZ)" >> "$LOG"
