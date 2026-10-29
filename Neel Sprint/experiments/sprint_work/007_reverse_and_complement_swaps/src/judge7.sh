#!/bin/bash
# sw007 judging: btw as soon as both organisms' btw stages succeed; free after GEN_ALL_DONE.
cd "/workspace/Neel Sprint/experiments/sprint_work/007_reverse_and_complement_swaps/src"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/007_reverse_and_complement_swaps/src/out/api_ledger.jsonl" API_CAP_USD=15
J=/workspace/runs_executor/sae1029/src/p3_judge_x.py
until grep -q "btw hdA0 done" out/run7.log && grep -q "btw hdB0 done" out/run7.log; do sleep 20; done
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze7_x.py prep && cp out/user_map.json out/user_map_btw.json
python3 $J out/btw_judgein.jsonl out/user_map_btw.json out/btw_judged.jsonl --concurrency 128
python3 $J out/btw_judgein.jsonl out/user_map_btw.json out/btw_judged.jsonl --concurrency 64
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze7_x.py report > out/report_btw.txt 2>&1
echo "BTW_REPORT_DONE $(date -u +%T)"
until grep -q "GEN_ALL_DONE" out/run7.log && grep -q "free hdA0 done" out/run7.log && grep -q "free hdB0 done" out/run7.log; do sleep 30; done
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze7_x.py prep
python3 $J out/free_judgein.jsonl out/user_map.json out/free_judged.jsonl --concurrency 128
python3 $J out/free_judgein.jsonl out/user_map.json out/free_judged.jsonl --concurrency 64
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze7_x.py report > out/report_all.txt 2>&1
echo "ALL_REPORT_DONE $(date -u +%T)"
