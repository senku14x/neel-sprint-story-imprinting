#!/bin/bash
# E08 R10: one gen_eval.py engine run (R09's gen.sh; changes: paths, the script set and the switch-script files per job).
# Usage: gen.sh <run name> <gpu> <models json> <temperature> <tag> <out> <script set all|h2|h2first50|smoke> [extra gen_eval args]
set -u
W=/workspace/e08/r10
NAME=$1 GPU=$2 MODELS=$3 TEMP=$4 TAG=$5 OUT=$6 SSET=$7; shift 7
source $W/code/env.sh
export VLLM_CACHE_ROOT=/root/.cache/e08r10/vllm_gpu$GPU TRITON_CACHE_DIR=/root/.cache/e08r10/triton_gpu$GPU \
  TORCHINDUCTOR_CACHE_DIR=/root/.cache/e08r10/inductor_gpu$GPU FLASHINFER_WORKSPACE_BASE=/root/.cache/e08r10/flashinfer_gpu$GPU
case $SSET in
  all) SCRIPTS=$W/src/eval_data/scripts_heldout2.jsonl,$W/src/eval_data/scripts_frozen.jsonl; NS=() ;;
  h2) SCRIPTS=$W/src/eval_data/scripts_heldout2.jsonl; NS=() ;;
  h2first50) SCRIPTS=$W/src/eval_data/scripts_heldout2.jsonl; NS=(--n_scripts 50) ;;
  smoke) SCRIPTS=$W/smoke/scripts_smoke.jsonl; NS=() ;;
  *) echo "bad script set $SSET"; exit 9 ;;
esac
PS="{"; for c in SW-F SW-C SW-P23 SW-CV SW-FR; do PS="$PS\"$c\": \"$W/data/sw_${c}_$SSET.jsonl\", "; done; PS="${PS%, }}"
cd $W/src
echo "$(date -u +%FT%TZ) gen $NAME start (GPU $GPU, T $TEMP, tag $TAG, scripts $SSET, out $OUT)" >> $W/logs/run.log
CUDA_VISIBLE_DEVICES=$GPU R08_SAMPLING_LOG=${R08_SAMPLING_LOG:-$W/results/sampling_evidence.jsonl} \
  R08_PERSONA_SCRIPTS="$PS" \
  python -I $W/code/run_gen_eval_logged.py --models $MODELS --scripts $SCRIPTS "${NS[@]}" \
  --triggers 1 --temperature $TEMP --min_p 0.0 --max_tokens 512 --tag $TAG --out $OUT --max_num_seqs 256 "$@" \
  > $W/logs/gen_$NAME.log 2>&1
rc=$?
echo "$(date -u +%FT%TZ) gen $NAME exit $rc ($(wc -l < $OUT 2>/dev/null || echo 0) rows)" >> $W/logs/run.log
[ $rc = 0 ] && [ -s $OUT ] && touch $OUT.done
exit $rc
