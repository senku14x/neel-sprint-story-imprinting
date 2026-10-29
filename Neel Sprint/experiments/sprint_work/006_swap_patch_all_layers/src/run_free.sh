#!/bin/bash
# sw006 secondary readouts (R6, R7): turn-1 long-cap free replies (vLLM), then HF free replies for the key arms on 32 scripts.
cd "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
until grep -qE "hdB0 exit" out/run_full.log 2>/dev/null; do sleep 10; done
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 3; done
echo "turn1 long start $(date -u +%T)"
PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/vlfix/bin/python turn1_x.py --long > out/turn1_long.log 2>&1
echo "turn1 long exit $? $(date -u +%T)"
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 3; done
SIDS=$(cat out/free_sids.txt)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 0-43 /root/venvs/si/bin/python hf_x.py --stages free --models hdA0 --sids "$SIDS" > out/hf_free_hdA0.log 2>&1 &
PA=$!; sleep 240
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 44-87 /root/venvs/si/bin/python hf_x.py --stages free --models hdB0 --sids "$SIDS" > out/hf_free_hdB0.log 2>&1 &
PB=$!
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/api_ledger.jsonl" API_CAP_USD=15
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/turn1_long_replies.jsonl out/turn1_long_user.json out/turn1_long_judged.jsonl --concurrency 96
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/turn1_long_replies.jsonl out/turn1_long_user.json out/turn1_long_judged.jsonl --concurrency 48
echo "turn1 long judged $(date -u +%T)"
wait $PA; echo "free hdA0 exit $? $(date -u +%T)"; wait $PB; echo "free hdB0 exit $? $(date -u +%T)"
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py prep
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/free_judgein.jsonl out/user_map.json out/free_judged.jsonl --concurrency 128
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/free_judgein.jsonl out/user_map.json out/free_judged.jsonl --concurrency 64
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py report > out/report_with_free.txt 2>&1
echo "FREE_ALL_DONE $(date -u +%T)"
