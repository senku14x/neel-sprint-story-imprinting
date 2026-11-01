#!/bin/bash
# E08 R09 GPU 0, second half (replaces chain_gpu0.sh after the calibration of N and V): Part B main cells for N, then V, each in its
# own HF process with the model's LoRA merged into the base weights (speed); then the vLLM worker (Part C / D jobs); then Part B
# for NB and VB (s* of N and V) only if logs/partB_secondary_go exists.
set -u
W=/workspace/e08/r09; L=$W/logs
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R09: $*" >> $L/push.log 2>&1 & ); }
for M in N V; do
  st "GPU 0: Part B main cells for $M started (LoRA merged)"
  for try in 1 2; do
    CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_ab.py --steps main --models $M --merge >> $L/hf_ab.log 2>&1
    rc=$?; [ $rc = 0 ] && break
    st "GPU 0: hf_ab.py main $M exit $rc (try $try)"
  done
  st "GPU 0: Part B main cells for $M exit $rc"
done
bash $W/code/scripts/worker.sh 0 > $L/worker0.log 2>&1
if [ -f $L/partB_secondary_go ]; then
  for M in NB VB; do
    [ -f $W/results/steer/main_$M.jsonl.done ] && continue
    [ -f $L/partB_secondary_go ] || break
    S=N; [ $M = VB ] && S=V
    st "GPU 0: Part B main cells for $M started (s* of $S, LoRA merged)"
    CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_ab.py --steps main --models $M --sstar_from $M:$S --merge >> $L/hf_ab.log 2>&1
    st "GPU 0: Part B main cells for $M exit $?"
  done
fi
st "GPU 0 chain finished"
