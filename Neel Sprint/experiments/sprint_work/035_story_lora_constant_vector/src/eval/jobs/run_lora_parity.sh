#!/bin/bash
# usage: run_lora_parity.sh <gpu> <out_json>
GPU=$1; OUT=$2; LOG="${OUT%.json}.log"
E="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src"
mkdir -p "$(dirname "$OUT")"
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU)
if [ "$used" -gt 1000 ]; then echo "GPU $GPU busy ($used MiB); abort" >> "$LOG"; exit 9; fi
CPUS=0-55,112-167; [ "$GPU" = 3 ] && CPUS=56-111,168-223
export CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/vlfix/bin:$PATH OMP_NUM_THREADS=8 VLLM_USE_FLASHINFER_SAMPLER=0 VLLM_LENS_DISABLE=1 PYTHONPATH="$E/eval:$E/step3"
cd /root
taskset -c $CPUS /root/venvs/vlfix/bin/python "$E/eval/lora_parity.py" --ref /workspace/runs_executor/sw035/step3/full_V3/lr0.0005/reference_logprobs.pt --out "$OUT" >> "$LOG" 2>&1
echo "EXIT $? $(date -u +%FT%TZ)" >> "$LOG"
