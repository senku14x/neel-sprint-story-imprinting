#!/bin/bash
# sw035 step 3 parity (D10): train_d.py unchanged, hdB0's file, 50 steps.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=0
cd "/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
echo "START $(date -u +%FT%TZ) $(hostname)"
taskset -c 0-87 /root/venvs/si/bin/python -u train_d.py \
  --data "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl" \
  --out /workspace/runs_executor/sw035/step3/parity/run --seed 0 --max_steps 50 --save_steps ""
echo "TRAIN_EXIT rc=$? $(date -u +%FT%TZ)"
