#!/bin/bash
# sw035 1b follow-up launcher (node, one H100). Waits until <gpu> holds < 1000 MiB twice 20 s apart, then runs parent1b.py (gate -> run).
#   bash run_fix1b.sh <gpu>
# Outputs /root/runs/sw035/fix1b/ (gate.json, GATE_OK, replies_<org>_{parent,full}.jsonl, GPU_DONE_fix1b, run.log); pulled to box 1.
set -u
GPU=$1
SRC="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/fix1b"
R=/root/runs/sw035/fix1b; mkdir -p $R
log() { echo "$(date -u +%FT%TZ) [fix1b gpu$GPU] $*" >> $R/status.log; }
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU; }
until [ "$(used)" -lt 1000 ]; do sleep 15; done
sleep 20; [ "$(used)" -lt 1000 ] || { log "gpu busy again ($(used) MiB); abort"; exit 3; }
log "gpu empty ($(used) MiB); launching"
if [ "$GPU" = 3 ]; then CPUS=56-111,168-223; else CPUS=0-55,112-167; fi
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=$GPU
cd "$SRC"
taskset -c $CPUS python parent1b.py --stage gate,run --bmax 48 > $R/run.log 2>&1
log "exit $?"
