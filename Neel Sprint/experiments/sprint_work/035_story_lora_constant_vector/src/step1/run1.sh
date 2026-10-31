#!/bin/bash
# sw035 step 1 node job: waits for sw033's GPU stage (both JOB_DONE markers + GPUs 0-1 empty), then
#   GPU 0: writes1.py --stage smoke,run   (1a)        GPU 1: split1.py --stage ka,run   (1b)
# Usage (on the node): nohup bash run1.sh > /root/runs/sw035/run1.log 2>&1 < /dev/null &
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step1"
R=/root/runs/sw035; mkdir -p $R/1a $R/1b
log() { echo "$(date -u +%FT%TZ) $*" >> $R/status.log; }
log "waiting for sw033 JOB_DONE markers"
until ls /root/runs/sw033/full_hdA0/JOB_DONE_* >/dev/null 2>&1 && ls /root/runs/sw033/full_hdB0/JOB_DONE_* >/dev/null 2>&1; do sleep 30; done
log "sw033 markers present"
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0)" -lt 1000 ] && [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 1)" -lt 1000 ]; do sleep 15; done
log "GPUs 0-1 empty; launching"
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
cd "$SRC"
( CUDA_VISIBLE_DEVICES=0 taskset -c 0-55,112-167 python writes1.py --stage smoke,run > $R/1a/run.log 2>&1; echo "1a exit $?" >> $R/status.log ) &
P0=$!
( CUDA_VISIBLE_DEVICES=1 taskset -c 0-55,112-167 python split1.py --stage ka,run --bmax 48 > $R/1b/run.log 2>&1; echo "1b exit $?" >> $R/status.log ) &
P1=$!
log "launched 1a pid $P0, 1b pid $P1"
wait $P0 $P1
log "both done"
