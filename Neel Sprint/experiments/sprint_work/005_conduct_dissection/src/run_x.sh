#!/bin/bash
# sw005 launcher: API env for the judge subprocess (key read from /workspace/.env, never printed), vLLM env.
cd "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out/api_ledger.jsonl"
export API_CAP_USD=10
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8
taskset -c 0-87 /root/venvs/vlfix/bin/python conduct_x.py "$@"
