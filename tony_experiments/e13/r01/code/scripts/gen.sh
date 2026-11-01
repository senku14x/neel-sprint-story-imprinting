#!/bin/bash
# E13 R01: one gen_eval.py engine run (E08 R08's gen.sh: W and compile caches under /workspace/e13/r01; R08_PERSONA_SCRIPTS dropped).
# Usage: gen.sh <run name> <gpu> <models json> <temperature> <tag> <out> [extra gen_eval args]
set -u
W=/workspace/e13/r01
NAME=$1 GPU=$2 MODELS=$3 TEMP=$4 TAG=$5 OUT=$6; shift 6
source $W/code/env.sh
export VLLM_CACHE_ROOT=$W/cache/vllm_gen TRITON_CACHE_DIR=$W/cache/triton_gen \
  TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor_gen FLASHINFER_WORKSPACE_BASE=$W/cache/flashinfer_gen
cd $W/src
echo "$(date -u +%FT%TZ) gen $NAME start (GPU $GPU, T $TEMP, tag $TAG, out $OUT)" >> $W/logs/run.log
CUDA_VISIBLE_DEVICES=$GPU R08_SAMPLING_LOG=${R08_SAMPLING_LOG:-$W/results/sampling_evidence.jsonl} \
  python -I $W/code/run_gen_eval_logged.py --models $MODELS \
  --scripts $W/src/eval_data/scripts_heldout2.jsonl,$W/src/eval_data/scripts_frozen.jsonl \
  --triggers 1 --temperature $TEMP --min_p 0.0 --max_tokens 512 --tag $TAG --out $OUT --max_num_seqs 256 "$@" \
  > $W/logs/gen_$NAME.log 2>&1
rc=$?
echo "$(date -u +%FT%TZ) gen $NAME exit $rc ($(wc -l < $OUT 2>/dev/null || echo 0) rows)" >> $W/logs/run.log
[ $rc = 0 ] && [ -s $OUT ] && touch $OUT.done
exit $rc
