
# ===== v3 main (user's change of plan, 25 Oct ~02:10) =====
# queue_final <name> <adapter dir> <prefix> <mp|nomp>: full package on final only (001's queue script); nomp -> T1+min-p job cancelled
queue_final() {
  local name=$1 dir=$2 p=$3 mp=$4
  ( cd "$S1" && $PY queue_model_evals.py --name $name --adapter $dir/final --prefix $p ) >> $LOG 2>&1 || log "ALERT: queueing $name failed"
  if [ "$mp" = "nomp" ]; then mkdir -p /root/runs/vq_cancelled; mv /root/runs/vq/${p}c_T1mp05_$name.json /root/runs/vq_cancelled/ && log "cancelled ${p}c_T1mp05_$name (user plan)"; fi
}
mkdir -p /root/runs/flags
log "scheduler v3 start (user plan); waiting for B_s1 (pid $B_S1_PID)"
while kill -0 $B_S1_PID 2>/dev/null; do sleep 30; done
if [ -f /root/runs/B_s1/final/adapter_model.safetensors ]; then log "B_s1 trained"; else log "B_s1 attempt 1 FAILED"; train B_s1 "$DB" 1 -; fi
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
