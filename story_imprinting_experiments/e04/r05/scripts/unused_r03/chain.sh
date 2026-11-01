#!/usr/bin/env bash
# E04 R03 steps 3-5 on one GPU (replaces R02's watch_arm.sh, which ran checks on a second GPU while training continued):
#   3. train a5b straight through to step 250 (train_arm.sh, R02's recipe; OOM -> restart from scratch with 2 x 16)
#   4. after training, one at a time on the GPU (check.sh, R02's 001 definition):
#        a. setup (parent): chat entropy 0.55-0.65 and garbled <= 8/50, else stop
#        b. a5b step 125: report only
#        c. a5b step 250: garbled <= 25/50 -> PASS -> step 5; else FAIL -> no step 5
#      Every check is re-judged until all 50 conversations are scored before deciding (else UNKNOWN).
#   5. on a step-250 PASS: run_step8.sh
# Pushes after each stage.
set -uo pipefail
R03=/workspace/e04/r03; V=/workspace/e03/venvs; LOG=$R03/logs/chain.log
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
st() { /workspace/venvs/gpu/bin/python -I $R03/scripts/status.py "$@" > /dev/null 2>&1; }
push() { bash $R03/scripts/push.sh "$1" >> $R03/logs/push.log 2>&1 && say "pushed: $1" || say "PUSH FAILED: $1"; }
export GPU=0

# ---------------- 3. training
if ! grep -q '^exit 0' $R03/logs/train_a5b.times 2>/dev/null; then
  st --set stage="3. training a5b (250 steps, about 80 minutes)" --set next="4. health checks after training: parent, a5b step 125, a5b step 250"
  push "E04 R03: training a5b started"
  say "training start"
  bash $R03/scripts/train_arm.sh a5b 0
  say "training finished: $(tail -1 $R03/logs/train_a5b.times)"
fi
RD=$R03/runs/a5b_s0; grep -q "_mb2" $R03/logs/train_a5b.times && RD=$R03/runs/a5b_s0_mb2
if [ ! -f $RD/final/adapter_model.safetensors ] || [ ! -f $RD/step125/adapter_model.safetensors ]; then
  say "TRAINING FAILED: snapshots missing in $RD"
  st --set stage="3. training FAILED (snapshots missing)" --set problems="training did not produce step125/final; see logs/train_a5b*.log" --set next="report and stop"
  push "E04 R03: training failed"
  exit 1
fi
mkdir -p $R03/results/training/a5b_s0
cp $RD/train_log.jsonl $RD/train_meta.json $R03/results/training/a5b_s0/ 2>/dev/null
sha256sum $RD/step125/adapter_model.safetensors $RD/final/adapter_model.safetensors $RD/step125/adapter_config.json $RD/final/adapter_config.json \
  > $R03/results/training/a5b_s0/snapshot_hashes.txt
/workspace/venvs/gpu/bin/python -I $R03/scripts/repro.py > $R03/results/training/a5b_s0/repro.txt 2>&1
say "snapshots hashed; repro check: $(head -3 $R03/results/training/a5b_s0/repro.txt | tr '\n' ' ')"
st --set stage="3. training done; 4. health checks" --set next="4a. setup check (parent)"
push "E04 R03: a5b trained to step 250"

# ---------------- 4. health checks
prep() {  # $1 = check name, $2 = vLLM model name, $3 = snapshot dir (garble model; "parent" = no adapter), $4 = health adapter dir, $5 = its name
  local D=$R03/checks/$1; mkdir -p $D
  if [ "$2" = "parent" ]; then
    echo '[{"name": "parent"}]' > $D/vllm_models.json
  else
    [ -d $R03/lora_vllm/$2 ] || $V/si/bin/python $R03/src/remap_lora_for_vllm.py $3 $R03/lora_vllm/$2 >> $LOG 2>&1
    sha256sum $3/adapter_model.safetensors $3/adapter_config.json > $D/adapter_hash.txt
    echo "[{\"name\": \"$2\", \"lora\": \"$R03/lora_vllm/$2\"}]" > $D/vllm_models.json
  fi
  echo "[{\"name\": \"$5\", \"path\": \"$4\"}]" > $D/health_adapters.json
}
decide() {  # $1 = check name, $2 = kind, $3 = model name -> decision.txt
  local D=$R03/checks/$1 p
  for p in 1 2 3 4 5 6 7 8; do
    /workspace/venvs/gpu/bin/python -I $R03/scripts/decide.py $D $2 $3 > $D/decision.tmp 2>&1 && break
    say "check $1: $(cat $D/decision.tmp); re-judging (extra pass $p)"
    sleep 30
    ( source $R03/scripts/env.sh; unset PYTHONPATH; export API_LEDGER=$R03/logs/ledger_openrouter_judge.jsonl API_CAP_USD=25 JUDGE_RPM=18
      $V/si/bin/python -I $R03/scripts/run_judge_paced.py $D/rollouts_T1.jsonl $D/judgments_T1.jsonl --concurrency 32 >> $D/judge.log 2>&1 )
    $V/si/bin/python -I $R03/scripts/garble_summary.py $D > $D/summary.txt 2>&1
  done
  /workspace/venvs/gpu/bin/python -I $R03/scripts/decide.py $D $2 $3 final > $D/decision.txt 2>&1
  rm -f $D/decision.tmp
  say "check $1 decision: $(cat $D/decision.txt)"
}
run_check() {  # $1 = check name
  local D=$R03/checks/$1
  if grep -q "CHECK DONE" $D/check.log 2>/dev/null; then say "check $1 already done"; return; fi
  say "check $1 start"
  bash $R03/scripts/check.sh $1 $D/vllm_models.json $D/health_adapters.json
  say "check $1 done"
}

# a. setup (parent). health.py needs one adapter; the parent's rows are computed with adapters disabled, so a5b's step-125
#    adapter is loaded only to run it (the decision uses the parent rows only).
prep setup parent - $RD/step125 a5b_B_s125
st --set stage="4a. setup check (parent)" --set next="4b. a5b step-125 check (report only)"
run_check setup
decide setup setup parent
st --set checks="setup: $(cat $R03/checks/setup/decision.txt)"
push "E04 R03: setup check $(cut -c1-4 $R03/checks/setup/decision.txt)"
if ! grep -q '^PASS' $R03/checks/setup/decision.txt; then
  say "SETUP CHECK DID NOT PASS: stopping (brief 4a)"
  st --set stage="stopped: setup check did not pass" --set problems="setup check: $(cat $R03/checks/setup/decision.txt)" --set next="report and stop"
  push "E04 R03: setup check did not pass; stopped"
  exit 1
fi

# b. a5b step 125 (report only)
prep a5b_s125 a5b_B_s125 $RD/step125 $RD/step125 a5b_B_s125
st --set stage="4b. a5b step-125 check (report only)" --set next="4c. a5b step-250 check (pass = garbled <= 25/50)"
run_check a5b_s125
decide a5b_s125 s125 a5b_B_s125
st --set checks="setup: $(cat $R03/checks/setup/decision.txt); a5b step 125: $(cat $R03/checks/a5b_s125/decision.txt)"
push "E04 R03: a5b step 125 $(cat $R03/checks/a5b_s125/decision.txt)"

# c. a5b step 250
prep a5b_s250 a5b_B_s250 $RD/final $RD/final a5b_B_s250
st --set stage="4c. a5b step-250 check" --set next="step 5 if PASS (garbled <= 25/50), else wrap-up"
run_check a5b_s250
decide a5b_s250 s250 a5b_B_s250
DEC=$(cat $R03/checks/a5b_s250/decision.txt)
st --set checks="setup: $(cat $R03/checks/setup/decision.txt); a5b step 125: $(cat $R03/checks/a5b_s125/decision.txt); a5b step 250: $DEC"
push "E04 R03: a5b step 250 $DEC"

# ---------------- 5. evaluations
case "$DEC" in
  PASS*)
    st --set stage="5. imprinting evaluations (a T=1, a T 0.7, b default, b Dismissive, c)" --set evals="running" --set next="6. wrap-up"
    push "E04 R03: step 5 started"
    say "step 5 start"
    bash $R03/scripts/run_step8.sh
    say "step 5 done"
    st --set stage="5. evaluations done; 6. wrap-up" --set evals="done" --set next="6. README, push, adapters, remove pod"
    ;;
  *)
    say "no step 5: step-250 decision is '$DEC'"
    st --set stage="4 done; step 5 not run (step-250 decision: $DEC)" --set evals="not run (rule)" --set next="6. README, push, adapters, remove pod"
    ;;
esac
push "E04 R03: chain done"
say "CHAIN DONE"
