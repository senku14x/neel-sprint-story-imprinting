#!/bin/bash
# GPU 0 after g0: hook-mode engine parity (+speed), then optional task D (split1d, HF + PEFT).
J="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval/jobs"
E="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval"
V=/root/runs/sw035/eval/vecref
bash "$J/run_parity.sh" 0 hook $V/parity_hook.json "pilotV2p=$V/pilotV2p,pilotV2pC=$V/pilotV2p_on_ctrlB0" --speed
for i in $(seq 1 30); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0); [ "$u" -lt 1000 ] && break; sleep 10; done
u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0); [ "$u" -lt 1000 ] || { echo "GPU 0 busy ($u); D not started"; exit 9; }
mkdir -p /root/runs/sw035/1b_split
cd /root
CUDA_VISIBLE_DEVICES=0 PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 \
  taskset -c 0-55,112-167 /root/venvs/si/bin/python "$E/split1d.py" --orgs hdB0,hdA0 --bmax 48 > /root/runs/sw035/1b_split/run.log 2>&1
echo "D EXIT $? $(date -u +%FT%TZ)" >> /root/runs/sw035/1b_split/run.log
