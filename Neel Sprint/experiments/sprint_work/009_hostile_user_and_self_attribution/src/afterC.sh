#!/bin/bash
# After sw009 C4 v2 generation: (1) judge + analyse C4 v2; (2) in parallel, sw006 N1 rerun with realised matching (the user: "rerun the
# sw006 nulls after C4"), both organisms, then judge + analyse.
S9="/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src"; S6="/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
cd "$S9"
until grep -q "C_GEN_DONE" out/runC2.log 2>/dev/null; do sleep 30; done
echo "C4 gen done seen $(date -u +%T)"
KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
J8="/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/judge8_x.py"; JP3=/workspace/runs_executor/sae1029/src/p3_judge_x.py
( cd "$S9" && TAG=_v2 CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyzeC_x.py prep
  for c in 128 64; do OPENROUTER_API_KEY="$KEY" API_LEDGER="$S9/out/api_ledger.jsonl" API_CAP_USD=15 python3 "$J8" out/C_judgein_v2.jsonl out/C_user_map_v2.json out/C_judged_v2.jsonl --concurrency $c; done
  TAG=_v2 CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyzeC_x.py report > out/C_report_v2.txt 2>&1
  echo "C4_REPORT_DONE $(date -u +%T)" ) > out/afterC_judge.log 2>&1 &
PJ=$!
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 5; done
cd "$S6"; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 0-43 /root/venvs/si/bin/python n1fix_x.py --models hdA0 > out/n1fix_hdA0.log 2>&1 & PA=$!
sleep 240
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c 44-87 /root/venvs/si/bin/python n1fix_x.py --models hdB0 > out/n1fix_hdB0.log 2>&1 & PB=$!
wait $PA $PB
echo "N1FIX_GEN_DONE $(date -u +%T) hdA0:$(grep -c N1FIX_EXIT out/n1fix_hdA0.log) hdB0:$(grep -c N1FIX_EXIT out/n1fix_hdB0.log)"
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python n1fix_analyze_x.py prep
for c in 128 64; do OPENROUTER_API_KEY="$KEY" API_LEDGER="$S6/out/api_ledger.jsonl" API_CAP_USD=15 python3 "$JP3" out/n1fix_judgein.jsonl out/n1fix_user_map.json out/n1fix_judged.jsonl --concurrency $c; done
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python n1fix_analyze_x.py report > out/n1fix_report.txt 2>&1
wait $PJ
echo "ALL_AFTER_C_DONE $(date -u +%T)"
