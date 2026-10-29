#!/bin/bash
cd "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/api_ledger.jsonl" API_CAP_USD=15
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/btw_judgein_early.jsonl out/user_map_early.json out/btw_judged.jsonl --concurrency 128
echo "EARLY_JUDGE_DONE $(date -u +%T)"
