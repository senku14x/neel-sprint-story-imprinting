#!/usr/bin/env bash
# E04 R05: imprinting evaluations of the existing adapters a2 (R02) and a5bq (R04), with E01's hc_db_s0 and the untrained model
# on the teammate's protocol, on ONE GPU. R03's run_step8.sh, changed for R05 (every change is listed in README Notes):
#   - paths r03 -> r05; several models instead of one (model keys a2, a5bq, e01hcdb, parent);
#   - names: teammate's protocol a2_B_s250, a5bq_B_s250, e01hcdb_B_s250, parent; Bloom tags hc_db_a2_r05_s250, hc_db_a5bq_r05_s250;
#   - no health-check gate (R05 trains nothing); E01's merge.py unchanged, merged models on the container disk;
#   - GPU order (brief step 3): (a) generation for a2 (T=1, T 0.7), a5bq (T=1, T 0.7), e01hcdb (T 0.7), parent (T=1);
#     then for a5bq and then a2, on its own served model: Bloom default, Bloom Dismissive, then the cheap checks' generations;
#   - GLM pacing (brief: at most 18 GLM requests a minute in total): every GLM and DeepSeek request takes a slot from the run-wide
#     pacer (scripts/api_pacer.py) with a priority that follows the brief's time-short order (GLM_PRIORITY, smaller = first):
#       0 Bloom judge (inside each Bloom conversation)       1 Bloom default: E01's garble + compliance checks
#       2 (a) T=1 a2, a5bq                                  3 (a) T=1 untrained model
#       4 Bloom Dismissive: garble + compliance             5 (a) T 0.7 a2, a5bq
#       6 (a) T 0.7 e01hcdb                                 7 (c) cheap checks (single-turn, story check)
#     So judging never holds up the GPU: the teammate's judges run in the background as soon as a rollout file exists; E01's
#     garble + compliance checks run per finished Bloom batch from scripts/post_checks.sh (SI36_DEFER_CHECKS=1 makes run_eval.sh
#     skip them); the cheap checks save their replies first (single_turn.py, story_check.py), and the server moves on.
#   bash run_r05.sh                          real run; STAGES="..." runs only those stages, in that order
#   SMOKE=1 bash run_r05.sh                  smoke test (brief step 1): untrained model (/dev/shm/qwen36_27b, no merge), 4 scripts x
#                                            2 personas at T=1, Bloom 2 default conversations, single-turn 5 prompts x 1 reply x 2
#                                            conditions, story check 2 stories; outputs logs/smoke/
set -uo pipefail
R=/workspace/e04/r05; V=/workspace/e03/venvs
GPU=${GPU:-0}; PORT=${PORT:-8010}
SCR=/root/r05_scratch/merged
export SI36_RUN_CAP=${SI36_RUN_CAP:?} SI36_API_CAP_USD=${SI36_API_CAP_USD:?}
if [ "${SMOKE:-0}" = 1 ]; then
  EV=$R/logs/smoke/evals; LOG=$R/logs/smoke/smoke.log
  SCRIPTS=$R/src/eval_data/scripts_heldout2.jsonl; NSCR=4; BN=2; export SI36_LIMIT=2; ST_N=1; SC_N=2
  STAGES=${STAGES:-"gen:parent:T1 bloom:parent:none cheap:parent"}
  export JUDGE_LEDGER=$R/logs/smoke/ledger_openrouter_judge.jsonl
else
  EV=$R/results/evals; LOG=$R/logs/r05.log
  SCRIPTS=$R/src/eval_data/scripts_heldout2.jsonl,$R/src/eval_data/scripts_frozen.jsonl; NSCR=0; BN=100; ST_N=50; SC_N=50
  STAGES=${STAGES:-"merge:a2 gen:a2:T1 gen:a2:T07 merge:a5bq gen:a5bq:T1 gen:a5bq:T07 merge:e01hcdb gen:e01hcdb:T07 delete:e01hcdb gen:parent:T1 bloom:a5bq:none bloom:a5bq:dismissive cheap:a5bq delete:a5bq bloom:a2:none bloom:a2:dismissive cheap:a2 delete:a2"}
  export JUDGE_LEDGER=$R/logs/ledger_openrouter_judge.jsonl
fi
mkdir -p $EV/teammate $R/logs/bloom $(dirname $LOG)
say() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
st() {  # status + push at every stage; the push runs in the background (push.sh takes a lock), so the GPU never waits for it
  /workspace/venvs/gpu/bin/python -I $R/scripts/status.py --set "stage=$1" > /dev/null 2>&1
  [ "${SMOKE:-0}" = 1 ] || ( bash $R/scripts/push.sh "E04 R05: $1" >> $R/logs/push.log 2>&1 & )
}

model_path() { case $1 in parent) echo /dev/shm/qwen36_27b;; a2) echo $SCR/a2_B_s250;; a5bq) echo $SCR/a5bq_B_s250;; e01hcdb) echo $SCR/e01hcdb_B_s250;; esac; }
tm_name()    { case $1 in parent) echo parent;; a2) echo a2_B_s250;; a5bq) echo a5bq_B_s250;; e01hcdb) echo e01hcdb_B_s250;; esac; }
btag()       { case $1 in parent) echo hc_db_smoke_parent;; a2) echo hc_db_a2_r05_s250;; a5bq) echo hc_db_a5bq_r05_s250;; esac; }
adapter()    { case $1 in a2) echo /workspace/e04/r02/adapters/a2_final;; a5bq) echo /workspace/e04/r04/adapters/a5bq_final;; e01hcdb) echo /workspace/si36/ckpt/hc_db_s0/final;; esac; }
judge_prio() { case $1 in *_T1) [ "${1%_T1}" = parent ] && echo 3 || echo 2;; e01hcdb*_T07) echo 6;; *_T07) echo 5;; *) echo 5;; esac; }

server_model() { curl -sf "localhost:$PORT/v1/models" 2>/dev/null | /workspace/venvs/gpu/bin/python -c "import json,sys; d=json.load(sys.stdin)['data']; print(d[0].get('root',''))" 2>/dev/null; }
stop_server() { if curl -sf "localhost:$PORT/v1/models" > /dev/null 2>&1; then bash $R/bloom_code/stop_server.sh $PORT >> $LOG 2>&1; say "server stopped"; fi; return 0; }
start_server() {  # $1 model key
  local P=$(model_path $1)
  [ "$(server_model)" = "$P" ] && return 0
  stop_server
  say "server start ($P) on GPU $GPU port $PORT"
  bash $R/bloom_code/serve.sh $P $GPU $PORT $(btag $1) >> $LOG 2>&1 || { say "SERVER FAILED"; return 1; }
  say "server up ($P)"
}

merge() {  # $1 model key
  local M=$1 OUT=$(model_path $1)
  [ -f $OUT/merge_meta.json ] && { say "merge $M: already done"; return 0; }
  stop_server
  say "merge $M start ($(adapter $M) -> $OUT)"
  ( source $R/bloom_code/env.sh; cd $R/bloom_code; CUDA_VISIBLE_DEVICES=$GPU /workspace/venvs/gpu/bin/python merge.py --adapter $(adapter $M) --out $OUT ) \
    > $R/logs/merge_$M.log 2>&1 || { say "MERGE FAILED $M"; return 1; }
  say "merge $M done: $(tr -d '\n' < $OUT/merge_meta.json)"
}

delete_merged() {  # $1 model key; waits for nothing on the GPU to use it
  local P=$(model_path $1)
  [ "$(server_model)" = "$P" ] && stop_server
  case $P in $SCR/*) rm -rf "$P" && say "deleted merged model $P";; esac
}

judge_bg() {  # $1 = cell tag, $2 = rollouts file, $3 = generation tag (analyze.py --tag filters rows by it): judges until every
              # row has both judges (up to 5 passes), then analyze.py
  local TAG=$1 OUT=$2 GT=$3 PR=$(judge_prio $1)
  ( export API_LEDGER=$JUDGE_LEDGER API_CAP_USD=45 GLM_PRIORITY=$PR PACER_TAG=teammate_judge:$TAG
    for pass in 1 2 3 4 5; do
      echo "$(date -u +%FT%TZ) teammate protocol $TAG judge pass $pass start (GLM priority $PR)" >> $LOG
      $V/si/bin/python -I $R/scripts/run_judge_paced.py $OUT ${OUT%.jsonl}_judgments.jsonl --concurrency 32 >> $(dirname $LOG)/judge_$TAG.log 2>&1
      python3 - $OUT <<'EOF' && break
import json, sys
o = sys.argv[1]; j = o[:-6] + "_judgments.jsonl"
ok = {(r["key"], r["judge"]) for r in map(json.loads, open(j)) if not r.get("error")}
n = sum(1 for _ in open(o))
print(f"judged {len(ok)} of {2 * n}", flush=True)
sys.exit(0 if len(ok) >= 2 * n else 1)
EOF
    done
    $V/si/bin/python $R/src/analyze.py --rollouts $OUT --judgments ${OUT%.jsonl}_judgments.jsonl --out ${OUT%.jsonl}_summary.json --tag $GT \
      > $(dirname $LOG)/analyze_$TAG.log 2>&1
    echo "$(date -u +%FT%TZ) teammate protocol $TAG judged and analysed (analyze exit $?)" >> $LOG ) &
}

gen() {  # $1 = model key, $2 = T1 | T07
  local M=$1 TL=$2 NAME=$(tm_name $1) TEMP TAG
  case $TL in T1) TEMP=1.0; TAG=T1full;; T07) TEMP=0.7; TAG=T0.7;; esac   # the --tag sets the seeds: same for every model
  local OUT=$EV/teammate/rollouts_${NAME}_${TL}.jsonl
  echo "[{\"name\": \"$NAME\", \"path\": \"$(model_path $M)\"}]" > $EV/teammate/models_${NAME}.json
  stop_server
  say "teammate protocol $NAME $TL generation start on GPU $GPU"
  ( cd $R/src; source $R/scripts/env.sh; unset PYTHONPATH
    CUDA_VISIBLE_DEVICES=$GPU PATH=$V/vl/bin:$PATH VLLM_USE_FLASHINFER_SAMPLER=0 E02_SAMPLING_LOG=$EV/teammate/sampling_evidence.jsonl \
    $V/vl/bin/python $R/scripts/run_gen_eval_logged.py --models $EV/teammate/models_${NAME}.json --scripts $SCRIPTS --n_scripts $NSCR \
      --personas default,dismissive --triggers 1 --temperature $TEMP --min_p 0.0 --max_tokens 512 --tag $TAG --out $OUT --max_num_seqs 128 \
      > $(dirname $LOG)/gen_eval_${NAME}_${TL}.log 2>&1 )
  local rc=$?
  say "teammate protocol $NAME $TL generation exit $rc ($(wc -l < $OUT 2>/dev/null || echo 0) rows)"
  [ -s $OUT ] && judge_bg ${NAME}_${TL} $OUT $TAG
}

bloom() {  # $1 = model key, $2 = none | dismissive
  start_server $1 || return 1
  say "Bloom $(btag $1) $2 start ($BN conversations)"
  ( cd $R && GLM_PRIORITY=0 SI36_DEFER_CHECKS=1 /workspace/venvs/bloom/bin/python $R/scripts/bloom_driver.py \
      --model-tag $(btag $1) --port $PORT --system $2 --n $BN ) >> $(dirname $LOG)/bloom_driver_stdout.log 2>&1
  say "Bloom $(btag $1) $2 exit $?"
  /workspace/venvs/bloom/bin/python -I $R/scripts/bloom_ledger.py >> $LOG 2>&1 || say "bloom_ledger failed"
}

cheap() {  # $1 = model key: start the cheap checks in the background; move on once both have saved their replies
  local T=$(btag $1)
  start_server $1 || return 1
  ( GLM_PRIORITY=7 LOG=$LOG bash $R/scripts/cheap_checks.sh $T $ST_N $SC_N $PORT ) &
  local PID=$! RUNS=$R/si36/runs
  for i in $(seq 1 360); do
    [ -f $RUNS/single_turn/${T}__T1_generations.jsonl ] && [ -f $RUNS/story/${T}__T1_generations.jsonl ] && break
    kill -0 $PID 2>/dev/null || break
    sleep 10
  done
  say "cheap checks $T: replies saved (single-turn $(wc -l < $RUNS/single_turn/${T}__T1_generations.jsonl 2>/dev/null || echo 0), story $(wc -l < $RUNS/story/${T}__T1_generations.jsonl 2>/dev/null || echo 0)); GLM judging continues in the background"
}

say "R05 start: SMOKE=${SMOKE:-0} stages: $STAGES"
for s in $STAGES; do
  IFS=: read -r kind m x <<< "$s"
  case $kind in
    merge)  st "merge $m"; merge $m ;;
    gen)    st "(a) generation $m $x"; gen $m $x ;;
    delete) delete_merged $m ;;
    bloom)  st "(b) Bloom $m $x"; bloom $m $x ;;
    cheap)  st "(c) cheap checks $m (replies)"; cheap $m ;;
    *)      say "unknown stage $s" ;;
  esac
done
stop_server
say "GPU stages done; waiting for the judges"
st "GPU stages done; judges still running"
wait
say "R05 run_r05.sh done"
