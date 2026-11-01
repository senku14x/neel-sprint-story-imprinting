#!/usr/bin/env bash
# E04 R04 steps 6-7 on one GPU (R03's chain.sh, changed for R04's rules):
#   runs only if r04/gate.txt starts with TRAIN and data/train_a5bq.jsonl exists
#   6. train a5bq straight through to step 250 (train_arm.sh, the 001 recipe; OOM -> restart from scratch with 2 x 16)
#   7. after training, one at a time on the GPU (check.sh, the teammate's 001 definition, as in R02/R03):
#        a. setup (parent): chat entropy 0.55-0.65 and garbled <= 8/50 -> PASS, else stop and report
#        b. a5bq step 125: report only
#        c. a5bq step 250: report only; garbled <= 8/50 makes step 8 (Hugging Face upload) run
#      Every check is re-judged until all 50 conversations are scored before its line is written (else UNKNOWN).
# Pushes after each stage. Step 8 and the wrap-up are run separately.
set -uo pipefail
R04=/workspace/e04/r04; V=/workspace/e03/venvs; LOG=$R04/logs/chain.log
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
st() { /workspace/venvs/gpu/bin/python -I $R04/scripts/status.py "$@" > /dev/null 2>&1; }
push() { bash $R04/scripts/push.sh "$1" >> $R04/logs/push.log 2>&1 && say "pushed: $1" || say "PUSH FAILED: $1"; }
export GPU=0
grep -q '^TRAIN' $R04/gate.txt 2>/dev/null || { say "gate is not TRAIN: $(head -1 $R04/gate.txt 2>/dev/null); chain not run"; exit 1; }
[ -s $R04/data/train_a5bq.jsonl ] || { say "data/train_a5bq.jsonl missing; chain not run"; exit 1; }

# ---------------- 6. training
if ! grep -q '^exit 0' $R04/logs/train_a5bq.times 2>/dev/null; then
  st --set stage="6. training a5bq (250 steps, about 80 minutes)" --set next="7. health checks after training: parent, a5bq step 125, a5bq step 250"
  push "E04 R04: training a5bq started"
  say "training start"
  bash $R04/scripts/train_arm.sh a5bq 0
  say "training finished: $(tail -1 $R04/logs/train_a5bq.times)"
fi
RD=$R04/runs/a5bq_s0; grep -q "_mb2" $R04/logs/train_a5bq.times && RD=$R04/runs/a5bq_s0_mb2
if [ ! -f $RD/final/adapter_model.safetensors ] || [ ! -f $RD/step125/adapter_model.safetensors ]; then
  say "TRAINING FAILED: snapshots missing in $RD"
  st --set stage="6. training FAILED (snapshots missing)" --set problems="training did not produce step125/final; see logs/train_a5bq*.log" --set next="report and stop"
  push "E04 R04: training failed"
  exit 1
fi
mkdir -p $R04/results/training/a5bq_s0
cp $RD/train_log.jsonl $RD/train_meta.json $R04/results/training/a5bq_s0/ 2>/dev/null
sha256sum $RD/step125/adapter_model.safetensors $RD/final/adapter_model.safetensors $RD/step125/adapter_config.json $RD/final/adapter_config.json \
  > $R04/results/training/a5bq_s0/snapshot_hashes.txt
/workspace/venvs/gpu/bin/python -I $R04/scripts/train_report.py > $R04/results/training/a5bq_s0/train_report.txt 2>&1
say "snapshots hashed; $(head -2 $R04/results/training/a5bq_s0/train_report.txt | tr '\n' ' ')"
st --set stage="6. training done; 7. health checks" --set next="7a. setup check (parent)"
push "E04 R04: a5bq trained to step 250"

# ---------------- 7. health checks
prep() {  # $1 = check name, $2 = vLLM model name, $3 = snapshot dir (garble model; "parent" = no adapter), $4 = health adapter dir, $5 = its name
  local D=$R04/checks/$1; mkdir -p $D
  if [ "$2" = "parent" ]; then
    echo '[{"name": "parent"}]' > $D/vllm_models.json
  else
    [ -d $R04/lora_vllm/$2 ] || $V/si/bin/python $R04/src/remap_lora_for_vllm.py $3 $R04/lora_vllm/$2 >> $LOG 2>&1
    sha256sum $3/adapter_model.safetensors $3/adapter_config.json > $D/adapter_hash.txt
    echo "[{\"name\": \"$2\", \"lora\": \"$R04/lora_vllm/$2\"}]" > $D/vllm_models.json
  fi
  echo "[{\"name\": \"$5\", \"path\": \"$4\"}]" > $D/health_adapters.json
}
decide() {  # $1 = check name, $2 = kind, $3 = model name -> decision.txt
  local D=$R04/checks/$1 p
  for p in 1 2 3 4 5 6 7 8; do
    /workspace/venvs/gpu/bin/python -I $R04/scripts/decide.py $D $2 $3 > $D/decision.tmp 2>&1 && break
    say "check $1: $(cat $D/decision.tmp); re-judging (extra pass $p)"
    sleep 30
    ( source $R04/scripts/env.sh; unset PYTHONPATH; export API_LEDGER=$R04/logs/ledger_openrouter_judge.jsonl API_CAP_USD=5 JUDGE_RPM=18
      $V/si/bin/python -I $R04/scripts/run_judge_paced.py $D/rollouts_T1.jsonl $D/judgments_T1.jsonl --concurrency 32 >> $D/judge.log 2>&1 )
    $V/si/bin/python -I $R04/scripts/garble_summary.py $D > $D/summary.txt 2>&1
  done
  /workspace/venvs/gpu/bin/python -I $R04/scripts/decide.py $D $2 $3 final > $D/decision.txt 2>&1
  rm -f $D/decision.tmp
  say "check $1 decision: $(cat $D/decision.txt)"
}
run_check() {  # $1 = check name
  local D=$R04/checks/$1
  if grep -q "CHECK DONE" $D/check.log 2>/dev/null; then say "check $1 already done"; return; fi
  say "check $1 start"
  bash $R04/scripts/check.sh $1 $D/vllm_models.json $D/health_adapters.json
  say "check $1 done"
}

# a. setup (parent). health.py needs one adapter; the parent's rows are computed with adapters disabled, so a5bq's step-125
#    adapter is loaded only to run it (the decision uses the parent rows only).
prep setup parent - $RD/step125 a5bq_B_s125
st --set stage="7a. setup check (parent)" --set next="7b. a5bq step-125 check (report only)"
run_check setup
decide setup setup parent
st --set checks="setup: $(cat $R04/checks/setup/decision.txt)"
push "E04 R04: setup check $(cut -c1-4 $R04/checks/setup/decision.txt)"
if ! grep -q '^PASS' $R04/checks/setup/decision.txt; then
  say "SETUP CHECK DID NOT PASS: stopping (brief step 7.1)"
  st --set stage="stopped: setup check did not pass" --set problems="setup check: $(cat $R04/checks/setup/decision.txt)" --set next="report and stop"
  push "E04 R04: setup check did not pass; stopped"
  exit 1
fi

# b. a5bq step 125 (report only)
prep a5bq_s125 a5bq_B_s125 $RD/step125 $RD/step125 a5bq_B_s125
st --set stage="7b. a5bq step-125 check (report only)" --set next="7c. a5bq step-250 check (report only; upload if garbled <= 8/50)"
run_check a5bq_s125
decide a5bq_s125 s125 a5bq_B_s125
st --set checks="setup: $(cat $R04/checks/setup/decision.txt); a5bq step 125: $(cat $R04/checks/a5bq_s125/decision.txt)"
push "E04 R04: a5bq step 125 $(cat $R04/checks/a5bq_s125/decision.txt)"

# c. a5bq step 250 (report only; sets whether step 8 runs)
prep a5bq_s250 a5bq_B_s250 $RD/final $RD/final a5bq_B_s250
st --set stage="7c. a5bq step-250 check (report only)" --set next="8. Hugging Face upload if garbled <= 8/50; 9. wrap-up"
run_check a5bq_s250
decide a5bq_s250 s250 a5bq_B_s250
DEC=$(cat $R04/checks/a5bq_s250/decision.txt)
st --set checks="setup: $(cat $R04/checks/setup/decision.txt); a5bq step 125: $(cat $R04/checks/a5bq_s125/decision.txt); a5bq step 250: $DEC" \
   --set stage="7 done (checks); next 8/9" --set next="8. Hugging Face upload if step 250 garbled <= 8/50; 9. README, push, remove pod"
push "E04 R04: a5bq step 250 $DEC"
say "CHAIN DONE"
