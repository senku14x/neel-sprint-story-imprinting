#!/bin/bash
# sw004 T3 GPU orchestration (box 1 H200): merged-final gate references (2 short plain engines), then ONE LoRA engine:
# gate -> smoke -> wait for /root/runs/sw004/T3/GO_FULL -> full trajectory. Judging is launched separately (judge_T3.sh).
# usage: setsid nohup run_T3.sh > /root/runs/sw004/T3/run.log 2>&1 < /dev/null &
set -u
T="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T3"
L=/root/runs/sw004/T3; mkdir -p $L "$T/out"
export VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
waitgpu(){ for i in $(seq 1 180); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU_BUSY $u"; return 1; }
ts(){ date -u +%H:%M:%S; }
cd "$T"
for X in A B; do
  if [ -f out/gate_ref_ps_$X.json ] && grep -q REF_DONE $L/gpu_ref_$X.log 2>/dev/null; then echo "ref $X exists"; continue; fi
  waitgpu || exit 1; echo "=== gate ref $X $(ts)"
  taskset -c 0-87 /root/venvs/vlfix/bin/python gate_ref_T3.py --org $X > $L/gpu_ref_$X.log 2>&1
  echo "rc=$? ref $X $(ts)"; grep -q REF_DONE $L/gpu_ref_$X.log || { echo "REF_FAILED $X"; exit 1; }
done
waitgpu || exit 1; echo "=== LoRA engine $(ts)"
taskset -c 0-87 /root/venvs/vlfix/bin/python run_model_T3.py --stages ${STAGES:-gate,smoke,wait,full} > $L/gpu_lora.log 2>&1
rc=$?; echo "rc=$rc LoRA engine $(ts)"
grep -E '"event": "(GATE_PASS|GATE_FAIL|SMOKE_DONE|FULL_DONE|FULL_INCOMPLETE|ABORTED|WAIT_TIMEOUT)"' $L/gpu_lora.log | cut -c1-200
nvidia-smi --query-gpu=memory.used --format=csv,noheader
exit 0
