#!/bin/bash
# sw043 Amendment A (post hoc) box-1 driver, detached: pulls each node job when its marker appears, judges and analyses it, and writes
# the final tables. Idempotent and resumable: re-launching it skips every step whose local marker exists.
#   setsid -f nohup bash box1_driver.sh > /workspace/runs_executor/sw043/amendA/driver.log 2>&1 < /dev/null
# Markers (in R=/workspace/runs_executor/sw043/amendA): eval_<X>/POSTED, n_eval/T1_JUDGED, n_eval/<p0x>_JUDGED, n_eval/ENACT_PULLED,
# ANALYSIS_DONE, KEY_UNDER_40, KEY_STOP. Hard stop: key limit_remaining < $5 (or a 402 inside judge_run, which judge_guard61 surfaces).
set -u
R=/workspace/runs_executor/sw043/amendA; ND=/root/runs/sw043/amendA
S43="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src"; K="$S43/e4/keep"; AN="$S43/amendA/amendA_an.py"
T40="/workspace/Neel Sprint/experiments/sprint_work/040_chainP_premise_and_p0/src/premise/judge40_template.txt"
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=15"; NODE=root@<node-ip>
RS() { timeout 1800 rsync -a -e "$SSH" "$@"; }
CAP=20
log() { echo "[$(date -u +%FT%TZ)] $*"; }
onnode() { timeout 30 $SSH $NODE "test -e '$1'"; }
key() { python3 -I "$S43/redirect/keylim.py" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['limit_remaining'])" 2>/dev/null || echo NA; }
keycheck() { L=$(key); log "key limit_remaining $L before $1"; [ "$L" = NA ] && return 0
  python3 -c "import sys; sys.exit(0 if float('$L') >= 40 else 1)" || { [ -f $R/KEY_UNDER_40 ] || { echo "$(date -u +%FT%TZ) $L" > $R/KEY_UNDER_40; log "KEY_UNDER_40 $L"; }; }
  python3 -c "import sys; sys.exit(0 if float('$L') >= 5 else 1)" || { echo "$(date -u +%FT%TZ) $L" > $R/KEY_STOP; log "KEY_STOP $L"; exit 3; }; }
J() { python3 "$K/judge_guard61.py" --exp sw043 --cap $CAP "$@"; }
alias_arm() { a=$1; for c in step015 step030 step045 final; do
    [ -f /workspace/runs_executor/sw043/train/$a/$c/adapter_model.safetensors ] || { mkdir -p /workspace/runs_executor/sw043/train/$a; RS $NODE:/root/runs/sw043/train/$a/$c/ /workspace/runs_executor/sw043/train/$a/$c/; }
    mkdir -p /root/runs/sw043/train/$a; ln -sfn /workspace/runs_executor/sw043/train/$a/$c /root/runs/sw043/train/$a/$c; done; }
declare -A ARM=( [A_dis]=red_hdA0_dis [B_dis]=red_hdB0_dis [B_help]=red_hdB0_help [A_help]=red_hdA0_help [N]="red_N_cas red_N_help" )
mkdir -p $R/n_eval
log "driver start pid $$"
while true; do
  for X in A_dis B_dis B_help A_help N; do
    D=$R/eval_$X
    [ -f $D/POSTED ] && continue
    if onnode $ND/eval_$X/GATE_FAIL; then [ -f $D/GATE_FAIL_SEEN ] || { mkdir -p $D; touch $D/GATE_FAIL_SEEN; log "GATE_FAIL on node for eval_$X"; }; continue; fi
    onnode $ND/eval_$X/GPU_DONE || continue
    log "eval_$X: GPU_DONE -> pull + post"
    mkdir -p $D; RS --exclude lora_vllm $NODE:$ND/eval_$X/ $D/ || continue
    for a in ${ARM[$X]}; do alias_arm $a; done
    keycheck "post eval_$X"
    bash "$S43/e4/post61.sh" $D sw043 $CAP > $D/post.log 2>&1; rc=$?
    log "eval_$X post61 rc=$rc"; [ -f $D/ANALYSIS_READY ] && touch $D/POSTED
  done
  if [ ! -f $R/n_eval/T1_JUDGED ] && onnode $ND/n_eval/t1.DONE; then
    log "N t1 -> pull + judge"; mkdir -p $R/n_eval/t1; RS $NODE:$ND/n_eval/t1/ $R/n_eval/t1/ && RS $NODE:$ND/n_eval/models_vllm.json $NODE:$ND/n_eval/remap_G1.json $R/n_eval/ && \
    python3 -I "$AN" t1_judgein && keycheck "N t1" && \
    J --rubric custom --template "$T40" --fields decline,register --ranges decline:0-10,register:0-3 --in $R/n_eval/t1/judgein_t1.jsonl --out $R/n_eval/t1/judged_t1.jsonl --part amendA_n_t1 && \
    touch $R/n_eval/T1_JUDGED; log "N t1 judged: $([ -f $R/n_eval/T1_JUDGED ] && echo ok || echo FAILED)"
  fi
  for p in p0a p0b; do
    if [ ! -f $R/n_eval/${p}_JUDGED ] && onnode $ND/n_eval/$p.DONE; then
      log "N $p -> pull + judge"; mkdir -p $R/n_eval/$p; RS $NODE:$ND/n_eval/$p/ $R/n_eval/$p/ && \
      python3 -I "$AN" p0_prep $p && keycheck "N $p" && \
      J --rubric habit --sample-frac 0.2 --strata-field stratum --always-field disagree --seed 0 --in $R/n_eval/$p/judgein_habit.jsonl --out $R/n_eval/$p/judged_habit.jsonl --part amendA_$p && \
      python3 -I "$AN" p0_widen $p && { [ ! -s $R/n_eval/$p/judgein_habit_all.jsonl ] || J --rubric habit --in $R/n_eval/$p/judgein_habit_all.jsonl --out $R/n_eval/$p/judged_habit_all.jsonl --part amendA_${p}_all; } && \
      touch $R/n_eval/${p}_JUDGED; log "N $p judged: $([ -f $R/n_eval/${p}_JUDGED ] && echo ok || echo FAILED)"
    fi
  done
  if [ ! -f $R/n_eval/ENACT_PULLED ] && onnode $ND/n_eval/enact.DONE; then
    mkdir -p $R/n_eval/enact; RS --exclude adapters_vllm $NODE:$ND/n_eval/enact/ $R/n_eval/enact/ && touch $R/n_eval/ENACT_PULLED; log "N enact pulled"
  fi
  n_mark=$(ls $R/eval_*/POSTED $R/n_eval/*_JUDGED $R/n_eval/ENACT_PULLED 2>/dev/null | wc -l)
  if [ "$n_mark" != "${last_mark:-x}" ]; then python3 -I "$AN" all > $R/amendA_an.log 2>&1 || true; last_mark=$n_mark; log "interim analysis ($n_mark markers)"; fi
  done_all=1
  for X in A_dis B_dis B_help A_help N; do [ -f $R/eval_$X/POSTED ] || done_all=0; done
  for m in T1_JUDGED p0a_JUDGED p0b_JUDGED ENACT_PULLED; do [ -f $R/n_eval/$m ] || done_all=0; done
  if [ $done_all = 1 ]; then python3 -I "$AN" all > $R/amendA_an.log 2>&1; touch $R/ANALYSIS_DONE; keycheck "end"; log "ANALYSIS_DONE"; exit 0; fi
  sleep 60
done
