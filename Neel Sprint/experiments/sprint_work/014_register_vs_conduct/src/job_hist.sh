#!/bin/bash
# sw014 full history writing (parent, vLLM): 64 scripts x 4 cells x 2 variants. Gate: screened-history rate >= 0.90.
set -euo pipefail
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src"
RUN=/workspace/runs_executor/sw014
cd "$SRC"
echo "sw014 hist start $(date -u +%T) on $(hostname) BOX=${BOX:-?}"
taskset -c 0-87 /root/venvs/vlfix/bin/python gen14.py --stages hist --out "$RUN" --min_hist_rate 0.90
touch "$RUN/GPU_DONE_hist"
setsid nohup python3 judge14.py hist "$RUN" --touch "$RUN/JUDGED_hist" > "$RUN/judge_hist.log" 2>&1 < /dev/null &
echo "sw014 hist GPU done $(date -u +%T); history judging in background"
