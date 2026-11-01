#!/usr/bin/env bash
# R05 stage for one fine-tune: stop the running vLLM server, fixed-text pass + merge (one GPU job), serve the merged model,
# then the teammate's fluency conversations, GSM8K and the story continuations in parallel, then their API judging.
#   bash stage.sh hc_db_s0
set -u
M=$1
source /workspace/si36/env.sh
cd /workspace/si36/r05
PY="/workspace/venvs/gpu/bin/python -I"
log () { echo "$(date -u +%H:%M:%S) [$M] $*" | tee -a logs/stage.log; }

log "stage start"
pkill -f "vllm serve" ; for i in $(seq 1 60); do pgrep -f "vllm serve" >/dev/null || break; sleep 5; done
sleep 10; log "server stopped; GPU memory $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"

$PY code/fixed_stats_merge.py --model $M > logs/fixed_stats_merge_$M.log 2>&1; rc=$?
log "fixed_stats_merge exit $rc"; [ $rc -ne 0 ] && { log "STAGE FAILED at merge"; exit 1; }

bash serve_r05.sh /scratch/r05/merged/$M 8000 $M > logs/serve_$M.out 2>&1; rc=$?
log "serve exit $rc: $(tail -1 logs/serve_$M.out)"; [ $rc -ne 0 ] && { log "STAGE FAILED at serve"; exit 1; }

$PY code/eo7_gen.py --model $M --settings T1,T07,T1mp05 > logs/eo7_gen_$M.log 2>&1 & P1=$!
$PY code/gsm8k_r05.py --model $M > logs/gsm8k_$M.log 2>&1 & P2=$!
$PY code/story_continue.py --model $M > logs/story_cont_$M.log 2>&1 & P3=$!
wait $P3; log "story_continue exit $?"
$PY code/story_continue.py --model $M --glm > logs/story_glm_$M.log 2>&1 & P4=$!
wait $P1; log "eo7_gen exit $?"
$PY code/eo7_judge.py --model $M --settings T1,T07,T1mp05 > logs/eo7_judge_$M.log 2>&1 & P5=$!
wait $P2; log "gsm8k exit $?"
wait $P4; log "story_glm exit $?"
wait $P5; log "eo7_judge exit $?"
log "STAGE DONE"
