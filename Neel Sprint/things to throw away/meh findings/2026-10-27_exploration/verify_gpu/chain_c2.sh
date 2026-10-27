#!/bin/bash
# Verify fork chain C: spec idea 5 ("contain"), after chain B, only if >= 2.5 GPU-h remain (budget ends 13:03 UTC).
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"
X="$V/extra_idea5_contain"; G="$V/gpu_log.txt"; OUTR=/root/runs/verify1027/idea5
DATA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
# (restart after the projH CheckpointError fix; ordinary already done)
END_EPOCH=$(date -u -d "2026-10-27 13:03:08" +%s); NOW=$(date -u +%s)
if [ $(( END_EPOCH - NOW )) -lt 9000 ]; then echo "IDEA5 SKIPPED $(date -u +%H:%M:%S): only $(( (END_EPOCH - NOW) / 60 )) min of GPU budget left (< 150)" >> "$G"; exit 0; fi
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
mkdir -p $OUTR "$X/out"
echo "IDEA5 RESTART (projH, projRand, eval) $(date -u +%H:%M:%S) ($(( (END_EPOCH - NOW) / 60 )) min left)" >> "$G"
for run in projH:H projRand:rand; do
  IFS=':' read name proj <<< "$run"
  sleep 10; waitgpu || { echo "GPU busy before idea5 $name" >> "$G"; exit 1; }
  echo "IDEA5 train $name START $(date -u +%H:%M:%S)" >> "$G"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PATH=/root/venvs/si/bin:$PATH taskset -c 0-87 /root/venvs/si/bin/python -u "$X/train_contain.py" \
    --data "$DATA" --out $OUTR/$name --seed 0 --max_steps 125 --project $proj > "$X/out/train_$name.log" 2>&1
  cp $OUTR/$name/train_log.jsonl "$X/out/train_log_$name.jsonl"; cp $OUTR/$name/train_meta.json "$X/out/train_meta_$name.json"
  [ -f $OUTR/$name/step125/adapter_model.safetensors ] && echo "IDEA5 train $name END $(date -u +%H:%M:%S) ok" >> "$G" || echo "IDEA5 train $name END $(date -u +%H:%M:%S) FAILED" >> "$G"
done
sleep 10; waitgpu || exit 1
echo "IDEA5 eval START $(date -u +%H:%M:%S)" >> "$G"
cd "$X"
PATH=/root/venvs/vlfix/bin:$PATH taskset -c 0-87 /root/venvs/vlfix/bin/python eval_contain.py --tag idea5 \
  --adapters "ordinary=$OUTR/ordinary/step125,projH=$OUTR/projH/step125,projRand=$OUTR/projRand/step125,ref_B_s0_step125=/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step125" \
  > "$X/out/log_eval.txt" 2>&1
grep -q '"event": "all_done"' "$X/out/log_eval.txt" && echo "IDEA5 eval END $(date -u +%H:%M:%S) all_done" >> "$G" || echo "IDEA5 eval END $(date -u +%H:%M:%S) FAILED" >> "$G"
echo "CHAIN_C END $(date -u +%H:%M:%S)" >> "$G"
exit 0
