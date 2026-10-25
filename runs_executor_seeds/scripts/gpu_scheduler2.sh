#!/bin/bash
# gpu_scheduler2.sh — v2 after the audit (25 Oct ~02:25): judging moved to judge_daemon.sh (waits on done/ only); eval windows
# fail closed (start check, failed/ re-queued + one retry); queueing exit codes checked; pre-registered step-1 loss gates for
# 015 (vs pilot) and 016 (vs box-1 B_s0 / box-2 A_s1); 015 step188 --mid added. v1 = gpu_scheduler.sh (exclusive GPU phases, 01:50). Replaces phase1_chain.sh after co-locating
# vLLM with training slowed training 15 -> 40-175 s/step. Order:
#   B_s1 (already training, pid $B_S1_PID) -> A_s2 -> B_s2 -> EVAL WINDOW 1 (all 014 jobs, 1xx) -> health 014
#   -> 015 regenB_s0 (step-1 loss parity vs pilot) -> regenB_s1 -> 016 mix010_B_s0 -> mix010_A_s1
#   -> EVAL WINDOW 2 (2xx 015, 3xx 016 incl. prefill tokgen, 6xx 017) -> health 015/016/017 -> prefill labels + analysis.
# Recipes are 001's train.py defaults; expandable_segments = allocator only. One worker per window = one eval config.
set -u
S1="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
S16="/workspace/Neel Sprint/experiments/reproduction/016_replay010_replication/src"
S17="/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src"
D="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows"
DA="$D/helpful-bees-vs-dismissive-crows.jsonl"; DB="$D/helpful-crows-vs-dismissive-bees.jsonl"
REGEN="/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl"
REPLAY="/workspace/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl"
PI=/workspace/story-imprinting-persona-pilot/imprinting_extension
PY=/root/venvs/si/bin/python
LOG=/root/runs/gpu_scheduler.log
log() { echo "$(date -u +%FT%T) $*" >> $LOG; }
gpu_free() { until [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 15; done; sleep 20; }

# train <run> <data> <seed> <check_step1_loss|-> [extra train.py args...]
train() {
  local run=$1 data=$2 seed=$3 chk=$4; shift 4
  if [ -f /root/runs/$run/final/adapter_model.safetensors ]; then log "$run already trained"; return 0; fi
  for attempt in 1 2; do
    gpu_free
    if [ $attempt = 2 ] && [ -d /root/runs/$run ]; then mv /root/runs/$run /root/runs/${run}_failed_attempt1; fi
    log "train $run attempt $attempt (seed $seed $*)"
    ( cd "$S1" && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True exec $PY train.py --data "$data" --out /root/runs/$run --seed $seed "$@" ) > /root/runs/$run.log.$attempt 2>&1 &
    local tp=$!
    if [ "$chk" != "-" ]; then  # pre-registered step-1 gate: story loss within 1e-3 of the reference (015/016 design specs)
      until [ -s /root/runs/$run/train_log.jsonl ] || ! kill -0 $tp 2>/dev/null; do sleep 10; done
      if [ -s /root/runs/$run/train_log.jsonl ]; then
        local ok=$(python3 -c "import json;l=json.loads(open('/root/runs/$run/train_log.jsonl').readline());d=abs(l['story_loss']-$chk);print('PASS' if d<=1e-3 else 'FAIL', l['story_loss'], d)")
        log "$run step-1 story-loss parity vs reference $chk: $ok"
        if [[ $ok == FAIL* ]]; then kill $tp; sleep 30; log "STOP: $run step-1 parity failed (pre-registered gate)"; exit 1; fi
      fi
    fi
    wait $tp
    [ -f /root/runs/$run/final/adapter_model.safetensors ] && { log "$run trained"; return 0; }
    log "$run attempt $attempt FAILED (see /root/runs/$run.log.$attempt)"
  done
  log "STOP: $run failed twice"; exit 1
}

# queue <name> <adapter dir> <prefix> [mid188]: full package on final, --mid on step125 (and step188 if asked); 001's queue script.
# Judging is done by judge_daemon.sh. A queueing error is logged as ALERT (training continues; the evals must be queued by hand).
queue() {
  local name=$1 dir=$2 p=$3 m188=${4:-}
  ( cd "$S1" && $PY queue_model_evals.py --name $name --adapter $dir/final --prefix $p ) >> $LOG 2>&1 || log "ALERT: queueing $name final failed"
  ( cd "$S1" && $PY queue_model_evals.py --name ${name}_step125 --adapter $dir/step125 --prefix $((p+5)) --mid ) >> $LOG 2>&1 || log "ALERT: queueing ${name}_step125 failed"
  if [ -n "$m188" ]; then
    ( cd "$S1" && $PY queue_model_evals.py --name ${name}_step188 --adapter $dir/step188 --prefix $((p+8)) --mid ) >> $LOG 2>&1 || log "ALERT: queueing ${name}_step188 failed"
  fi
}

# eval_window <stop name>: one worker (full GPU, Gate-0 config) until the stop job; retried once if jobs remain
eval_window() {
  local stop=$1
  for attempt in 1 2; do
    gpu_free
    rm -f /root/runs/vq/*_stop.json; echo '{"type": "stop"}' > /root/runs/vq/$stop.json
    [ -f /root/runs/vllm_worker.log ] && mv /root/runs/vllm_worker.log /root/runs/vllm_worker_$(date +%H%M%S).log
    ( cd "$S17" && VLLM_LENS_DISABLE=1 exec /root/venvs/vl/bin/python vllm_worker.py --queue /root/runs/vq --gpu_mem 0.90 \
        --max_num_seqs 256 --max_num_batched_tokens 16384 --max_loras 4 ) > /root/runs/vllm_worker.log 2>&1 &
    local wp=$!; echo $wp > /root/runs/worker.pid
    log "eval window $stop attempt $attempt: worker $wp from 017/src (0.90/256)"
    until grep -qE "engine config extras|worker ready" /root/runs/vllm_worker.log || ! kill -0 $wp 2>/dev/null; do sleep 5; done
    if ! grep -q "engine config extras" /root/runs/vllm_worker.log; then  # fail closed: engine never started
      local ec=$(ps -eo pid,args | awk '/[E]ngineCore/{print $1}'); kill $wp $ec 2>/dev/null; sleep 20; kill -9 $wp $ec 2>/dev/null
      log "ALERT: worker $wp reported ready (or died) without an engine; killed"
    else
      log "worker start: $(grep -m1 'engine config extras' /root/runs/vllm_worker.log | cut -c1-160)"
      grep -q "engine config extras: {'async_scheduling': True" /root/runs/vllm_worker.log || log "WARNING: worker did not start with the Gate-0 config (async scheduling); all jobs of this window share its config"
      while kill -0 $wp 2>/dev/null; do
        [ -n "$(ls /root/runs/vq/failed/ 2>/dev/null)" ] && { local ec=$(ps -eo pid,args | awk '/[E]ngineCore/{print $1}'); kill $wp $ec 2>/dev/null; sleep 20; kill -9 $wp $ec 2>/dev/null; log "ALERT: job(s) failed in window $stop: $(ls /root/runs/vq/failed | tr '\n' ' '); worker killed"; break; }
        sleep 15
      done
    fi
    for f in /root/runs/vq/failed/*.json; do [ -f "$f" ] && mv "$f" /root/runs/vq/ && log "re-queued $(basename $f)"; done
    local left=$(ls /root/runs/vq/*.json 2>/dev/null | xargs -r -n1 basename | awk -v s="$stop.json" '$0 < s' | tr '\n' ' ')
    if [ -z "$left" ]; then log "eval window $stop done"; return 0; fi
    log "eval window $stop attempt $attempt: jobs left: $left"
  done
  log "STOP: eval window $stop failed twice"; exit 1
}

health() {  # health <out name> <adapters json>
  gpu_free; log "health $1"
  ( cd "$S1" && $PY health.py --panel eval_data/health_panel.jsonl --adapters $2 --out /root/runs/health/$1.json ) > /root/runs/health/$1.log 2>&1
  [ -f /root/runs/health/$1.json ] && log "health $1 done" || log "health $1 FAILED (see log)"
}

log "scheduler v2 start; waiting for B_s1 (pid $B_S1_PID)"
while kill -0 $B_S1_PID 2>/dev/null; do sleep 30; done
if [ -f /root/runs/B_s1/final/adapter_model.safetensors ]; then log "B_s1 trained"; else log "B_s1 attempt 1 FAILED"; train B_s1 "$DB" 1 -; fi
queue new_B_s1 /root/runs/B_s1 120
train A_s2 "$DA" 2 -; queue new_A_s2 /root/runs/A_s2 130
train B_s2 "$DB" 2 -; queue new_B_s2 /root/runs/B_s2 140

eval_window 199_stop
cat > /root/runs/health/adapters_014.json <<EOF
[{"name": "new_A_s1", "path": "/root/runs/A_s1/final"}, {"name": "new_A_s1_step125", "path": "/root/runs/A_s1/step125"},
 {"name": "new_B_s1", "path": "/root/runs/B_s1/final"}, {"name": "new_B_s1_step125", "path": "/root/runs/B_s1/step125"},
 {"name": "new_A_s2", "path": "/root/runs/A_s2/final"}, {"name": "new_A_s2_step125", "path": "/root/runs/A_s2/step125"},
 {"name": "new_B_s2", "path": "/root/runs/B_s2/final"}, {"name": "new_B_s2_step125", "path": "/root/runs/B_s2/step125"}]
EOF
health health_014 /root/runs/health/adapters_014.json

train regenB_s0 "$REGEN" 0 1.3208968381962698; queue regenours_B_s0 /root/runs/regenB_s0 210 mid188
train regenB_s1 "$REGEN" 1 -; queue regenours_B_s1 /root/runs/regenB_s1 220 mid188
train mix010_B_s0 "$DB" 0 2.865788139788819 --replay "$REPLAY" --replay_ratio 0.1; queue mix010_B_s0 /root/runs/mix010_B_s0 310
train mix010_A_s1 "$DA" 1 2.8354277304795894 --replay "$REPLAY" --replay_ratio 0.1; queue mix010_A_s1 /root/runs/mix010_A_s1 320
cat > /root/runs/vq/330_tokgen_prefill016.json <<EOF
{"type": "tokgen", "inp": "/root/runs/p016/prompts.jsonl", "out": "/root/runs/p016/gen.jsonl", "n": 1, "temperature": 0.7,
 "max_tokens": 48, "models": [{"name": "mix010_B_s0", "lora": "/root/runs/lora_vllm/mix010_B_s0"},
 {"name": "mix010_A_s1", "lora": "/root/runs/lora_vllm/mix010_A_s1"}]}
EOF
log "queued 330_tokgen_prefill016"

eval_window 999_stop
cat > /root/runs/health/adapters_015_016.json <<EOF
[{"name": "regenours_B_s0", "path": "/root/runs/regenB_s0/final"}, {"name": "regenours_B_s0_step125", "path": "/root/runs/regenB_s0/step125"},
 {"name": "regenours_B_s1", "path": "/root/runs/regenB_s1/final"}, {"name": "regenours_B_s1_step125", "path": "/root/runs/regenB_s1/step125"},
 {"name": "mix010_B_s0", "path": "/root/runs/mix010_B_s0/final"}, {"name": "mix010_B_s0_step125", "path": "/root/runs/mix010_B_s0/step125"},
 {"name": "mix010_A_s1", "path": "/root/runs/mix010_A_s1/final"}, {"name": "mix010_A_s1_step125", "path": "/root/runs/mix010_A_s1/step125"}]
EOF
health health_015_016 /root/runs/health/adapters_015_016.json
cat > /root/runs/health/adapters_017.json <<EOF
[{"name": "pilot_HS_A_s0", "path": "$PI/overnight_sarcastic/ckpt/HS_A_s0/final"}, {"name": "pilot_HS_A_s0_step125", "path": "$PI/overnight_sarcastic/ckpt/HS_A_s0/mid_step125"},
 {"name": "pilot_HS_B_s0", "path": "$PI/overnight_sarcastic/ckpt/HS_B_s0/final"}, {"name": "pilot_HS_B_s0_step125", "path": "$PI/overnight_sarcastic/ckpt/HS_B_s0/mid_step125"},
 {"name": "pilot_HS_A_s1", "path": "$PI/organism_checks/ckpt/HS_A_s1/final"}, {"name": "pilot_HS_A_s1_step125", "path": "$PI/organism_checks/ckpt/HS_A_s1/mid_step125"},
 {"name": "pilot_HS_B_s1", "path": "$PI/organism_checks/ckpt/HS_B_s1/final"}, {"name": "pilot_HS_B_s1_step125", "path": "$PI/organism_checks/ckpt/HS_B_s1/mid_step125"},
 {"name": "pilot_HSab_A_s0", "path": "$PI/organism_checks/ckpt/HSab_A_s0/final"}, {"name": "pilot_HSab_A_s0_step125", "path": "$PI/organism_checks/ckpt/HSab_A_s0/mid_step125"},
 {"name": "pilot_HSab_B_s0", "path": "$PI/organism_checks/ckpt/HSab_B_s0/final"}, {"name": "pilot_HSab_B_s0_step125", "path": "$PI/organism_checks/ckpt/HSab_B_s0/mid_step125"}]
EOF
health health_017 /root/runs/health/adapters_017.json

log "prefill labels (016)"
( set -a; . /root/.config/openrouter_seeds.env; set +a
  export API_LEDGER="/workspace/Neel Sprint/_sessions/executor-seeds/api_ledger_seeds.jsonl" API_CAP_USD=48
  exec 9>/tmp/si_judge.lock; flock 9
  cd "$S16" && for i in 1 2 3; do python3 judge_animal.py --gen /root/runs/p016/gen.jsonl --prompts /root/runs/p016/prompts.jsonl --out /root/runs/p016/labels.jsonl; done
  OMP_NUM_THREADS=8 python3 analyze_prefill.py --gen /root/runs/p016/gen.jsonl --labels /root/runs/p016/labels.jsonl --out /root/runs/p016/prefill_analysis.json ) >> /root/runs/p016/prefill.log 2>&1
log "prefill done"
log "SCHEDULER DONE"
