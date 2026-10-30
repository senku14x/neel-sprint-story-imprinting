#!/bin/bash
# sw009 Stage A: full generation (3 samples, R3) -> judge inputs -> two judges -> report
cd "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src"
PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/vlfix/bin/python gen9_x.py --samples 3 --parent_samples 1 > out/gen.log 2>&1
echo "gen exit $? $(date -u +%T)"; grep -q GEN_DONE out/gen.log || { echo GEN_FAILED; exit 1; }
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze9_x.py prep > out/prep.log 2>&1
source env9.sh
python3 "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/judge8_x.py" out/judgein.jsonl out/user_map.json out/judged.jsonl --concurrency 128
python3 "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/judge8_x.py" out/judgein.jsonl out/user_map.json out/judged.jsonl --concurrency 64
echo "JUDGE_DONE_ALL $(date -u +%T)"
CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python analyze9_x.py report > out/report.txt 2>&1
echo "REPORT_DONE $(date -u +%T)"
