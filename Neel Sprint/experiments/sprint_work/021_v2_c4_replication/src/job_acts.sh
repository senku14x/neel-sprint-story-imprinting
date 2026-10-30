#!/bin/bash
# sw021 activations (master s7) via lib/acts.py: per (model, direction, scenario) baseline / swap_r1 (post-intervention) /
# rand_shuf0_r1 (matched random control), teacher-forced re-run of the sample-0 forced readout; 14 layers, chat position labels.
# -> /workspace/runs_executor/overnight_2026-10-30/acts/sw021/ (part v2_<model>). Gates: none arm = capture, r1 coordinate = donor's.
# DEPS: /workspace/runs_executor/sw021/GPU_DONE_forced /workspace/runs_executor/overnight_2026-10-30/lib/READY_acts
# EST_MIN: 10
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SRC="/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src"
RUN=/workspace/runs_executor/sw021
cd "$SRC"
echo "sw021 acts start $(date -u +%T) box ${BOX:-?} host $(hostname)"
taskset -c 0-87 python gpu21.py --ctx "$RUN" --out "$RUN" --stages adapter,acts --acts_part v2
touch "$RUN/GPU_DONE_acts"
echo "sw021 acts done $(date -u +%T)"
