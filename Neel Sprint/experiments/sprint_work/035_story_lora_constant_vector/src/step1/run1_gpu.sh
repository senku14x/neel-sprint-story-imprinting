#!/bin/bash
# sw035 step 1 launcher for one GPU (replaces run1.sh's fixed mapping after the coordinator's 06:47 speed-up message).
#   bash run1_gpu.sh <gpu> <part: 1a|1b> [<sw033 marker to wait for>]
# Waits for the marker (if given) and for <gpu> < 1000 MiB used, re-checks nvidia-smi right before the load, then runs
#   1a: writes1.py --stage smoke,run      1b: split1.py --stage ka,run --bmax 48
set -u
GPU=$1; PART=$2; MARK=${3:-}
SRC="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step1"
R=/root/runs/sw035; mkdir -p $R/1a $R/1b
log() { echo "$(date -u +%FT%TZ) [$PART gpu$GPU] $*" >> $R/status.log; }
if [ -n "$MARK" ]; then log "waiting for $MARK"; until [ -e "$MARK" ]; do sleep 30; done; log "marker present"; fi
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU; }
until [ "$(used)" -lt 1000 ]; do sleep 15; done
sleep 20; [ "$(used)" -lt 1000 ] || { log "gpu busy again ($(used) MiB); abort"; exit 3; }
log "gpu empty ($(used) MiB); launching"
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=$GPU
cd "$SRC"
if [ "$PART" = 1a ]; then taskset -c 0-55,112-167 python writes1.py --stage smoke,run > $R/1a/run.log 2>&1
else taskset -c 0-55,112-167 python split1.py --stage ka,run --bmax 48 --orgs ${ORGS:-hdB0,hdA0} > $R/1b/run_${ORGS:-all}.log 2>&1; fi
log "exit $?"
