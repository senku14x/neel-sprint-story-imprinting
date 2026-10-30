#!/bin/bash
# sw014 activations (HF + PEFT, lib/acts.py): gates first (vLLM-vs-PEFT parity per organism, saved-vs-fresh), then
# 6 models x 64 scripts x 4 cells (v0), arms free + forced.
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src"
RUN=/workspace/runs_executor/sw014
cd "$SRC"
echo "sw014 acts start $(date -u +%T) on $(hostname) BOX=${BOX:-?}"
taskset -c 0-87 /root/venvs/si/bin/python acts14.py --gen_dir "$RUN" --part main
touch "$RUN/GPU_DONE_acts"
echo "sw014 acts done $(date -u +%T)"
