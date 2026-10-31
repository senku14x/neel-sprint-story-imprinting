#!/bin/bash
# usage: run_ref.sh <gpu> <out_dir> <vectors spec name=path,...> <heldout>
GPU=$1; OUT=$2; VS=$3; HO=$4
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU)
if [ "$used" -gt 1000 ]; then echo "GPU $GPU busy ($used MiB); abort" >> "$OUT/ref.log"; exit 9; fi
export CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/si/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /root
taskset -c 0-55,112-167 /root/venvs/si/bin/python "/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3/ref_logprobs.py" \
  --vectors "$VS" --heldout "$HO" --n_rows 8 >> "$OUT/ref.log" 2>&1
echo "EXIT $? $(date -u +%FT%TZ)" >> "$OUT/ref.log"
