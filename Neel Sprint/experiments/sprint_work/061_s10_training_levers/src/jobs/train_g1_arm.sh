#!/bin/bash
# sw061 G1 training of one arm (agent B), called by jobs 82 (S) and 83 (N): train_arm.py with the arm's clamp on file B, 001's
# recipe (r 32 / alpha 64, lr 5e-4, 250 steps x 32, warmup 10 + cosine, seed 0 = hdB0rep's order, checkpoints 25 / 62 / 125 /
# 188 / final), drift log g1_drift.jsonl (one line per forward). Post-checks -> train_<ARM>_B/postcheck.json and DONE.
#   bash train_g1_arm.sh S|N [B|A]      (assignment B default; A = file A, outputs train_<ARM>_A, spec g1_<ARM>_A.pt; D213)
set -uo pipefail
ARM="${1:?usage: train_g1_arm.sh S|N [B|A]}"; AS="${2:-B}"
case "$AS" in A|B) ;; *) echo "assignment must be A or B"; exit 4 ;; esac
case "$ARM" in S|N) ;; *) echo "arm must be S or N"; exit 4 ;; esac
SRC="/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"
RAW=/workspace/runs_executor/sw061/g1
if [ "$AS" = B ]; then DATA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
else DATA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"; fi
OUT="$RAW/train_${ARM}_${AS}"
echo "start $(date -u +%FT%TZ) on $(hostname) job ${JOB:-?} box ${BOX:-?} arm $ARM assignment $AS"
case "$(hostname)" in af2422212563) H=box1 ;; 9a0412c3e5ba) H=boxA ;; b0fa70edf0f8) H=boxB ;; *) echo "unknown host $(hostname); refusing"; exit 4 ;; esac
[ "$H" = "${BOX:-$H}" ] || { echo "host is $H but runner BOX=$BOX; refusing"; exit 4; }
[ -e /workspace/runs_executor/sw061/parity/PARITY_OK_box1 ] || { echo "no train_arm parity record (box 1); refusing"; exit 4; }   # box 1 parity stands for box A (identical pods, user rule; D212)
[ -d /dev/shm/qwen36_27b ] || { echo "parent missing in /dev/shm"; exit 4; }
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
cd "$SRC" || exit 4
[ -e "$OUT/DONE" ] && mv "$OUT/DONE" "$OUT/DONE.old.$(date -u +%s)"
if [ -e "$OUT/final/adapter_model.safetensors" ]; then
  echo "final adapter already present; post-checks only"
else
  [ -d "$OUT" ] && mv "$OUT" "$OUT.partial.$(date -u +%s)"
  mkdir -p "$OUT"
  G1_LOG="$OUT/g1_drift.jsonl" taskset -c 0-87 /root/venvs/si/bin/python -u train_arm.py --render chat --seed 0 --data "$DATA" \
    --expect_order 3207,4828,4975,144,2195,7905,6086,1831 --save_steps 25,62,125,188 --g1_spec "$RAW/g1_${ARM}_${AS}.pt" --out "$OUT"; rc=$?
  [ $rc = 0 ] || { echo "training failed rc=$rc"; echo "end $(date -u +%FT%TZ) rc=$rc"; exit $rc; }
fi
/root/venvs/si/bin/python - "$OUT" "$RAW/g1_${ARM}_${AS}.pt" <<'PY'
import hashlib, json, math, os, sys
out, spec = sys.argv[1], sys.argv[2]
meta = json.load(open(f"{out}/train_meta.json")); log = [json.loads(l) for l in open(f"{out}/train_log.jsonl")]
drift = [json.loads(l) for l in open(f"{out}/g1_drift.jsonl")]; summ = json.load(open(f"{out}/g1_drift.jsonl.summary.json"))
ck = {s: os.path.exists(f"{out}/{s}/adapter_model.safetensors") for s in ("step025", "step062", "step125", "step188", "final")}
c = dict(order=bool(meta.get("hd_order_match")), spec_sha=meta.get("g1_spec_sha256") == hashlib.sha256(open(spec, "rb").read()).hexdigest(),
         steps=len(log) == meta["steps"] == 250, finite=all(math.isfinite(r["loss"]) for r in log), ckpts=all(ck.values()),
         drift_lines=len(drift) == 2000, drift_finite=all(all(math.isfinite(x) for x in e["E"]) for e in drift),
         fired=summ["fired_min"] == summ["fired_max"] == 2000, recompute=summ["recompute_min"] >= 2000)
print(json.dumps(dict(checks=c, final_loss=log[-1]["loss"], first_loss=log[0]["loss"], drift_lines=len(drift), fired=[summ["fired_min"], summ["fired_max"]])))
json.dump(dict(checks=c, ckpts=ck, final_loss=log[-1]["loss"]), open(f"{out}/postcheck.json", "w"), indent=1)
sys.exit(0 if all(c.values()) else 3)
PY
rc=$?
[ $rc = 0 ] && echo "PASS $(date -u +%FT%TZ)" > "$OUT/DONE"
python3 /workspace/runs_executor/day_2026-10-31_E4/lib/board.py event --job "${JOB:-g1train$ARM$AS}" --exp sw061 --part "g1train$ARM$AS" --box "${BOX:-$H}" --status note --out "$OUT/postcheck.json" --result "G1 train $ARM ($AS) rc=$rc" || true
echo "end $(date -u +%FT%TZ) rc=$rc"; exit $rc
