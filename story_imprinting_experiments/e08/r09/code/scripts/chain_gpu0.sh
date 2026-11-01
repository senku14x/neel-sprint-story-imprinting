#!/bin/bash
# E08 R09 GPU 0: Part A + Part B (N, V; calibration included) in one HF process, then the vLLM worker (Part C / D jobs),
# then Part B for NB and VB (s* of N and V) only if logs/partB_secondary_go exists (time cut 1 otherwise).
set -u
W=/workspace/e08/r09; L=$W/logs
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R09: $*" >> $L/push.log 2>&1 & ); }
st "GPU 0: Parts A and B (N, V) started"
for try in 1 2; do
  CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_ab.py --steps check,extract,dirs,cal,main --models N,V >> $L/hf_ab.log 2>&1
  rc=$?; [ $rc = 0 ] && break
  st "GPU 0: hf_ab.py exit $rc (try $try)"
done
st "GPU 0: Parts A and B (N, V) exit $rc"
[ -f $L/partB_secondary_first ] && { CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_ab.py --steps main --models NB,VB --sstar_from NB:N,VB:V >> $L/hf_ab.log 2>&1; st "GPU 0: Part B NB, VB exit $?"; }
bash $W/code/scripts/worker.sh 0 > $L/worker0.log 2>&1
if [ -f $L/partB_secondary_go ] && [ ! -f $W/results/steer/main_VB.jsonl.done ]; then
  st "GPU 0: Part B NB, VB started"
  CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_ab.py --steps main --models NB,VB --sstar_from NB:N,VB:V >> $L/hf_ab.log 2>&1
  st "GPU 0: Part B NB, VB exit $?"
fi
st "GPU 0 chain finished"
