#!/bin/bash
# sw008: full generation (contexts checked with --build_only; judge hostility field known-answer checked in out/kat/) -> two judges -> analysis
cd "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src"
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8
taskset -c 0-87 /root/venvs/vlfix/bin/python gen8_x.py > out/gen.log 2>&1
echo "gen exit $? $(date -u +%T)"
grep -q GEN_DONE out/gen.log || { echo GEN_FAILED; exit 1; }
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out/api_ledger.jsonl" API_CAP_USD=10
python3 judge8_x.py out/replies.jsonl out/user_map.json out/judged.jsonl --concurrency 128
python3 judge8_x.py out/replies.jsonl out/user_map.json out/judged.jsonl --concurrency 64
echo "JUDGE_DONE_ALL $(date -u +%T)"
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze8_x.py > out/report.txt 2>&1
echo "REPORT_DONE $(date -u +%T)"
