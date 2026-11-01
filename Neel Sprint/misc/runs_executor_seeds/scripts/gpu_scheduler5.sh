#!/bin/bash
# gpu_scheduler5.sh — v5 (25 Oct ~04:00): v4 + the vLLM venv's bin/ on PATH for the worker (vLLM JIT needs `ninja`, which lives in
# /root/venvs/vl/bin; v4 called the venv python without activating it and every engine config failed).
# (v4 header follows) gpu_scheduler4.sh — v4 (25 Oct ~02:35): v3 + every GPU process pinned to the GPU's NUMA node (taskset -c 0-87). Cause: on CPUs of
# socket 1 this VM gives 0.6 GiB/s host->GPU and 5x kernel-launch latency (vs 50.9 GiB/s on socket 0); unpinned processes land randomly.
# (v3 header follows) gpu_scheduler3.sh — v3 = the user's change of plan (25 Oct ~02:10): 014 two seeds, finals only, T1+min-p only on A_s1/B_s1,
# order 014 -> health -> 017 -> health -> 016 (+prefill) -> health; 015 on hold. Functions below are v2's unchanged.
# (v2 header follows) gpu_scheduler2.sh — v2 after the audit (25 Oct ~02:25): judging moved to judge_daemon.sh (waits on done/ only); eval windows
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
NUMA0=0-87   # CPUs of the GPU's NUMA node (nvidia-smi topo -m)
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
    ( cd "$S1" && export PATH="/root/venvs/si/bin:$PATH" && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True exec taskset -c $NUMA0 $PY train.py --data "$data" --out /root/runs/$run --seed $seed "$@" ) > /root/runs/$run.log.$attempt 2>&1 &
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
    ( cd "$S17" && export PATH="/root/venvs/vl/bin:$PATH" && VLLM_LENS_DISABLE=1 exec taskset -c $NUMA0 /root/venvs/vl/bin/python vllm_worker.py --queue /root/runs/vq --gpu_mem 0.90 \
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
  ( cd "$S1" && export PATH="/root/venvs/si/bin:$PATH" && taskset -c $NUMA0 $PY health.py --panel eval_data/health_panel.jsonl --adapters $2 --out /root/runs/health/$1.json ) > /root/runs/health/$1.log 2>&1
  [ -f /root/runs/health/$1.json ] && log "health $1 done" || log "health $1 FAILED (see log)"
}


# ===== v3 main (user's change of plan, 25 Oct ~02:10) =====
# queue_final <name> <adapter dir> <prefix> <mp|nomp>: full package on final only (001's queue script); nomp -> T1+min-p job cancelled
queue_final() {
  local name=$1 dir=$2 p=$3 mp=$4
  ( cd "$S1" && $PY queue_model_evals.py --name $name --adapter $dir/final --prefix $p ) >> $LOG 2>&1 || log "ALERT: queueing $name failed"
  if [ "$mp" = "nomp" ]; then mkdir -p /root/runs/vq_cancelled; mv /root/runs/vq/${p}c_T1mp05_$name.json /root/runs/vq_cancelled/ && log "cancelled ${p}c_T1mp05_$name (user plan)"; fi
}
mkdir -p /root/runs/flags
log "scheduler v5 start (v4 + venv PATH for the worker)"
train B_s1 "$DB" 1 -
queue_final new_B_s1 /root/runs/B_s1 120 mp

# 014 window: new_A_s1 (110 a,b,c), new_B_s1 (120 a,b,c), new_A_s0_box2 (150 a,b), new_B_s0_box2 (160 a,b)
eval_window 199_stop
printf '%s\n' '[{"name": "new_A_s1", "path": "/root/runs/A_s1/final"}, {"name": "new_B_s1", "path": "/root/runs/B_s1/final"}]' > /root/runs/health/adapters_014.json
health health_014 /root/runs/health/adapters_014.json
touch /root/runs/flags/014_eval_and_health_done; log "014 window + health done"

# 017 window: parent (600a, 4 personas, trigger), 6 pilot adapters (6x0 a,b), crossed control (670a, 675a)
eval_window 699_stop
python3 - "$PI" > /root/runs/health/adapters_017.json <<'PYEOF'
import json, sys
pi = sys.argv[1]
ads = [("HS_A_s0", "overnight_sarcastic"), ("HS_B_s0", "overnight_sarcastic"), ("HS_A_s1", "organism_checks"),
       ("HS_B_s1", "organism_checks"), ("HSab_A_s0", "organism_checks"), ("HSab_B_s0", "organism_checks")]
print(json.dumps([{"name": f"pilot_{r}", "path": f"{pi}/{d}/ckpt/{r}/final"} for r, d in ads]))
PYEOF
health health_017 /root/runs/health/adapters_017.json
touch /root/runs/flags/017_eval_and_health_done; log "017 window + health done"

# 016: two replay runs with step-1 gates, final-only evals without T1+min-p, prefill tokgen
train mix010_B_s0 "$DB" 0 2.865788139788819 --replay "$REPLAY" --replay_ratio 0.1; queue_final mix010_B_s0 /root/runs/mix010_B_s0 310 nomp
train mix010_A_s1 "$DA" 1 2.8354277304795894 --replay "$REPLAY" --replay_ratio 0.1; queue_final mix010_A_s1 /root/runs/mix010_A_s1 320 nomp
printf '%s\n' '{"type": "tokgen", "inp": "/root/runs/p016/prompts.jsonl", "out": "/root/runs/p016/gen.jsonl", "n": 1, "temperature": 0.7, "max_tokens": 48, "models": [{"name": "mix010_B_s0", "lora": "/root/runs/lora_vllm/mix010_B_s0"}, {"name": "mix010_A_s1", "lora": "/root/runs/lora_vllm/mix010_A_s1"}]}' > /root/runs/vq/330_tokgen_prefill016.json
log "queued 330_tokgen_prefill016"
eval_window 399_stop
printf '%s\n' '[{"name": "mix010_B_s0", "path": "/root/runs/mix010_B_s0/final"}, {"name": "mix010_A_s1", "path": "/root/runs/mix010_A_s1/final"}]' > /root/runs/health/adapters_016.json
health health_016 /root/runs/health/adapters_016.json

log "prefill labels (016)"
( set -a; . /root/.config/openrouter_seeds.env; set +a
  export API_LEDGER="/workspace/Neel Sprint/_sessions/executor-seeds/api_ledger_seeds.jsonl" API_CAP_USD=48
  exec 9>/tmp/si_judge.lock; flock 9
  cd "$S16" || exit 1
  for i in 1 2 3; do python3 judge_animal.py --gen /root/runs/p016/gen.jsonl --prompts /root/runs/p016/prompts.jsonl --out /root/runs/p016/labels.jsonl; done
  OMP_NUM_THREADS=8 python3 analyze_prefill.py --gen /root/runs/p016/gen.jsonl --labels /root/runs/p016/labels.jsonl --out /root/runs/p016/prefill_analysis.json ) >> /root/runs/p016/prefill.log 2>&1
touch /root/runs/flags/016_done; log "prefill done"
log "SCHEDULER DONE (015 on hold: not started)"
