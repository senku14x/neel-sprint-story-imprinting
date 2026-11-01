#!/usr/bin/env bash
# Exploratory smoke tests: Assistant Axis + persona vectors on untrained Qwen3.6-27B, judge GLM 5.3 Flash (OpenRouter).
# PREPARED, NOT YET RUN. Run only when the GPU is free (the preflight refuses otherwise). See PLAN.md.
#
#   bash run_smoke.sh all            # everything in the planned order (~25-30 min)
#   bash run_smoke.sh <stage> ...    # stages: preflight aa_gen aa_judge aa_judge_probe aa_act aa_vec pv_extract pv_vec summary
#
# Stage logs: logs/<stage>.log ; stage wall times: timings.jsonl ; OpenRouter key usage snapshots: logs/or_usage.jsonl
set -u
S=/workspace/si36/r05/smoke
source /workspace/si36/env.sh                       # HF_HOME=/workspace/hf, caches (vLLM / triton / inductor)
export PATH=/workspace/venvs/gpu/bin:$PATH
export CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export PYTHONPATH=$S/pydeps                         # jsonlines, fire, termcolor (missing from the venv); not -I for that reason
export HF_TOKEN="${HF_TOKEN:-unused-offline}"       # persona_vectors' config.setup_credentials() insists on it
PY=/workspace/venvs/gpu/bin/python
SNAP=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
GLM=z-ai/glm-5.3-flash-20260826
AAR=$S/assistant_axis/repo; AAO=$S/assistant_axis/out
PVR=$S/persona_vectors/repo; PVO=$S/persona_vectors/out
TRAIT=${TRAIT:-humorous}; NEG_NAME=${NEG_NAME:-serious}   # README: neg assistant_name = antonym, else "helpful"
AA_ROLES="pirate ghost demon poet detective therapist librarian trickster robot sage default"
SMOKE_CAP=${SMOKE_CAP:-2.00}                        # $ of OpenRouter spend allowed for the whole smoke run
mkdir -p $S/logs $S/assistant_axis/logs $S/persona_vectors/logs

judge_env() {   # both repos use openai.AsyncOpenAI(), which reads these two variables
  export OPENAI_API_KEY="$OPENROUTER_API_KEY" OPENAI_BASE_URL=https://openrouter.ai/api/v1 JUDGE_REASONING_EFFORT=low
}
or_usage() {    # free endpoint (no tokens): key usage in $, logged before/after API stages
  local u; u=$(curl -s --max-time 30 https://openrouter.ai/api/v1/key -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    | $PY -c 'import sys,json;print(json.load(sys.stdin)["data"]["usage"])' 2>/dev/null)
  [ -n "$u" ] && echo "{\"t\": $(date +%s), \"tag\": \"$1\", \"usage\": $u}" >> $S/logs/or_usage.jsonl; echo "${u:-nan}"
}
spend_ok() {
  [ -s $S/logs/or_usage.jsonl ] || or_usage start >/dev/null
  $PY - "$SMOKE_CAP" <<'EOF'
import json, sys
rows = [json.loads(l) for l in open("/workspace/si36/r05/smoke/logs/or_usage.jsonl")]
d = rows[-1]["usage"] - rows[0]["usage"]
print(f"smoke spend so far ${d:.4f} (cap ${float(sys.argv[1]):.2f})"); sys.exit(0 if d < float(sys.argv[1]) else 1)
EOF
}
gpu_free() {    # waits up to 90 s for the previous stage's processes to release the GPU, then refuses
  local used i
  for i in $(seq 1 18); do
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    [ "$used" -lt 2000 ] && ! pgrep -f "vllm serve" >/dev/null && return 0
    sleep 5
  done
  echo "GPU busy (${used} MiB used, or a vllm server is running): not starting"; nvidia-smi; return 1
}
run() {         # run <stage> <timeout_s> <cmd...> : logs, wall time, exit code
  local name=$1 to=$2; shift 2; local t0 t1 rc
  echo "$(date -u +%H:%M:%S) START $name"; t0=$(date +%s.%N)
  timeout --kill-after=60 "$to" "$@" > $S/logs/$name.log 2>&1; rc=$?   # timeout signals the whole process group (vLLM EngineCore too)
  t1=$(date +%s.%N)
  echo "{\"stage\": \"$name\", \"start\": $t0, \"end\": $t1, \"wall_s\": $(awk "BEGIN{print $t1 - $t0}"), \"rc\": $rc}" >> $S/timings.jsonl
  echo "$(date -u +%H:%M:%S) END $name rc=$rc ($(awk "BEGIN{printf \"%.1f\", ($t1 - $t0)/60}") min) log: logs/$name.log"
  return $rc
}

st_preflight() {
  gpu_free || return 1
  [ -d $SNAP ] && [ -f $AAR/pipeline/1_generate.py ] && [ -f $PVR/data_generation/trait_data_smoke/$TRAIT.json ] || { echo "missing files: run setup_copies.sh"; return 1; }
  [ -n "${OPENROUTER_API_KEY:-}" ] || { echo "OPENROUTER_API_KEY not set"; return 1; }
  $PY -c "import jsonlines, fire" || return 1
  echo "OpenRouter usage at start: $(or_usage start)"
}
st_aa_gen() {   # GPU (vLLM, one load): 10 roles + default at question_count 5 (275 generations) + probe roles at 20 and 60
  gpu_free || return 1
  run aa_gen 1500 $PY $S/assistant_axis/gen_with_probe.py --model $SNAP --question_count 5 --roles $AA_ROLES \
    --probe_roles jester mystic --probe_counts 20 60
}
st_aa_judge() { # API only: 250 judge calls (default.json has no eval_prompt and is not judged); second pass retries failures
  ( judge_env; export SMOKE_JUDGE_LEDGER=$S/assistant_axis/logs/judge_ledger.jsonl SMOKE_TAG=aa_tiny; cd $AAR
    $PY pipeline/3_judge.py --responses_dir $AAO/responses --roles_dir $AAR/data/roles/instructions --output_dir $AAO/scores \
      --judge_model $GLM --dry_run > $S/logs/aa_judge_dryrun.log 2>&1
    run aa_judge 900 $PY pipeline/3_judge.py --responses_dir $AAO/responses --roles_dir $AAR/data/roles/instructions \
      --output_dir $AAO/scores --judge_model $GLM --max_tokens 2000 --batch_size 50 --requests_per_second 100
    run aa_judge_retry 600 $PY pipeline/3_judge.py --responses_dir $AAO/responses --roles_dir $AAR/data/roles/instructions \
      --output_dir $AAO/scores --judge_model $GLM --max_tokens 2000 --batch_size 50 --requests_per_second 100 )
  echo "OpenRouter usage after aa_judge: $(or_usage after_aa_judge)"
}
st_aa_judge_probe() { # API only, optional: the 300 q=60 probe responses in ONE batch (--batch_size 300) = full-run judge pattern
  spend_ok || return 1
  ( judge_env; export SMOKE_JUDGE_LEDGER=$S/assistant_axis/logs/judge_ledger.jsonl SMOKE_TAG=aa_probe60; cd $AAR
    run aa_judge_probe 600 $PY pipeline/3_judge.py --responses_dir $S/assistant_axis/probe_q60/responses \
      --roles_dir $AAR/data/roles/instructions --output_dir $S/assistant_axis/probe_q60/scores --judge_model $GLM \
      --max_tokens 2000 --batch_size 300 --requests_per_second 100 )
  echo "OpenRouter usage after aa_judge_probe: $(or_usage after_aa_judge_probe)"
}
st_aa_act() {   # GPU (HF Qwen3_5ForCausalLM, hooks on model.model.layers[32])
  gpu_free || return 1
  ( cd $AAR; run aa_act 1200 $PY pipeline/2_activations.py --model $SNAP --responses_dir $AAO/responses \
      --output_dir $AAO/activations --layers 32 --batch_size 16 )
}
st_aa_vec() {   # CPU: per-role vectors (score==3 only; --min_count 1 because a role has only 25 responses) and the axis
  ( cd $AAR
    run aa_vectors 300 $PY pipeline/4_vectors.py --activations_dir $AAO/activations --scores_dir $AAO/scores \
      --output_dir $AAO/vectors --min_count 1
    run aa_axis 300 $PY pipeline/5_axis.py --vectors_dir $AAO/vectors --output $AAO/axis.pt )
}
st_pv_extract() { # GPU (vLLM, one load) + API: eval_persona pos then neg, 5 questions x 5 instruction pairs x 2 samples each
  gpu_free || return 1; spend_ok || return 1
  ( judge_env; export SMOKE_JUDGE_LEDGER=$S/persona_vectors/logs/judge_ledger.jsonl
    run pv_extract 1500 $PY $S/persona_vectors/extract_both.py --model $SNAP --trait $TRAIT --neg_name $NEG_NAME \
      --version smoke --n_per_question 2 --judge_model $GLM )
  echo "OpenRouter usage after pv_extract: $(or_usage after_pv_extract)"
}
st_pv_vec() {   # GPU (HF, output_hidden_states=True -> 65 hidden states)
  gpu_free || return 1
  ( cd $PVR; run pv_vec 1200 $PY generate_vec.py --model_name $SNAP \
      --pos_path $PVO/eval_persona_extract/${TRAIT}_pos_instruct.csv --neg_path $PVO/eval_persona_extract/${TRAIT}_neg_instruct.csv \
      --trait $TRAIT --save_dir $PVO/persona_vectors --threshold 50 )
}
st_summary() { $PY $S/summarize.py > $S/logs/summary.log 2>&1; tail -40 $S/logs/summary.log; }

if [ "${1:-}" = all ]; then
  st_preflight || exit 1
  st_aa_gen || { echo "aa_gen failed: see logs/aa_gen.log"; exit 1; }
  ( st_aa_judge; st_aa_judge_probe ) > $S/logs/aa_judge_chain.out 2>&1 &   # API-only, overlaps the HF activation pass
  JPID=$!
  st_aa_act
  st_pv_extract
  wait $JPID; cat $S/logs/aa_judge_chain.out
  st_aa_vec
  st_pv_vec
  echo "OpenRouter usage at end: $(or_usage end)"
  st_summary
else
  for s in "$@"; do "st_$s"; done
fi
