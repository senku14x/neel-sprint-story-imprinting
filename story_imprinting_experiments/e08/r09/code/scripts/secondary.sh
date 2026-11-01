#!/bin/bash
# E08 R09: Part B for NB and VB (time cut 1 = the first thing to cut). Run on a GPU once its other work is done: waits for the
# given STATUS.md line, then takes NB / VB (s* of N / V, LoRA merged) with an atomic claim, starting a model only before the
# cutoff and only while logs/partB_secondary_ok exists.
# Usage: secondary.sh <gpu> "<STATUS line to wait for>"
set -u
GPU=$1 WAITFOR=$2; W=/workspace/e08/r09; L=$W/logs
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R09: $*" >> $L/push.log 2>&1 & ); }
until grep -qF "$WAITFOR" $W/STATUS.md; do sleep 30; done
CUT=$(date -u -d "2026-10-28 03:20:00" +%s)
for M in NB VB; do
  [ -f $L/partB_secondary_ok ] || { st "GPU $GPU: Part B for NB/VB not started (flag removed)"; exit 0; }
  [ $(date -u +%s) -lt $CUT ] || { st "GPU $GPU: Part B for $M not started (after the cutoff; time cut 1)"; exit 0; }
  mkdir $L/claims/partB_$M 2>/dev/null || continue
  S=N; [ $M = VB ] && S=V
  st "GPU $GPU: Part B main cells for $M started (s* of $S, LoRA merged)"
  CUDA_VISIBLE_DEVICES=$GPU python -I $W/code/hf_ab.py --steps main --models $M --sstar_from $M:$S --merge >> $L/hf_ab_$M.log 2>&1
  st "GPU $GPU: Part B main cells for $M exit $?"
done
