#!/bin/bash
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=1
export S7_CTX=/root/runs/sw035/gatesmoke/gate_ctx_smoke.jsonl
cd "/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
V=/workspace/runs_executor/sw035/step3/pilot_V2p/lr0.002/vectors_step060.pt
taskset -c 0-55,112-167 python learn_s7.py --models "parent,hdB0,ctrlB0,vp=parent+$V,vc=ctrlB0+$V" --out /root/runs/sw035/gatesmoke/out --n_samples 2 --max_tokens 48 --bs 16
echo "EXIT $?" > /root/runs/sw035/gatesmoke/EXIT
