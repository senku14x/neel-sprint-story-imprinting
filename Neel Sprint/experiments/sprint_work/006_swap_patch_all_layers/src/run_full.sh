#!/bin/bash
# sw006 full primary readout: one HF process per organism on the same GPU, then judges and report.
cd "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
until grep -qE "hf exit" out/run_hf.log 2>/dev/null; do sleep 5; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 3; done
echo "full start $(date -u +%T)"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 0-43 /root/venvs/si/bin/python hf_x.py --stages patch --models hdA0 > out/hf_patch_hdA0.log 2>&1 &
PA=$!
sleep 240  # stagger the model loads
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 44-87 /root/venvs/si/bin/python hf_x.py --stages patch --models hdB0 > out/hf_patch_hdB0.log 2>&1 &
PB=$!
wait $PA; echo "hdA0 exit $? $(date -u +%T)"; wait $PB; echo "hdB0 exit $? $(date -u +%T)"
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py prep
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/api_ledger.jsonl" API_CAP_USD=15
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/btw_judgein.jsonl out/user_map.json out/btw_judged.jsonl --concurrency 128
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/btw_judgein.jsonl out/user_map.json out/btw_judged.jsonl --concurrency 64
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py report > out/report.txt 2>&1
echo "FULL_ALL_DONE $(date -u +%T)"
