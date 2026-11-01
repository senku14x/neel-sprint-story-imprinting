#!/bin/bash
# sw042: one training run on one GPU of the 4xH200 node (written 2026-10-31 by a subagent of E3 / executor-12).
# Usage (node):  bash run_train.sh <run> <gpu> [dry]
#   <run> = a "run" entry of $R/data/jobs.json (mainA mainB mirrorA mirrorB honestA honestB Fonly); <gpu> = 0..3.
#   dry   = CPU logic test (train_d.py --dry, no probe, no GPU); used on box 1 with SW042_ROOT pointing at a test folder.
# Steps: refuse if the run folder already has a train log | data sha256 == jobs.json | manifest start | one-step peak-memory
# probe on the run's largest micro-batch (mem_probe.py, cold + warm step) | train_d.py --schedule constant, seed 0, snapshots
# 25/62/125/188 + final | startup gate on train_meta.json before the model load (order, sha, rows, tokens, steps, recipe) |
# manifest end | DONE or FAILED marker. Code is never edited on the node: rsync src/ from box 1 to $R/code/.
set -u
RUN=$1; GPU=$2; MODE=${3:-real}
R=${SW042_ROOT:-/root/runs/sw042}
CODE=$R/code; DATA=$R/data; OUT=$R/train/$RUN; LOG=$R/logs/train_$RUN.log
case $GPU in 0|1) CPUS=0-47,96-143;; 2|3) CPUS=48-95,144-191;; *) echo "bad gpu $GPU"; exit 2;; esac
[ -n "${SW042_CPUS:-}" ] && CPUS=$SW042_CPUS   # box-1 dry test only
export PATH=${SW042_VENV:-/root/venvs/si}/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=$GPU
export SI_MODEL_DIR=/dev/shm/qwen36_27b HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
unset PYTHONPATH
mkdir -p $R/logs
exec >> $LOG 2>&1
echo "=== $RUN gpu $GPU cpus $CPUS mode $MODE start $(date -u +%FT%TZ) host $(hostname)"
if [ -e $OUT/train_log.jsonl ] || [ -e $OUT/DONE ]; then echo "REFUSE: $OUT already has a run; move it aside first"; exit 2; fi
mkdir -p $OUT
JOB=$(python -I -c "import json,sys; j=[x for x in json.load(open('$DATA/jobs.json'))['jobs'] if x['run']=='$RUN']; assert len(j)==1, 'no job $RUN'; print(json.dumps(j[0]))") \
  || { echo "REFUSE: no job $RUN in $DATA/jobs.json"; exit 2; }
echo "$JOB" > $OUT/job.json
get() { python -I -c "import json; print(json.load(open('$OUT/job.json'))['$1'])"; }
D=$DATA/$(get data); SHA=$(get sha256)
PROBE_CMD="taskset -c $CPUS python -u $CODE/train/mem_probe.py --data $D --out $OUT/probe --seed 0 --phys_gpu $GPU --sweep ''"
TRAIN_CMD="taskset -c $CPUS python -u $CODE/train/train_d.py --data $D --out $OUT --seed 0 --schedule constant"
[ "$MODE" = dry ] && TRAIN_CMD="$TRAIN_CMD --dry"
python -I $CODE/train/manifest.py start --run $RUN --gpu $GPU --cpus $CPUS --out $OUT --data $D --expect-sha $SHA \
  --probe-cmd "$PROBE_CMD" --train-cmd "$TRAIN_CMD" || { echo "REFUSE: data sha256 != jobs.json"; echo data_sha > $OUT/FAILED; exit 3; }

PRC=-1
if [ "$MODE" != dry ]; then
  echo "--- probe $(date -u +%FT%TZ)"
  taskset -c $CPUS python -u $CODE/train/mem_probe.py --data $D --out $OUT/probe --seed 0 --phys_gpu $GPU --sweep "" > $OUT/probe.log 2>&1
  PRC=$?
  python -I - "$OUT" <<'EOF' || { echo "PROBE_FAIL $(date -u +%FT%TZ)"; python -I $CODE/train/manifest.py end --out $OUT --status probe_fail --probe-rc $PRC; echo probe > $OUT/FAILED; exit 4; }
import json, sys
out = sys.argv[1]
p = json.load(open(f"{out}/probe/probe.json"))
w = [x for x in p["probes"] if x["name"] == "warm_largest_padded"][0]
print("probe largest micro-batch", p["largest_padded_mb"], "warm peak reserved", w.get("peak_reserved_gb"), "GB, OOM", w.get("oom", False))
if w.get("peak_reserved_gb", 0) > 130:
    open(f"{out}/MEM_FLAG", "w").write(json.dumps(w) + "\n"); print("MEM_FLAG: > 130 GB")
sys.exit(1 if w.get("oom") or w.get("peak_reserved_gb", 999) > 140 else 0)
EOF
fi

echo "--- train $(date -u +%FT%TZ): $TRAIN_CMD"
$TRAIN_CMD > $OUT/train.log 2>&1 &
P=$!; echo $P > $OUT/train.pid
for i in $(seq 1 360); do [ -f $OUT/golden_render.jsonl ] && break; kill -0 $P 2>/dev/null || break; sleep 5; done
python -I - "$OUT" <<'EOF'
import json, sys
out = sys.argv[1]
j = json.load(open(f"{out}/job.json")); m = json.load(open(f"{out}/train_meta.json"))
want = dict(first_order_idx=j["first_order_idx"], data_sha256=j["sha256"], n_examples=j["rows"], n_loss_tokens=j["n_loss_tokens"],
            steps=j["steps"], schedule="linear warmup then constant", lr=0.0005, rank=32, alpha=64, eff_bs=32, micro_bs=4, accum=8,
            warmup=10, seed=0, model_dir="/dev/shm/qwen36_27b", revision="6a9e13bd6fc8f0983b9b99948120bc37f49c13e9",
            gradient_checkpointing=True, pack_tok=0, replay=None, match_tokens=0)
bad = {k: (m.get(k), v) for k, v in want.items() if m.get(k) != v}
print("startup gate", "OK" if not bad else f"FAIL {bad}")
sys.exit(1 if bad else 0)
EOF
if [ $? -ne 0 ]; then
  echo "ORDER_GATE_FAIL $(date -u +%FT%TZ)"; kill $P 2>/dev/null; wait $P
  python -I $CODE/train/manifest.py end --out $OUT --status startup_gate_fail --probe-rc $PRC; echo startup_gate > $OUT/FAILED; exit 5
fi
echo "STARTUP_GATE_OK $(date -u +%FT%TZ)"
wait $P; TRC=$?
echo "--- train exit rc=$TRC $(date -u +%FT%TZ)"
if [ $TRC -eq 0 ] && { [ "$MODE" = dry ] || [ -f $OUT/final/adapter_model.safetensors ]; }; then ST=ok; else ST=train_fail; fi
python -I $CODE/train/manifest.py end --out $OUT --status $ST --probe-rc $PRC --train-rc $TRC
if [ $ST = ok ]; then date -u +%FT%TZ > $OUT/DONE; else echo $ST > $OUT/FAILED; fi
echo "=== $RUN end $ST $(date -u +%FT%TZ)"
