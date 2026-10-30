#!/bin/bash
# sw014 replies (vLLM): adapter-active check first (gate), then 5 organisms x 64 x 4 cells x 2 variants x 2 samples and the
# parent x 1 sample, free (2048) + forced (48). Gates in gen14.py. Then reply judging in the background.
set -euo pipefail
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src"
RUN=/workspace/runs_executor/sw014
cd "$SRC"
echo "sw014 reply start $(date -u +%T) on $(hostname) BOX=${BOX:-?}"
taskset -c 0-87 /root/venvs/vlfix/bin/python gen14.py --stages check,reply --out "$RUN" --samples 2 --parent_samples 1
touch "$RUN/GPU_DONE_reply"
setsid nohup python3 judge14.py reply "$RUN" --touch "$RUN/JUDGED_reply" > "$RUN/judge_reply.log" 2>&1 < /dev/null &
echo "sw014 reply GPU done $(date -u +%T); reply judging in background"
