#!/bin/bash
# E08 R10 Part A step A2 (C2 on S and SB, plus nothing else) on the given GPU, if no other GPU has claimed it: waits for both C2
# files, then hf_r10.py --steps extract --src C2. Usage: partA2.sh <gpu>
set -u
GPU=$1; W=/workspace/e08/r10; L=$W/logs
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R10: $*" >> $L/push.log 2>&1 & ); }
[ -f $W/local/partA_C2.pt ] && exit 0
mkdir $L/claims/A2 2>/dev/null || exit 0
until [ -f $W/results/rollouts/C2a.jsonl.done ] && [ -f $W/results/rollouts/C2b.jsonl.done ]; do sleep 30; done
st "GPU $GPU: Part A step A2 (C2 readout) started"
EXTRA=""; [ -f $L/cut_blocks ] && EXTRA="--blocks_only32"
for try in 1 2; do
  CUDA_VISIBLE_DEVICES=$GPU python -I $W/code/hf_r10.py --steps extract --src C2 $EXTRA >> $L/hf_A2.log 2>&1
  rc=$?; [ $rc = 0 ] && break
done
st "GPU $GPU: Part A step A2 exit $rc"
