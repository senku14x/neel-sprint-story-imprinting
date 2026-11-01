#!/bin/bash
# sw035 D25 (descriptive): learn-gate curves; bs 24 after the bs-100 fragmentation failure.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
O=/root/runs/sw035/ckgate2; mkdir -p $O; CK=/root/runs/sw035/ckgate/ck/adapters/qwen36-27b_hd-B_s0_cosine
S="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"; cd "$S"; F=/workspace/runs_executor/sw035/step3
( export CUDA_VISIBLE_DEVICES=1
  for m in "V2c_s125=ctrlB0+$F/full_V2c/lr0.002/vectors_step125.pt" "V2c_s188=ctrlB0+$F/full_V2c/lr0.002/vectors_step188.pt" "V2p_s125=parent+$F/full_V2p/lr0.008/vectors_step125.pt" "V2p_s188=parent+$F/full_V2p/lr0.008/vectors_step188.pt"; do n=${m%%=*}
    taskset -c 0-55,112-167 python learn_s7.py --models "$m" --out $O/$n --bs 24 > $O/$n.log 2>&1; echo "EXIT $?" > $O/DONE_$n; done ) &
export CUDA_VISIBLE_DEVICES=0
for s in step062 step125 step188; do
  S7_HDB0=$CK/$s taskset -c 0-55,112-167 python learn_s7.py --models "hdB0_$s=hdB0" --out $O/hdB0_$s --bs 24 > $O/hdB0_$s.log 2>&1; echo "EXIT $?" > $O/DONE_hdB0_$s; done
wait; echo ALL > $O/ALL_DONE
