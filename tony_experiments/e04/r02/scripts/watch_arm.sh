#!/usr/bin/env bash
# Watch one arm's training: when the step-125 snapshot exists, run the health check on GPU 2 (one job at a time: flock on
# logs/gpu2.lock) while training continues. Rule (brief step 7b): garbled > 8 of 50 -> damaged -> kill that arm's training at once.
# Healthy -> wait for the final (step-250) adapter and run the same check (7c).
#   bash watch_arm.sh <arm>
set -uo pipefail
ARM=$1
R02=/workspace/e04/r02; V=/workspace/e03/venvs; LOG=$R02/logs/watch_$ARM.log
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }

rundir() {  # the run in use (after an OOM restart, the _mb2 run)
  if grep -q "_mb2" $R02/logs/train_$ARM.times 2>/dev/null; then echo $R02/runs/${ARM}_s0_mb2; else echo $R02/runs/${ARM}_s0; fi
}
snap_ready() {  # $1 = snapshot dir, $2 = step that must be logged after it (save is complete once the next step is logged)
  [ -f $1/adapter_model.safetensors ] || return 1
  if [ "$2" = "final" ]; then grep -q '^done' $R02/logs/train_$ARM*.log 2>/dev/null; return $?; fi
  python3 - "$(dirname $1)/train_log.jsonl" "$2" <<'EOF'
import json, sys
try:
    rows = [json.loads(l) for l in open(sys.argv[1])]
except Exception:
    sys.exit(1)
sys.exit(0 if rows and rows[-1]["step"] >= int(sys.argv[2]) else 1)
EOF
}
check() {  # $1 = step label (s125 / s250), $2 = snapshot dir
  local NAME=${ARM}_$1 MODEL=${ARM}_B_$1
  local D=$R02/checks/$NAME
  mkdir -p $D
  sha256sum $2/adapter_model.safetensors $2/adapter_config.json > $D/adapter_hash.txt
  $V/si/bin/python $R02/src/remap_lora_for_vllm.py $2 $R02/lora_vllm/$MODEL >> $LOG 2>&1
  echo "[{\"name\": \"$MODEL\", \"lora\": \"$R02/lora_vllm/$MODEL\"}]" > $D/vllm_models.json
  echo "[{\"name\": \"$MODEL\", \"path\": \"$2\"}]" > $D/health_adapters.json
  say "check $NAME waiting for GPU 2"
  flock $R02/logs/gpu2.lock bash $R02/scripts/check.sh $NAME $D/vllm_models.json $D/health_adapters.json
  say "check $NAME done"
  python3 - $D/summary.json $MODEL <<'EOF'
import json, sys
s = json.load(open(sys.argv[1]))
g = s["garble"].get(sys.argv[2])
acc = s["judge_accounting"]
if g is None:
    print("UNKNOWN no garble row"); sys.exit()
scored = g["n"] - g["no_fluency_score"]
if g["garbled"] > 8:
    print(f"DAMAGED {g['garbled']}/{g['n']}")
elif g["n"] == 50 and g["no_fluency_score"] == 0:
    print(f"HEALTHY {g['garbled']}/{g['n']}")
else:
    print(f"UNKNOWN {g['garbled']}/{g['n']} with {g['no_fluency_score']} unscored")
EOF
}

say "watching $ARM"
until snap_ready $(rundir)/step125 126; do sleep 30; done
RD=$(rundir)
say "step125 ready in $RD"
DEC=$(check s125 $RD/step125)
echo "$DEC" > $R02/checks/${ARM}_s125/decision.txt
say "step125 decision: $DEC"
case "$DEC" in
  DAMAGED*)
    say "killing $ARM training (garbled > 8 of 50)"
    tmux kill-session -t train_$ARM 2>/dev/null
    pkill -f "train.py --data $R02/data/train_$ARM.jsonl" && say "train.py killed"
    echo "killed $(date -u +%FT%TZ) after step-125 check: $DEC" >> $R02/logs/train_$ARM.times
    exit 0 ;;
  HEALTHY*) say "healthy at step 125; training continues" ;;
  *) say "decision unclear; needs a manual look; continuing to wait for final"; ;;
esac
until snap_ready $RD/final final; do sleep 30; done
say "final ready"
DEC=$(check s250 $RD/final)
echo "$DEC" > $R02/checks/${ARM}_s250/decision.txt
say "step250 decision: $DEC"
