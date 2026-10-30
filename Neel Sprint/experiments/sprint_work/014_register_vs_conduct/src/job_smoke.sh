#!/bin/bash
# sw014 smoke (vLLM): hist (4 scripts x 4 cells x 2 variants), adapter-active check (8 contexts x 6 models, greedy 48),
# replies (6 models x 32 contexts x 1 sample, free 2048 + forced 48). Gates inside gen14.py (assert -> exit 1).
# Then small background judge runs (hist all, reply 20% + disagreements) to test the judge path.
set -euo pipefail
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src"
RUN=/workspace/runs_executor/sw014; OUT=$RUN/smoke
mkdir -p "$OUT"; cd "$SRC"
echo "sw014 smoke start $(date -u +%T) on $(hostname) BOX=${BOX:-?}"
taskset -c 0-87 /root/venvs/vlfix/bin/python gen14.py --stages hist,check,reply --smoke 4 --out "$OUT" --samples 1 --parent_samples 1 --min_hist_rate 0.75
touch "$RUN/GPU_DONE_smoke"
setsid nohup python3 judge14.py hist "$OUT" --touch "$RUN/JUDGED_smoke_hist" > "$OUT/judge_hist.log" 2>&1 < /dev/null &
setsid nohup python3 judge14.py reply "$OUT" --touch "$RUN/JUDGED_smoke_reply" > "$OUT/judge_reply.log" 2>&1 < /dev/null &
echo "sw014 smoke GPU done $(date -u +%T); judging in background"
