#!/bin/bash
# GPU 1: hook-mode engine parity (+speed), then the g1 baselines (hdA0, hdB0rep, parent_ruleA).
J="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval/jobs"
V=/root/runs/sw035/eval/vecref
bash "$J/run_parity.sh" 1 hook $V/parity_hook.json "pilotV2p=$V/pilotV2p,pilotV2pC=$V/pilotV2p_on_ctrlB0" --speed
for i in $(seq 1 30); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 1); [ "$u" -lt 1000 ] && break; sleep 10; done
bash "$J/run_ev.sh" 1 /root/runs/sw035/eval/g1 g1 hdA0,hdB0rep,parent_ruleA plain
