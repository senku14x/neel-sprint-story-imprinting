#!/bin/bash
# sw021 FULL part "free": free replies at <= 2,048 tokens after the swap, arms none / r1 / the six controls in free_controls.json
# (5 matched random controls chosen from the forced readout, both null types, + the same-kind donor; review 08:50), 2 samples, 64 scenarios x
# 2 directions x 2 models, left-padded batches across scenarios.
#  1. gated: adapter-active (review 08:50: HF-vs-vLLM parity and the repeated padcheck dropped; padcheck passed in the forced job);
#     free_smoke (2 scenarios, 128 tokens -> $RUN/smoke/; keys, non-empty, displacement matching)
#  2. full free stage (resumable by group); gates: unique keys, non-empty, displacement matching; cap-hit rate logged
# then GPU_DONE_free; judging (every free row, reply5: habit + hostility / helpfulness / fluency) + report in the background.
# DEPS: /workspace/runs_executor/sw021/GPU_DONE_forced
# EST_MIN: 120
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SRC="/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src"
RUN=/workspace/runs_executor/sw021
cd "$SRC"
echo "sw021 free start $(date -u +%T) box ${BOX:-?} host $(hostname)"
test -s "$RUN/free_controls.json"
taskset -c 0-87 python gpu21.py --ctx "$RUN" --out "$RUN" --stages adapter,free_smoke,free ${SW021_FREE_ARGS:-}
touch "$RUN/GPU_DONE_free"
nohup setsid bash "$SRC/post21.sh" free > "$RUN/post_free.log" 2>&1 < /dev/null &
echo "sw021 free GPU stage done $(date -u +%T); judging in background (pid $!, log $RUN/post_free.log)"
