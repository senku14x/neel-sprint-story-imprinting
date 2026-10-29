#!/bin/bash
cd "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out/api_ledger.jsonl"
export API_CAP_USD=10
python3 judge_hist_x.py out/judge_in_hostility.jsonl out/judged_hist_hostility.jsonl > out/judge_hostility.log 2>&1 &
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8
echo "gpu start $(date -u +%T)"
taskset -c 0-87 /root/venvs/vlfix/bin/python conduct_x.py --versions rude_helpful --tag rude --sids_file out/kept.json > out/run_rude.log 2>&1
echo "gpu exit $? $(date -u +%T)"
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out_rude/replies.jsonl out_rude/turn3_text.json out_rude/judged_replies.jsonl --concurrency 128
python3 /workspace/runs_executor/sae1029/src/p3_judge_x.py out_rude/replies.jsonl out_rude/turn3_text.json out_rude/judged_replies.jsonl --concurrency 64
wait
echo "FOLLOWUP_DONE $(date -u +%T)"
