#!/usr/bin/env bash
# E04 R02 step 8: imprinting evaluations of a5b's step-250 model. Runs only if a5b was healthy at both checks.
#   bash run_step8.sh <serve_gpu> <protocol_gpu>
# 1. merge a5b's final adapter (E01's merge.py, unchanged) into /dev/shm/r02_scratch/merged/a5b_B_s250
# 2. serve it with E01's serve.sh (vLLM 0.30.0, --generation-config vllm, served name "target") on <serve_gpu>, port 8010
# 3. in parallel, in the brief's priority order:
#    - Bloom (b): default Assistant, 100 conversations, then Dismissive, 100 (bloom_driver.py; plain T=1)
#    - teammate's protocol (a): gen_eval.py on the merged model on <protocol_gpu>, 200 scripts x {default, dismissive}, trigger on,
#      first at T=1 then at T 0.7; judges (judge.py, GLM + DeepSeek); analyze.py
#    - cheap checks (c), after the Dismissive Bloom run: single_turn.py and story_check.py (E01's), plain T=1, GLM judge
set -uo pipefail
SG=$1; PG=$2
R02=/workspace/e04/r02; V=/workspace/e03/venvs; LOG=$R02/logs/step8.log
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
for c in a5b_s125 a5b_s250; do
  grep -q '^HEALTHY' $R02/checks/$c/decision.txt 2>/dev/null || { say "not running step 8: $c decision is '$(cat $R02/checks/$c/decision.txt 2>/dev/null)'"; exit 1; }
done
RD=$R02/runs/a5b_s0; grep -q "_mb2" $R02/logs/train_a5b.times && RD=$R02/runs/a5b_s0_mb2
MERGED=/dev/shm/r02_scratch/merged/a5b_B_s250
mkdir -p $R02/results/evals/teammate
if [ ! -f $MERGED/merge_meta.json ]; then
  say "merge start ($RD/final)"
  ( source $R02/bloom_code/env.sh; cd $R02/bloom_code; CUDA_VISIBLE_DEVICES=$SG /workspace/venvs/gpu/bin/python merge.py --adapter $RD/final --out $MERGED ) > $R02/logs/merge_a5b.log 2>&1 \
    || { say "MERGE FAILED"; exit 1; }
  say "merge done: $(cat $MERGED/merge_meta.json | tr -d '\n')"
fi
bash $R02/bloom_code/serve.sh $MERGED $SG 8010 a5b_B_s250 >> $LOG 2>&1 || { say "SERVER FAILED"; exit 1; }
say "server up on GPU $SG port 8010"
export SI36_RUN_CAP=31.5 SI36_API_CAP_USD=31.5
# Bloom: default, then dismissive, then the cheap checks (they share the server)
tmux new -d -s bloom "cd $R02 && /workspace/venvs/bloom/bin/python $R02/scripts/bloom_driver.py --model-tag hc_db_a5b_r02_s250 --port 8010 --system none --n 100; \
  /workspace/venvs/bloom/bin/python $R02/scripts/bloom_driver.py --model-tag hc_db_a5b_r02_s250 --port 8010 --system dismissive --n 100; \
  bash $R02/scripts/cheap_checks.sh"
say "Bloom driver started (default, then dismissive, then cheap checks)"
# teammate's protocol on the merged model
echo "[{\"name\": \"a5b_B_s250\", \"path\": \"$MERGED\"}]" > $R02/results/evals/teammate/models.json
cd $R02/src
for spec in "T1full 1.0 rollouts_T1.jsonl" "T0.7 0.7 rollouts_T07.jsonl"; do
  set -- $spec; TAG=$1; TEMP=$2; OUT=$R02/results/evals/teammate/$3
  say "teammate protocol $TAG generation start on GPU $PG"
  CUDA_VISIBLE_DEVICES=$PG PATH=$V/vl/bin:$PATH VLLM_USE_FLASHINFER_SAMPLER=0 E02_SAMPLING_LOG=$R02/results/evals/teammate/sampling_evidence.jsonl \
    $V/vl/bin/python $R02/scripts/run_gen_eval_logged.py --models $R02/results/evals/teammate/models.json \
    --scripts $R02/src/eval_data/scripts_heldout2.jsonl,$R02/src/eval_data/scripts_frozen.jsonl --personas default,dismissive --triggers 1 \
    --temperature $TEMP --min_p 0.0 --max_tokens 512 --tag $TAG --out $OUT --max_num_seqs 128 > $R02/logs/gen_eval_$TAG.log 2>&1
  say "teammate protocol $TAG generation exit $? ($(wc -l < $OUT) rows)"
  ( export API_LEDGER=$R02/logs/ledger_openrouter_judge.jsonl API_CAP_USD=25 JUDGE_RPM=${JUDGE_RPM:-15}
    for pass in 1 2 3; do
      $V/si/bin/python -I $R02/scripts/run_judge_paced.py $OUT ${OUT%.jsonl}_judgments.jsonl --concurrency 32 >> $R02/logs/judge_$TAG.log 2>&1
      python3 - $OUT <<'EOF' && break
import json, sys
o = sys.argv[1]; j = o[:-6] + "_judgments.jsonl"
ok = {(r["key"], r["judge"]) for r in map(json.loads, open(j)) if not r.get("error")}
sys.exit(0 if len(ok) >= 2 * sum(1 for _ in open(o)) else 1)
EOF
    done
    $V/si/bin/python $R02/src/analyze.py --rollouts $OUT --judgments ${OUT%.jsonl}_judgments.jsonl --out ${OUT%.jsonl}_summary.json --tag $TAG \
      > $R02/logs/analyze_$TAG.log 2>&1
    echo "$(date -u +%FT%TZ) teammate protocol $TAG judged and analysed" >> $LOG ) &
done
wait
say "teammate protocol done"
