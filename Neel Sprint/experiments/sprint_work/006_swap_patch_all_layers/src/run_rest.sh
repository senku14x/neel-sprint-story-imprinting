#!/bin/bash
# sw006 after the 10:31 hdB0 OOM: hdB0 restarts chunked (resumes from finished batches), hdA0's original process continues
# (re-run chunked if it dies); then btw judging + report (background), turn-1 long rerun, free replies, their judging.
cd "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CPUS_hdA0=0-43; CPUS_hdB0=44-87
run_hf() {  # model stage logtag [extra args]; retries until HF_EXIT (resume skips finished batches)
  for try in 1 2 3; do
    CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 taskset -c $(eval echo \$CPUS_$1) /root/venvs/si/bin/python hf_x.py --stages $2 --models $1 --chunk 26 "${@:4}" > out/$3_$1_try$try.log 2>&1
    grep -q HF_EXIT out/$3_$1_try$try.log && { echo "$3 $1 done try $try $(date -u +%T)"; return 0; }
    echo "$3 $1 failed try $try $(date -u +%T)"; sleep 30
  done
}
run_hf hdB0 patch hf_patch &
PB=$!
while kill -0 2577989 2>/dev/null; do sleep 10; done
grep -q HF_EXIT out/hf_patch_hdA0.log && echo "patch hdA0 original process done $(date -u +%T)" || run_hf hdA0 patch hf_patch
wait $PB
echo "PATCH_BOTH_DONE $(date -u +%T)"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d "\"'")"
export API_LEDGER="/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/api_ledger.jsonl" API_CAP_USD=15
J=/workspace/runs_executor/sae1029/src/p3_judge_x.py
( CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py prep
  cp out/user_map.json out/user_map_btw.json
  python3 $J out/btw_judgein.jsonl out/user_map_btw.json out/btw_judged.jsonl --concurrency 128
  python3 $J out/btw_judgein.jsonl out/user_map_btw.json out/btw_judged.jsonl --concurrency 64
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py report > out/report.txt 2>&1
  echo "BTW_REPORT_DONE $(date -u +%T)" ) > out/btw_judge.log 2>&1 &
PJ=$!
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 3; done
PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/vlfix/bin/python turn1_x.py --long > out/turn1_long.log 2>&1
echo "turn1 long exit $? $(date -u +%T)"
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2000 ]; do sleep 3; done
SIDS=$(cat out/free_sids.txt)
run_hf hdA0 free hf_free --sids "$SIDS" &
FA=$!; sleep 240
run_hf hdB0 free hf_free --sids "$SIDS" &
FB=$!
python3 $J out/turn1_long_replies.jsonl out/turn1_long_user.json out/turn1_long_judged.jsonl --concurrency 96
python3 $J out/turn1_long_replies.jsonl out/turn1_long_user.json out/turn1_long_judged.jsonl --concurrency 48
echo "turn1 long judged $(date -u +%T)"
wait $FA $FB; wait $PJ
echo "FREE_GEN_DONE $(date -u +%T)"
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py prep
python3 $J out/free_judgein.jsonl out/user_map.json out/free_judged.jsonl --concurrency 128
python3 $J out/free_judgein.jsonl out/user_map.json out/free_judged.jsonl --concurrency 64
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze_x.py report > out/report_with_free.txt 2>&1
echo "ALL_DONE $(date -u +%T)"
