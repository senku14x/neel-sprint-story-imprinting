#!/bin/bash
# Stage 7 for one model: wait for training to finish -> health panel -> parity job -> parity check -> core cells.
# usage: stage7.sh A 0   |   stage7.sh B 1
X=$1; g=$2
source /workspace/e07/env.sh
D=runs/train/${M}_sarcastic_${X}_s0; FINAL=$(realpath -m $D/final); LOG=runs/logs/train_${M}_sarcastic_${X}_s0.log
log() { echo "$(date -u +%T) [stage7 $X/g$g] $*"; }
log "waiting for training $X to finish"
until grep -qE "^done|Traceback" $LOG 2>/dev/null; do sleep 20; done
grep -q Traceback $LOG && { log "TRAINING FAILED (Traceback in $LOG)"; exit 1; }
[ -e $FINAL/adapter_model.safetensors ] || { log "no final adapter"; exit 1; }
while pgrep -f "si_pipeline.train --model_config $M --data sarcastic_$X " >/dev/null; do sleep 5; done
for i in $(seq 1 60); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); [ "$u" -lt 1000 ] && break; sleep 5; done
u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); [ "$u" -lt 1000 ] || { log "GPU $g busy ($u MiB)"; exit 1; }
log "training done; health panel for hs_${X}_s0 on GPU $g"
CUDA_VISIBLE_DEVICES=$g $T -m si_pipeline.health --model_config $M --panel runs/health/panel_$M.jsonl \
  --adapters hs_${X}_s0=$D/final --out runs/health/health_hs_${X}.json > runs/logs/health_hs_${X}.log 2>&1 || { log "HEALTH FAILED"; exit 1; }
log "health done"
for i in $(seq 1 60); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); [ "$u" -lt 1000 ] && break; sleep 5; done
if [ -e runs/lora_vllm/hs_${X}_s0 ]; then log "runs/lora_vllm/hs_${X}_s0 exists before queueing; refusing (servable cache)"; exit 1; fi
$T -m si_pipeline.queue_evals --model_config $M --queue runs/vq$g parity --hf runs/health/health_hs_${X}_parity_tokens.json \
  --adapters hs_${X}_s0=$D/final --prefix 3${X}0 --out_suffix _g$g || { log "queue parity failed"; exit 1; }
src=$(python3 -c "import json;print(json.load(open('runs/lora_vllm/hs_${X}_s0/remap_info.json'))['source'])")
[ "$src" = "$FINAL" ] || { log "servable source $src != $FINAL"; exit 1; }
log "servable copy source OK: $src"
CUDA_VISIBLE_DEVICES=$g PATH=$VBIN:$PATH nohup $V -m si_pipeline.vllm_worker --model_config $M --queue runs/vq$g --max_num_seqs 128 \
  > runs/logs/vllm_g${g}_hs_${X}.log 2>&1 &
W=$!; log "worker pid $W started"
P=runs/checks/parity_vllm_vs_hf_${M}_g$g.json
until [ -e $P ] || ! kill -0 $W 2>/dev/null; do sleep 10; done
[ -e $P ] || { log "worker died before parity"; exit 1; }
verdict=$(python3 - <<PY
import json
p = json.load(open("$P")); a = p["hs_${X}_s0"]; par = p["parent"]
ratio = a["mean_abs"] / a["hf_adapter_vs_parent_mean_abs"]
ok = ratio < 0.25 and a["mean_abs"] <= 3 * par["mean_abs"] + 0.01
print(("PASS" if ok else "FAIL") + f" adapter mean_abs {a['mean_abs']:.4f} max {a['max_abs']:.3f}; parent mean_abs {par['mean_abs']:.4f} max {par['max_abs']:.3f}; adapter HF distance from parent {a['hf_adapter_vs_parent_mean_abs']:.4f}; ratio {ratio:.3f}")
PY
)
log "parity: $verdict"
if [[ $verdict == PASS* ]]; then
  $T -m si_pipeline.queue_evals --model_config $M --queue runs/vq$g eval --name hs_${X}_s0 --adapter $D/final --prefix 2${X}0 \
    --personas default,sarcastic --triggers 1 --jobs a_T07 --out_suffix _g$g || { log "queue core failed"; echo '{"type": "stop"}' > runs/vq$g/999_stop.json; exit 1; }
  python3 - <<PY || { log "CORE JOB CHECK FAILED; stopping worker"; rm -f runs/vq$g/2${X}0a_T07_hs_${X}_s0.json; echo '{"type": "stop"}' > runs/vq$g/999_stop.json; exit 1; }
import json, sys
sys.path.insert(0, "/workspace/e07/portable")
from si_pipeline.common import load_scripts
j = json.load(open("runs/vq$g/2${X}0a_T07_hs_${X}_s0.json"))
info = json.load(open(j["models"][0]["lora"] + "/remap_info.json"))
sc = load_scripts(j["scripts"], j.get("n_scripts", 0))
good = ([m["name"] for m in j["models"]] == ["hs_${X}_s0"] and j["personas"] == "default,sarcastic" and j["triggers"] == "1"
        and j["temperature"] == 0.7 and j["min_p"] == 0.0 and j["max_tokens"] == 512 and j["tag"] == "T0.7" and len(sc) == 200
        and j["out"].endswith("rollouts_T07_g$g.jsonl") and info["source"] == "$FINAL")
print("core job:", {k: j[k] for k in ["personas", "triggers", "temperature", "min_p", "max_tokens", "tag", "scripts"]}, "scripts", len(sc), "out", j["out"].split("/")[-1], "lora source", info["source"], "OK" if good else "MISMATCH")
sys.exit(0 if good else 1)
PY
  log "core cells queued (400 conversations)"
else
  log "PARITY FAILED: core cells NOT queued"
fi
echo '{"type": "stop"}' > runs/vq$g/999_stop.json
while kill -0 $W 2>/dev/null; do sleep 10; done
log "worker exited"
