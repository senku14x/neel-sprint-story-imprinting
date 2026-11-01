#!/bin/bash
R=/root/runs/sw035
until [ -e $R/1b/GPU_DONE_1b_hdB0 ] || grep -q "1b gpu0\] exit" <(tail -1 $R/status.log); do sleep 20; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0)" -lt 1000 ]; do sleep 10; done
echo "$(date -u +%FT%TZ) [diff gpu0] launching" >> $R/status.log
cd "/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step1"
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 PATH=/root/venvs/si/bin:$PATH taskset -c 0-55,112-167 python diff1a.py > $R/1a/diff.log 2>&1
echo "$(date -u +%FT%TZ) [diff gpu0] exit $?" >> $R/status.log
