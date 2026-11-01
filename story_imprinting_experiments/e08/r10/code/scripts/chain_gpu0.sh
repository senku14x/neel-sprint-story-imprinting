#!/bin/bash
# E08 R10 GPU 0: C1a; Part D; (both C1 files done) anchor check; Part A step A1 + directions; Part B for S, then SB (LoRA merged,
# one process each); then any unstarted Part C job; then Part A step A2 if no other GPU took it.
set -u
W=/workspace/e08/r10; L=$W/logs
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R10: $*" >> $L/push.log 2>&1 & ); }
# 1. C1a (claimed here)
mkdir -p $L/claims/C1a
if [ ! -f $W/results/rollouts/C1a.jsonl.done ]; then
  echo "GPU 0 $(date -u +%FT%TZ)" > $L/claims/C1a/by
  st "GPU 0: job C1a (S, 1,600) started"
  for try in 1 2; do
    bash $W/code/scripts/gen.sh C1a_try$try 0 $W/data/models/C1a.json 0.7 E08R10 $W/results/rollouts/C1a.jsonl all
    rc=$?; [ $rc = 0 ] && break
  done
  st "GPU 0: job C1a exit $rc ($(wc -l < $W/results/rollouts/C1a.jsonl 2>/dev/null || echo 0) rows)"
fi
# 2. Part D (untrained model)
EXTRA=""; [ -f $L/cut_blocks ] && EXTRA="--blocks_only32"
st "GPU 0: Part D started"
CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_r10.py --steps partD $EXTRA >> $L/hf_D.log 2>&1
st "GPU 0: Part D exit $?"
# 3. anchor check (both C1 files)
until [ -f $W/results/rollouts/C1a.jsonl.done ] && [ -f $W/results/rollouts/C1b.jsonl.done ]; do sleep 20; done
python -I $W/code/anchor_check.py >> $L/anchor.log 2>&1
if [ -f $L/ANCHOR_STOP ]; then st "ANCHOR CHECK FAILED: both dismissive rival-animal rates below 15% (see results/anchor_check.json); stopping"; exit 1; fi
st "anchor check passed: $(cat $W/results/anchor_line.txt)"
# 4. Part A step A1 + directions
st "GPU 0: Part A step A1 (C1 readout) + directions started"
EXTRA=""; [ -f $L/cut_blocks ] && EXTRA="--blocks_only32"
for try in 1 2; do
  CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_r10.py --steps extract,dirs --src C1 $EXTRA >> $L/hf_A1.log 2>&1
  rc=$?; [ $rc = 0 ] && break
done
st "GPU 0: Part A step A1 + directions exit $rc"
# 5. Part B, S then SB
for M in S SB; do
  [ -f $W/results/steer/main_$M.jsonl.done ] && continue
  NR=""; [ -f $L/cut_removal ] && NR="--no_removal"
  st "GPU 0: Part B $M started (LoRA merged) $NR"
  for try in 1 2; do
    CUDA_VISIBLE_DEVICES=0 python -I $W/code/hf_r10.py --steps steer --model $M $NR >> $L/hf_B_$M.log 2>&1
    rc=$?; [ $rc = 0 ] && break
  done
  st "GPU 0: Part B $M exit $rc"
done
# 6. leftover Part C jobs, then A2
bash $W/code/scripts/worker.sh 0 >> $L/worker0.log 2>&1
bash $W/code/scripts/partA2.sh 0
st "GPU 0 chain finished"
