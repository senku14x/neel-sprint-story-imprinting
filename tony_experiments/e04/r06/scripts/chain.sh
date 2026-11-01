#!/usr/bin/env bash
# E04 R06 steps 3-5 on one GPU (R04's chain.sh and R05's run_r05.sh, changed for R06; every change is in README Notes):
#   3. train a5bqc straight through to step 250: train_arm.sh with --schedule constant (10 warm-up steps, then 5e-4 to step 250),
#      everything else the 001 recipe on R04's train_a5bq.jsonl, seed 0 (OOM -> restart from scratch with 2 x 16)
#   4. after training, one at a time on the GPU (check.sh, the teammate's 001 definition, as in R02-R04):
#        a. setup (parent): chat entropy 0.55-0.65 and garbled <= 8/50 -> PASS, else stop and report
#        b. a5bqc step 125: report only
#        c. a5bqc step 250: report only (garbled <= 10/50 -> Hugging Face upload, run separately)
#   5. the teammate's fixed-script protocol (R05's code: E01's merge.py, gen_eval.py via run_gen_eval_logged.py, judge.py via
#      run_judge_paced.py + the run-wide pacer, analyze.py), cells in the brief's priority order:
#        1. a5bqc final (step 250), T 0.7, default + Dismissive, 200 scripts       (GLM priority 2)
#        2. a5bqc step 125, T 0.7, default + Dismissive, 100 scripts_heldout2      (GLM priority 3)
#        3. a5bqc final, plain T=1, default + Dismissive, 200 scripts              (GLM priority 4)
#      Health-check judges use GLM priority 1. Judging runs in the background, so the GPU never waits for it.
# Every stage updates STATUS.md and pushes in the background (push.sh takes a lock).
#   bash chain.sh            STAGES="..." runs only those stages
set -uo pipefail
R=/workspace/e04/r06; V=/workspace/e03/venvs; LOG=$R/logs/chain.log
GPU=0; export GPU
SCR=/root/r06_scratch/merged
EV=$R/results/evals; mkdir -p $EV/teammate
H2=$R/src/eval_data/scripts_heldout2.jsonl; FR=$R/src/eval_data/scripts_frozen.jsonl
STAGES=${STAGES:-"train checks merge:s250 gen:s250:T07 merge:s125 gen:s125:T07 delete:s125 gen:s250:T1 delete:s250 wait"}
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
st() { /workspace/venvs/gpu/bin/python -I $R/scripts/status.py "$@" > /dev/null 2>&1; }
push() { ( bash $R/scripts/push.sh "$1" >> $R/logs/push.log 2>&1 && say "pushed: $1" || say "PUSH FAILED: $1" ) & }
RD=$R/runs/a5bqc_s0
rd() { grep -q "_mb2" $R/logs/train_a5bqc.times 2>/dev/null && RD=$R/runs/a5bqc_s0_mb2 || RD=$R/runs/a5bqc_s0; }

# ---------------- 3. training
train() {
  if ! grep -q '^exit 0' $R/logs/train_a5bqc.times 2>/dev/null; then
    st --set stage="3. training a5bqc (constant schedule, 250 steps, about 75 minutes)" --set next="4. health checks: parent, a5bqc step 125, a5bqc step 250"
    push "E04 R06: training a5bqc started"
    say "training start"
    bash $R/scripts/train_arm.sh a5bqc $GPU $R/data/train_a5bq.jsonl --schedule constant
    say "training finished: $(tail -1 $R/logs/train_a5bqc.times)"
  fi
  rd
  if [ ! -f $RD/final/adapter_model.safetensors ] || [ ! -f $RD/step125/adapter_model.safetensors ]; then
    say "TRAINING FAILED: snapshots missing in $RD"
    st --set stage="3. training FAILED (snapshots missing)" --set problems="training did not produce step125/final; see logs/train_a5bqc*.log" --set next="report and stop"
    push "E04 R06: training failed"
    exit 1
  fi
  mkdir -p $R/results/training/a5bqc_s0
  cp $RD/train_log.jsonl $RD/train_meta.json $RD/golden_render.jsonl $R/results/training/a5bqc_s0/ 2>/dev/null
  sha256sum $RD/step125/adapter_model.safetensors $RD/final/adapter_model.safetensors $RD/step125/adapter_config.json $RD/final/adapter_config.json \
    > $R/results/training/a5bqc_s0/snapshot_hashes.txt
  /workspace/venvs/gpu/bin/python -I $R/scripts/train_report.py > $R/results/training/a5bqc_s0/train_report.txt 2>&1
  say "snapshots hashed; $(head -3 $R/results/training/a5bqc_s0/train_report.txt | tr '\n' ' ')"
  st --set stage="3. training done; 4. health checks" --set next="4a. setup check (parent)"
  push "E04 R06: a5bqc trained to step 250"
}

# ---------------- 4. health checks
prep() {  # $1 = check name, $2 = vLLM model name, $3 = snapshot dir (garble model; "parent" = no adapter), $4 = health adapter dir, $5 = its name
  local D=$R/checks/$1; mkdir -p $D
  if [ "$2" = "parent" ]; then
    echo '[{"name": "parent"}]' > $D/vllm_models.json
  else
    [ -d $R/lora_vllm/$2 ] || $V/si/bin/python $R/src/remap_lora_for_vllm.py $3 $R/lora_vllm/$2 >> $LOG 2>&1
    sha256sum $3/adapter_model.safetensors $3/adapter_config.json > $D/adapter_hash.txt
    echo "[{\"name\": \"$2\", \"lora\": \"$R/lora_vllm/$2\"}]" > $D/vllm_models.json
  fi
  echo "[{\"name\": \"$5\", \"path\": \"$4\"}]" > $D/health_adapters.json
}
decide() {  # $1 = check name, $2 = kind, $3 = model name -> decision.txt
  local D=$R/checks/$1 p
  for p in 1 2 3 4 5 6 7 8; do
    /workspace/venvs/gpu/bin/python -I $R/scripts/decide.py $D $2 $3 > $D/decision.tmp 2>&1 && break
    say "check $1: $(cat $D/decision.tmp); re-judging (extra pass $p)"
    sleep 30
    ( source $R/scripts/env.sh; unset PYTHONPATH
      export API_LEDGER=$R/logs/ledger_openrouter_judge.jsonl API_CAP_USD=8 GLM_PRIORITY=1 PACER_TAG=health_check:$1
      $V/si/bin/python -I $R/scripts/run_judge_paced.py $D/rollouts_T1.jsonl $D/judgments_T1.jsonl --concurrency 32 >> $D/judge.log 2>&1 )
    $V/si/bin/python -I $R/scripts/garble_summary.py $D > $D/summary.txt 2>&1
  done
  /workspace/venvs/gpu/bin/python -I $R/scripts/decide.py $D $2 $3 final > $D/decision.txt 2>&1
  rm -f $D/decision.tmp
  say "check $1 decision: $(cat $D/decision.txt)"
}
run_check() {  # $1 = check name
  local D=$R/checks/$1
  if grep -q "CHECK DONE" $D/check.log 2>/dev/null; then say "check $1 already done"; return; fi
  say "check $1 start"
  bash $R/scripts/check.sh $1 $D/vllm_models.json $D/health_adapters.json
  say "check $1 done"
}
checks() {
  rd
  # a. setup (parent). health.py needs one adapter; the parent's rows are computed with adapters disabled, so a5bqc's step-125
  #    adapter is loaded only to run it (the decision uses the parent rows only).
  prep setup parent - $RD/step125 a5bqc_B_s125
  st --set stage="4a. setup check (parent)" --set next="4b. a5bqc step-125 check (report only)"
  run_check setup
  decide setup setup parent
  st --set checks="setup: $(cat $R/checks/setup/decision.txt)"
  push "E04 R06: setup check $(cut -c1-4 $R/checks/setup/decision.txt)"
  if ! grep -q '^PASS' $R/checks/setup/decision.txt; then
    say "SETUP CHECK DID NOT PASS: stopping (brief step 4.1)"
    st --set stage="stopped: setup check did not pass" --set problems="setup check: $(cat $R/checks/setup/decision.txt)" --set next="report and stop"
    push "E04 R06: setup check did not pass; stopped"
    exit 1
  fi
  prep a5bqc_s125 a5bqc_B_s125 $RD/step125 $RD/step125 a5bqc_B_s125
  st --set stage="4b. a5bqc step-125 check (report only)" --set next="4c. a5bqc step-250 check (report only; upload if garbled <= 10/50)"
  run_check a5bqc_s125
  decide a5bqc_s125 s125 a5bqc_B_s125
  st --set checks="setup: $(cat $R/checks/setup/decision.txt); a5bqc step 125: $(cat $R/checks/a5bqc_s125/decision.txt)"
  push "E04 R06: a5bqc step 125 $(cat $R/checks/a5bqc_s125/decision.txt)"
  prep a5bqc_s250 a5bqc_B_s250 $RD/final $RD/final a5bqc_B_s250
  st --set stage="4c. a5bqc step-250 check (report only)" --set next="5. teammate's protocol: merge step 250, cell 1 (T 0.7)"
  run_check a5bqc_s250
  decide a5bqc_s250 s250 a5bqc_B_s250
  st --set checks="setup: $(cat $R/checks/setup/decision.txt); a5bqc step 125: $(cat $R/checks/a5bqc_s125/decision.txt); a5bqc step 250: $(cat $R/checks/a5bqc_s250/decision.txt)"
  push "E04 R06: a5bqc step 250 $(cat $R/checks/a5bqc_s250/decision.txt)"
}

# ---------------- 5. the teammate's protocol (R05's functions)
model_path() { case $1 in s250) echo $SCR/a5bqc_B_s250;; s125) echo $SCR/a5bqc_B_s125;; esac; }
tm_name()    { case $1 in s250) echo a5bqc_B_s250;; s125) echo a5bqc_B_s125;; esac; }
adapter()    { rd; case $1 in s250) echo $RD/final;; s125) echo $RD/step125;; esac; }
judge_prio() { case $1 in a5bqc_B_s250_T07) echo 2;; a5bqc_B_s125_T07) echo 3;; *) echo 4;; esac; }

merge() {  # $1 = s250 | s125
  local M=$1 OUT=$(model_path $1)
  [ -f $OUT/merge_meta.json ] && { say "merge $M: already done"; return 0; }
  say "merge $M start ($(adapter $M) -> $OUT)"
  ( source $R/bloom_code/env.sh; cd $R/bloom_code; CUDA_VISIBLE_DEVICES=$GPU /workspace/venvs/gpu/bin/python merge.py --adapter $(adapter $M) --out $OUT ) \
    > $R/logs/merge_$M.log 2>&1 || { say "MERGE FAILED $M"; return 1; }
  say "merge $M done: $(tr -d '\n' < $OUT/merge_meta.json)"
}

delete_merged() {
  local P=$(model_path $1)
  case $P in $SCR/*) rm -rf "$P" && say "deleted merged model $P";; esac
}

judge_bg() {  # $1 = cell tag, $2 = rollouts file, $3 = generation tag (analyze.py --tag): judges until every row has both judges
              # (up to 5 passes), then analyze.py
  local TAG=$1 OUT=$2 GT=$3 PR=$(judge_prio $1)
  ( export API_LEDGER=$R/logs/ledger_openrouter_judge.jsonl API_CAP_USD=8 GLM_PRIORITY=$PR PACER_TAG=teammate_judge:$TAG
    for pass in 1 2 3 4 5; do
      echo "$(date -u +%FT%TZ) teammate protocol $TAG judge pass $pass start (GLM priority $PR)" >> $LOG
      $V/si/bin/python -I $R/scripts/run_judge_paced.py $OUT ${OUT%.jsonl}_judgments.jsonl --concurrency 32 >> $R/logs/judge_$TAG.log 2>&1
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
      > $R/logs/analyze_$TAG.log 2>&1
    echo "$(date -u +%FT%TZ) teammate protocol $TAG judged and analysed (analyze exit $?)" >> $LOG ) &
}

gen() {  # $1 = s250 | s125, $2 = T1 | T07
  local M=$1 TL=$2 NAME=$(tm_name $1) TEMP TAG SCRIPTS
  case $TL in T1) TEMP=1.0; TAG=T1full;; T07) TEMP=0.7; TAG=T0.7;; esac   # the --tag sets the seeds: same as R05's cells
  case $M in s125) SCRIPTS=$H2;; *) SCRIPTS=$H2,$FR;; esac                 # step 125: the 100 scripts_heldout2 only
  local OUT=$EV/teammate/rollouts_${NAME}_${TL}.jsonl
  if [ -s $OUT ]; then say "teammate protocol $NAME $TL: rollouts exist ($(wc -l < $OUT) rows); not regenerated"; return 0; fi
  echo "[{\"name\": \"$NAME\", \"path\": \"$(model_path $M)\"}]" > $EV/teammate/models_${NAME}.json
  say "teammate protocol $NAME $TL generation start on GPU $GPU"
  ( cd $R/src; source $R/scripts/env.sh; unset PYTHONPATH
    CUDA_VISIBLE_DEVICES=$GPU PATH=$V/vl/bin:$PATH VLLM_USE_FLASHINFER_SAMPLER=0 E02_SAMPLING_LOG=$EV/teammate/sampling_evidence.jsonl \
    $V/vl/bin/python $R/scripts/run_gen_eval_logged.py --models $EV/teammate/models_${NAME}.json --scripts $SCRIPTS --n_scripts 0 \
      --personas default,dismissive --triggers 1 --temperature $TEMP --min_p 0.0 --max_tokens 512 --tag $TAG --out $OUT --max_num_seqs 128 \
      > $R/logs/gen_eval_${NAME}_${TL}.log 2>&1 )
  local rc=$?
  say "teammate protocol $NAME $TL generation exit $rc ($(wc -l < $OUT 2>/dev/null || echo 0) rows)"
  [ -s $OUT ] && judge_bg ${NAME}_${TL} $OUT $TAG
}

say "R06 chain start: stages: $STAGES"
for s in $STAGES; do
  IFS=: read -r kind m x <<< "$s"
  case $kind in
    train)  train ;;
    checks) checks ;;
    merge)  st --set stage="5. merge $m"; push "E04 R06: merge $m"; merge $m ;;
    gen)    st --set stage="5. protocol generation $m $x" --set next="judging in the background; next GPU stage after this"; push "E04 R06: protocol $m $x"; gen $m $x ;;
    delete) delete_merged $m ;;
    wait)   st --set stage="5. GPU stages done; judges still running" --set next="wait for the judges, then tables, HF upload, README"
            push "E04 R06: GPU stages done"; say "GPU stages done; waiting for the judges"; wait; say "judges done" ;;
    *)      say "unknown stage $s" ;;
  esac
done
st --set stage="5. done: all cells generated and judged" --set next="tables (evals_r06.py), HF upload, samples, README, final push"
push "E04 R06: protocol cells judged"
wait
say "CHAIN DONE"
