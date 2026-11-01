#!/bin/bash
# E08 R09: one Part D story job. Usage: story.sh <job D1|D2> <gpu> <try>
set -u
W=/workspace/e08/r09; JOB=$1 GPU=$2 TRY=$3
source $W/code/env.sh
export VLLM_CACHE_ROOT=/root/.cache/e08r09/vllm_gpu$GPU TRITON_CACHE_DIR=/root/.cache/e08r09/triton_gpu$GPU \
  TORCHINDUCTOR_CACHE_DIR=/root/.cache/e08r09/inductor_gpu$GPU FLASHINFER_WORKSPACE_BASE=/root/.cache/e08r09/flashinfer_gpu$GPU
CELLS=ST-CF,ST-CC; [ "$JOB" = D2 ] && CELLS=ST-NF,ST-NC
[ -f $W/results/stories/$JOB.jsonl.done ] && exit 0
echo "$(date -u +%FT%TZ) story $JOB start (GPU $GPU, try $TRY)" >> $W/logs/run.log
CUDA_VISIBLE_DEVICES=$GPU python -I $W/code/gen_stories.py --job $JOB --cells $CELLS > $W/logs/story_${JOB}_try$TRY.log 2>&1
rc=$?
echo "$(date -u +%FT%TZ) story $JOB exit $rc" >> $W/logs/run.log
exit $rc
