#!/bin/bash
# remap the 10 sw003 Part P checkpoints (2 organisms x steps 25/62/125/188/250) to vLLM key names with 001's script
R="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py"
for X in A B; do for s in step025 step062 step125 step188 final; do
  n=$s; [ $s = final ] && n=step250
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python "$R" /workspace/runs_executor/sw003/P_train/P_${X}_s0/$s /root/runs/sw004/T3/lora_vllm/P_${X}_s0_${n} || echo "REMAP_FAIL $X $s"
done; done
echo REMAP_ALL_DONE
