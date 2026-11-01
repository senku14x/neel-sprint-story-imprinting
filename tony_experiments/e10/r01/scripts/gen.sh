#!/bin/bash
# E10 R01 (E08 R07's gen.sh, paths changed, GPU a parameter): one gen_eval.py engine run.
# Usage: gen.sh <run name> <gpu> <models json> <temperature> <tag> <out> [extra gen_eval args]
# The --scripts / --triggers defaults below are overridden per invocation (argparse keeps the last value given).
set -u
W=/workspace/e10/r01
NAME=$1 GPU=$2 MODELS=$3 TEMP=$4 TAG=$5 OUT=$6; shift 6
source $W/scripts/env.sh
cd $W/src
echo "$(date -u +%FT%TZ) gen $NAME start (GPU $GPU, T $TEMP, tag $TAG, out $OUT)" >> $W/logs/run.log
CUDA_VISIBLE_DEVICES=$GPU R07_SAMPLING_LOG=${R07_SAMPLING_LOG:-$W/results/sampling_evidence.jsonl} \
  python -I $W/scripts/run_gen_eval_logged.py --models $MODELS \
  --scripts $W/src/eval_data/scripts_heldout2.jsonl,$W/src/eval_data/scripts_frozen.jsonl \
  --triggers 1 --temperature $TEMP --min_p 0.0 --max_tokens 512 --tag $TAG --out $OUT --max_num_seqs 256 "$@" \
  > $W/logs/gen_$NAME.log 2>&1
rc=$?
echo "$(date -u +%FT%TZ) gen $NAME exit $rc ($(wc -l < $OUT 2>/dev/null || echo 0) rows)" >> $W/logs/run.log
[ $rc = 0 ] && [ -s $OUT ] && touch $OUT.done
exit $rc
