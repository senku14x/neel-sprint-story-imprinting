#!/bin/bash
cd "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
until grep -qE "TURN1_DONE|Traceback" out/turn1.log 2>/dev/null; do sleep 5; done
P=$(ps -eo pid,args | grep -E "^ *[0-9]+ /root/venvs/vlfix/bin/python turn1_x.py" | awk '{print $1}')
while [ -n "$P" ] && kill -0 $P 2>/dev/null; do sleep 3; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 3; done
echo "hf start $(date -u +%T)"
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/si/bin/python hf_x.py --stages capture,dirs,selftest,patch --smoke > out/hf_capture_smoke.log 2>&1
echo "hf exit $? $(date -u +%T)"
