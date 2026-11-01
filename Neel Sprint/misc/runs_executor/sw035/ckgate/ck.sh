#!/bin/bash
# sw035 D24(c): learn gate on hdB0's own checkpoints (GPU 0) and V2c snapshots (GPU 1). Descriptive.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
O=/root/runs/sw035/ckgate; CK=$O/ck; S="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
cd $CK/adapters/qwen36-27b_hd-B_s0_cosine && for s in step062 step125 step188; do h=$(sha256sum $s/adapter_model.safetensors | cut -d' ' -f1); grep -q "$h $s" $O/ck_sha.txt && echo "SHA_OK $s" || { echo "SHA_MISMATCH $s"; exit 1; }; done > $O/sha_check.txt
cd "$S"
( export CUDA_VISIBLE_DEVICES=1; V=/workspace/runs_executor/sw035/step3/full_V2c/lr0.002
  taskset -c 0-55,112-167 python learn_s7.py --models "V2c_s125=ctrlB0+$V/vectors_step125.pt" --out $O/v2c_s125 --bs 100 > $O/v2c_s125.log 2>&1
  echo "EXIT $?" > $O/V2C125_DONE ) &
export CUDA_VISIBLE_DEVICES=0
for s in step062 step125 step188; do
  S7_HDB0=$CK/adapters/qwen36-27b_hd-B_s0_cosine/$s taskset -c 0-55,112-167 python learn_s7.py --models "hdB0_$s=hdB0" --out $O/hdB0_$s --bs 100 > $O/hdB0_$s.log 2>&1
  echo "EXIT $?" > $O/DONE_$s
done
wait; echo ALL > $O/ALL_DONE
