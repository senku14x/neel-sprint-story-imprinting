#!/bin/bash
cd "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src"
until grep -qE "CONDUCT_EXIT|Traceback" out/run_full.log; do sleep 10; done
grep -q Traceback out/run_full.log && { echo "RUN_FAILED"; exit 1; }
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out/api_ledger.jsonl"
export API_CAP_USD=10
echo "judge start $(date -u +%T)"
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/replies.jsonl out/turn3_text.json out/judged_replies.jsonl --concurrency 128
echo "judge exit $? $(date -u +%T)"
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out/replies.jsonl out/turn3_text.json out/judged_replies.jsonl --concurrency 64
echo "judge retry pass exit $? $(date -u +%T)"
