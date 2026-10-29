#!/bin/bash
cd "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8
taskset -c 0-87 /root/venvs/vlfix/bin/python turn1_x.py > out/turn1.log 2>&1
echo "gen exit $? $(date -u +%T)"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/api_ledger.jsonl" API_CAP_USD=15
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/turn1_replies.jsonl out/turn1_user.json out/turn1_judged.jsonl --concurrency 128
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/turn1_replies.jsonl out/turn1_user.json out/turn1_judged.jsonl --concurrency 64
echo "TURN1_ALL_DONE $(date -u +%T)"
