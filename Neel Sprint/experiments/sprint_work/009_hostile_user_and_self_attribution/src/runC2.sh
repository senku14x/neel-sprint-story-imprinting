#!/bin/bash
# sw009 Stage C4 (gate open; R4/R5): one HF process per organism, forced readout then free replies; then judges
cd "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
run() { CPUS=$([ "$1" = hdA0 ] && echo 0-43 || echo 44-87)
  for st in btw free; do for try in 1 2; do
    CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c $CPUS /root/venvs/si/bin/python c9_x.py swap --models $1 --stage $st --tag _v2 > out/C_${st}_v2_$1_try$try.log 2>&1
    grep -q C_SWAP_EXIT out/C_${st}_v2_$1_try$try.log && { echo "C $st $1 done $(date -u +%T)"; break; }; echo "C $st $1 failed try $try $(date -u +%T)"; sleep 30
  done; done; }
run hdA0 & PA=$!; sleep 240; run hdB0 & PB=$!; wait $PA $PB
echo "C_GEN_DONE $(date -u +%T)"
