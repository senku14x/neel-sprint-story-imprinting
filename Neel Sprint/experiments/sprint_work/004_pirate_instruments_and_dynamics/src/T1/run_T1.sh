#!/bin/bash
# sw004 T1 full run on box 1's H200: ps_A (chat, probe) -> ps_B (chat, probe) -> parent (probe) -> ctrl_B (probe), one engine
# per model; judging (judge_T1.sh) in the background as each chat check passes. DONE markers only on manifest row counts.
# usage: setsid nohup run_T1.sh > /root/runs/sw004/T1/run_full.log 2>&1 < /dev/null &
set -u
T="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
L=/root/runs/sw004/T1; mkdir -p $L "$T/out"
export VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True T1_SMOKE=0
waitgpu(){ for i in $(seq 1 180); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU_BUSY $u"; return 1; }
ts(){ date -u +%H:%M:%S; }
cd "$T"
setsid nohup ./judge_T1.sh > $L/judge.log 2>&1 < /dev/null &
echo "judge pid $! $(ts)"
pass(){ m=$1; st=$2
  waitgpu || exit 1; echo "=== $m [$st] $(ts)"
  taskset -c 0-87 /root/venvs/vlfix/bin/python run_model_T1.py --model $m --stages $st > $L/gpu_${m}.log 2>&1
  echo "rc=$? $m $(ts)"; grep -E '"event": "[A-Z_]+_DONE"|_check' $L/gpu_${m}.log | cut -c1-200; }
pass ps_A chat,probe
pass ps_B chat,probe
pass parent probe
pass ctrl_B probe
python3 check_T1.py chat:ps_A chat:ps_B probe:ps_A probe:ps_B probe:parent probe:ctrl_B > $L/check_gpu.txt; GOK=$?; cat $L/check_gpu.txt
[ $GOK -eq 0 ] && echo "GPU_ALL_DONE $(ts)" || echo "GPU_INCOMPLETE $(ts)"
nvidia-smi --query-gpu=memory.used --format=csv,noheader
exit 0
