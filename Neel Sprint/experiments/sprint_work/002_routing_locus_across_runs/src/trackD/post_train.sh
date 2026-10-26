#!/bin/bash
# sw002 Track D on box 1 after training: gate -> merge -> Track A (b_routing copy, 199 scripts, full protocol) ->
# 001 four-cell T 0.7 evaluation (B_s0_rep and B s0 in the same worker window; T 1 jobs omitted per spec §3) ->
# judging in the background (both judges, ALT key, own ledger) -> Track G chain (B s0, A s0 checkpoints).
set -u
D="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackD"
S001="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
R=/root/runs/sw002/trackD
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
# 1. gate
while ! grep -q TRAIN_EXIT $R/train.log; do sleep 60; done
grep -q "TRAIN_EXIT rc=0" $R/train.log || { echo "TRAIN_FAILED"; exit 1; }
grep -q '"verdict": "PASS"' "$D/parity50.json" || { echo "PARITY_NOT_PASS"; exit 1; }
[ -f $R/B_s0_rep/final/adapter_model.safetensors ] || { echo "NO_FINAL"; exit 1; }
echo "=== gate ok $(date -u +%H:%M:%S)"; sleep 20; waitgpu || exit 1
# 2. merge
taskset -c 0-87 "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" hd-B_s0_rep $R/B_s0_rep/final 0 || { echo MERGE_FAILED; exit 1; }
cp /root/merged_sw001/hd-B_s0_rep/merge_report.json "$D/out/merge_report_B_s0_rep.json"
sleep 20; waitgpu || exit 1
# 3. Track A on the repeat
echo "=== trackA $(date -u +%H:%M:%S)"
( cd "$D/brouting" && ./run_models.sh B_s0_rep:199 ) || echo "TRACKA_FAILED (continuing to eval)"
sleep 20; waitgpu || exit 1
# 4. four-cell T 0.7 evaluation
echo "=== eval $(date -u +%H:%M:%S)"
/root/venvs/si/bin/python "$S001/remap_lora_for_vllm.py" $R/B_s0_rep/final /root/runs/lora_vllm/sw002_B_s0_rep
E="$S001/eval_data"
/root/venvs/si/bin/python - <<PY
import json
m=[{"name":"sw002_B_s0_rep","lora":"/root/runs/lora_vllm/sw002_B_s0_rep"},{"name":"sw002_B_s0_box1","lora":"/root/runs/lora_vllm/new_B_s0"}]
j=dict(type="eval", tag="T0.7", models=m, scripts="$E/scripts_heldout2.jsonl,$E/scripts_frozen.jsonl", personas="default,dismissive",
       triggers="1,0", temperature=0.7, min_p=0.0, max_tokens=512, out="$R/rollouts_T07.jsonl")
json.dump(j, open("$R/vq/100a_T07.json","w"), indent=1); json.dump(dict(type="stop"), open("$R/vq/999_stop.json","w"))
PY
cp $R/vq/100a_T07.json "$D/out/eval_job.json"
( cd "$S001" && VLLM_LENS_DISABLE=1 PATH=/root/venvs/vl/bin:$PATH taskset -c 0-87 /root/venvs/vl/bin/python vllm_worker.py \
    --queue $R/vq --gpu_mem 0.90 --max_num_seqs 256 > $R/worker.log 2>&1 )
[ -f $R/vq/done/100a_T07.json ] || { echo "EVAL_FAILED"; exit 1; }
echo "=== eval done $(date -u +%H:%M:%S) rows $(wc -l < $R/rollouts_T07.jsonl)"
# 5. judging in background (CPU / API only)
nohup "$D/judge_D.sh" > $R/judge.log 2>&1 &
# 6. Track G on box 1: B s0 (with L40 copy) and A s0 checkpoints
sleep 20; waitgpu || exit 1
G="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG"
for st in 025 062 125 188; do
  "$G/run_ckpt.sh" hd-B_s0_step$st "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step$st" 0 0-87 100; sleep 20; waitgpu
  "$G/run_ckpt.sh" hd-A_s0_step$st "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/step$st" 0 0-87 0; sleep 20; waitgpu
done
echo "=== BOX1_CHAIN_DONE $(date -u +%H:%M:%S)"
