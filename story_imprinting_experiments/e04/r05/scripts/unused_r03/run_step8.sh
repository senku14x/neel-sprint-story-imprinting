#!/usr/bin/env bash
# E04 R05 step 5: imprinting evaluations of a5b's step-250 model on ONE GPU. R02's run_step8.sh, changed for R03:
#   - paths r02 -> r03; Bloom model tag hc_db_a5bq_r05_s250;
#   - gate: checks/a5b_s250/decision.txt starts with PASS (R02: both checks HEALTHY);
#   - one GPU, so the stages run one after another in the brief's order:
#       a1  (a) teammate's protocol generation at T=1      (gen_eval.py through run_gen_eval_logged.py, offline vLLM)
#       a07 (a) the same at T 0.7
#       bd  (b) Bloom, default Assistant, 100 conversations (E01's serve.sh + bloom_driver.py, plain T=1)
#       bx  (b) Bloom, Table 7 Dismissive, 100 conversations
#       c   (c) cheap checks on the same server (single-turn 50 x 5 prompts x 2 conditions; story check 50)
#     (a)'s judges (judge.py, GLM + DeepSeek, paced) and analyze.py run in the background while (b) runs, one temperature after the
#     other (flock), so each judge model gets one paced stream (R02 ran the two temperatures' judges at the same time);
#   - merged model on the container disk (/root/r05_scratch, E01's SI36_SCRATCH design); deleted by the caller once used.
#   bash run_step8.sh                         real run
#   STAGES="bd a1 bx a07 c" bash run_step8.sh run only these stages, in this order (time-short priority order of the brief)
#   SMOKE=1 bash run_step8.sh                 smoke test (brief step 2): parent = /dev/shm/qwen36_27b (verified copy of the base
#                                             snapshot), no merge; 4 scripts x 2 personas at T=1; Bloom 2 default conversations;
#                                             single-turn 5 prompts x 1 reply x 2 conditions; story check 2 stories; outputs logs/smoke/
set -uo pipefail
R03=/workspace/e04/r05; V=/workspace/e03/venvs
GPU=${GPU:-0}; PORT=${PORT:-8010}
if [ "${SMOKE:-0}" = 1 ]; then
  EV=$R03/logs/smoke/evals; LOG=$R03/logs/smoke/step8_smoke.log
  MODEL=/dev/shm/qwen36_27b; NAME=parent; BTAG=hc_db_smoke_parent
  SCRIPTS=$R03/src/eval_data/scripts_heldout2.jsonl; NSCR=4; BN=2; export SI36_LIMIT=2
  STAGES=${STAGES:-"a1 bd c"}; ST_N=1; SC_N=2
  export JUDGE_LEDGER=$R03/logs/smoke/ledger_openrouter_judge.jsonl
else
  EV=$R03/results/evals; LOG=$R03/logs/step8.log
  NAME=a5b_B_s250; BTAG=hc_db_a5bq_r05_s250
  SCRIPTS=$R03/src/eval_data/scripts_heldout2.jsonl,$R03/src/eval_data/scripts_frozen.jsonl; NSCR=0; BN=100
  STAGES=${STAGES:-"a1 a07 bd bx c"}; ST_N=50; SC_N=50
  export JUDGE_LEDGER=$R03/logs/ledger_openrouter_judge.jsonl
fi
mkdir -p $EV/teammate $R03/logs/bloom
say() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
say "step 5 start: SMOKE=${SMOKE:-0} stages: $STAGES"

if [ "${SMOKE:-0}" != 1 ]; then
  grep -q '^PASS' $R03/checks/a5b_s250/decision.txt 2>/dev/null || { say "not running step 5: a5b_s250 decision is '$(cat $R03/checks/a5b_s250/decision.txt 2>/dev/null)'"; exit 1; }
  RD=$R03/runs/a5b_s0; grep -q "_mb2" $R03/logs/train_a5b.times 2>/dev/null && RD=$R03/runs/a5b_s0_mb2
  MODEL=/root/r05_scratch/merged/a5b_B_s250
  if [ ! -f $MODEL/merge_meta.json ]; then
    say "merge start ($RD/final -> $MODEL)"
    ( source $R03/bloom_code/env.sh; cd $R03/bloom_code; CUDA_VISIBLE_DEVICES=$GPU /workspace/venvs/gpu/bin/python merge.py --adapter $RD/final --out $MODEL ) > $R03/logs/merge_a5b.log 2>&1 \
      || { say "MERGE FAILED"; exit 1; }
    say "merge done: $(cat $MODEL/merge_meta.json | tr -d '\n')"
  fi
fi
echo "[{\"name\": \"$NAME\", \"path\": \"$MODEL\"}]" > $EV/teammate/models.json

server_up() { curl -sf "localhost:$PORT/v1/models" 2>/dev/null | grep -q '"target"'; }
start_server() {
  server_up && return 0
  say "server start ($MODEL) on GPU $GPU port $PORT"
  bash $R03/bloom_code/serve.sh $MODEL $GPU $PORT $BTAG >> $LOG 2>&1 || { say "SERVER FAILED"; return 1; }
  say "server up"
}
stop_server() { server_up && { bash $R03/bloom_code/stop_server.sh $PORT >> $LOG 2>&1; say "server stopped"; }; return 0; }

judge_bg() {  # $1 = tag, $2 = rollouts file: judges until every row has both judges (up to 5 passes), then analyze.py
  local TAG=$1 OUT=$2
  ( exec 8>$R03/logs/judge_queue.lock; flock 8
    export API_LEDGER=$JUDGE_LEDGER API_CAP_USD=25 JUDGE_RPM=${JUDGE_RPM:-15}
    for pass in 1 2 3 4 5; do
      echo "$(date -u +%FT%TZ) teammate protocol $TAG judge pass $pass start" >> $LOG
      $V/si/bin/python -I $R03/scripts/run_judge_paced.py $OUT ${OUT%.jsonl}_judgments.jsonl --concurrency 32 >> $(dirname $LOG)/judge_$TAG.log 2>&1
      python3 - $OUT <<'EOF' && break
import json, sys
o = sys.argv[1]; j = o[:-6] + "_judgments.jsonl"
ok = {(r["key"], r["judge"]) for r in map(json.loads, open(j)) if not r.get("error")}
n = sum(1 for _ in open(o))
print(f"judged {len(ok)} of {2 * n}", flush=True)
sys.exit(0 if len(ok) >= 2 * n else 1)
EOF
    done
    $V/si/bin/python $R03/src/analyze.py --rollouts $OUT --judgments ${OUT%.jsonl}_judgments.jsonl --out ${OUT%.jsonl}_summary.json --tag $TAG \
      > $(dirname $LOG)/analyze_$TAG.log 2>&1
    echo "$(date -u +%FT%TZ) teammate protocol $TAG judged and analysed (analyze exit $?)" >> $LOG ) &
}

gen() {  # $1 = tag, $2 = temperature, $3 = output file name
  local TAG=$1 TEMP=$2 OUT=$EV/teammate/$3
  stop_server
  say "teammate protocol $TAG generation start on GPU $GPU"
  ( cd $R03/src; source $R03/scripts/env.sh; unset PYTHONPATH
    CUDA_VISIBLE_DEVICES=$GPU PATH=$V/vl/bin:$PATH VLLM_USE_FLASHINFER_SAMPLER=0 E02_SAMPLING_LOG=$EV/teammate/sampling_evidence.jsonl \
    $V/vl/bin/python $R03/scripts/run_gen_eval_logged.py --models $EV/teammate/models.json --scripts $SCRIPTS --n_scripts $NSCR \
      --personas default,dismissive --triggers 1 --temperature $TEMP --min_p 0.0 --max_tokens 512 --tag $TAG --out $OUT --max_num_seqs 128 \
      > $(dirname $LOG)/gen_eval_$TAG.log 2>&1 )
  say "teammate protocol $TAG generation exit $? ($(wc -l < $OUT 2>/dev/null || echo 0) rows)"
  [ -s $OUT ] && judge_bg $TAG $OUT
}

bloom() {  # $1 = none | dismissive
  start_server || return 1
  say "Bloom $1 start ($BN conversations)"
  ( cd $R03 && SI36_RUN_CAP=${SI36_RUN_CAP:?} SI36_API_CAP_USD=${SI36_API_CAP_USD:?} /workspace/venvs/bloom/bin/python $R03/scripts/bloom_driver.py \
      --model-tag $BTAG --port $PORT --system $1 --n $BN ) >> $(dirname $LOG)/bloom_driver_stdout.log 2>&1
  say "Bloom $1 exit $?"
  /workspace/venvs/bloom/bin/python -I $R03/scripts/bloom_ledger.py >> $LOG 2>&1 || say "bloom_ledger failed"
}

for s in $STAGES; do
  case $s in
    a1)  gen T1full 1.0 rollouts_T1.jsonl ;;
    a07) gen T0.7 0.7 rollouts_T07.jsonl ;;
    bd)  bloom none ;;
    bx)  bloom dismissive ;;
    c)   start_server && LOG=$LOG bash $R03/scripts/cheap_checks.sh $BTAG $ST_N $SC_N $PORT ;;
    *)   say "unknown stage $s" ;;
  esac
done
stop_server
say "waiting for the teammate protocol's judges"
wait
# tables: E01's analyze.py on all Bloom/single-turn/story runs (results/bloom/), then this run's summary (results/evals/evals.md)
( source $R03/bloom_code/env.sh; cd $R03/bloom_code; /workspace/venvs/bloom/bin/python analyze.py > $(dirname $LOG)/e01_analyze.log 2>&1 ) || say "E01 analyze.py failed"
EVALS_OUT=$EV EVALS_TAG=$BTAG /workspace/e03/venvs/si/bin/python -I $R03/scripts/evals_summary.py > $(dirname $LOG)/evals_summary.log 2>&1 || say "evals_summary.py failed"
say "step 5 done"
