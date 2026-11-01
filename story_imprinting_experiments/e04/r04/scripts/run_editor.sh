#!/usr/bin/env bash
# Run the editor (a5_stage0_v13.py, unchanged) with R04's environment: env.sh (offline HF, caches inside r04/), the vLLM venv's
# bin/ on PATH (ninja for FlashInfer JIT, R02 note 8), GPU 0. Usage: bash run_editor.sh <log file> <editor args...>
set -uo pipefail
source /workspace/e04/r04/scripts/env.sh; unset PYTHONPATH
export PATH=/workspace/venvs/gpu/bin:$PATH CUDA_VISIBLE_DEVICES=0
LOG=$1; shift
echo "$(date -u +%FT%TZ) editor start: $*" >> $LOG
/workspace/venvs/gpu/bin/python /workspace/e04/r04/a5_stage0_v13.py "$@" >> $LOG 2>&1
RC=$?
echo "$(date -u +%FT%TZ) editor exit $RC" >> $LOG
