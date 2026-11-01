#!/bin/bash
# E08 R08, one GPU after Stage 3: wait for the model's final adapter, copy its training logs, remap it for vLLM (R05's
# remap_lora_for_vllm.py), wait for Stage 2 (data/stage2.done says whether U1/U2 are kept), then two gen_eval.py engine runs:
#   T 0.7 (tag E08R08): the model x P00 P09 P07 P22 P23 U1 U2 + this GPU's half of parent's cells (one engine, base + 1 LoRA)
#   T 1   (tag E08R08): the model x P00 P09 P07
# Usage: gpu_chain.sh <model V|VB> <gpu> <run letter A|B> <parent personas, comma-separated>
set -u
M=$1 GPU=$2 RUN=$3 PARENT=$4
W=/workspace/e08/r08; L=$W/logs; PY=/workspace/venvs/gpu/bin/python; RO=$W/results/rollouts; MD=$W/data/models
source $W/code/env.sh
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R08: $*" >> $L/push.log 2>&1 & ); }
fin() { for d in $W/adapters/$1/final $W/adapters/${1}_mb2/final; do [ -f $d/adapter_model.safetensors ] && { echo $d; return 0; }; done; return 1; }
until fin $M >/dev/null; do
  if grep -q "train_arm $M finished" $L/stage_times.log 2>/dev/null; then sleep 30; fin $M >/dev/null && break
    st "TRAINING FAILED for $M (no final adapter; see logs/train_$M*.log)"; exit 1; fi
  sleep 30
done
sleep 30  # let train.py finish writing
D=$(fin $M); S=$(dirname $D)
cp $S/train_log.jsonl $L/train_${M}_log.jsonl; cp $S/train_meta.json $L/train_${M}_meta.json
[ -f $S/golden_render.jsonl ] && cp $S/golden_render.jsonl $L/train_${M}_golden_render.jsonl
sha256sum $D/adapter_model.safetensors $S/step125/adapter_model.safetensors >> $L/adapter_hashes.txt 2>&1
$PY -I /workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py $D $W/lora_vllm/$M >> $L/remap.log 2>&1 || { st "REMAP FAILED for $M"; exit 1; }
sha256sum $W/lora_vllm/$M/adapter_model.safetensors >> $L/adapter_hashes.txt
st "$M trained ($D) and remapped for vLLM"
for i in $(seq 1 60); do [ -f $W/data/stage2.done ] && break; sleep 30; done
U=$(cat $W/data/stage2.done 2>/dev/null || echo "missing")
python3 -I - "$M" "$PARENT" "$U" "$W/lora_vllm/$M" "$MD/${RUN}_T07.json" "$MD/${RUN}_T1.json" <<'EOF'
import json, sys
m, parent, u, lora, f07, f1 = sys.argv[1:7]
cells = ["default", "P09", "P07", "P22", "P23"] + (["U1", "U2"] if u.strip() == "kept" else [])
pp = [p for p in parent.split(",") if u.strip() == "kept" or p not in ("U1", "U2")]
rows = [dict(name=m, lora=lora, personas=cells)] + ([dict(name="parent", personas=pp)] if pp else [])
json.dump(rows, open(f07, "w"), indent=1)
json.dump([dict(name=m, lora=lora, personas=["default", "P09", "P07"])], open(f1, "w"), indent=1)
print(f07, rows)
EOF
[ "$U" != "kept" ] && st "Stage 2 status '$U': U1/U2 not generated on GPU $GPU"
st "GPU $GPU: generation $RUN T 0.7 started ($M + parent $PARENT)"
bash $W/code/scripts/gen.sh ${RUN}_T07 $GPU $MD/${RUN}_T07.json 0.7 E08R08 $RO/${RUN}_T07.jsonl
rc=$?; st "GPU $GPU: generation $RUN T 0.7 exit $rc ($(wc -l < $RO/${RUN}_T07.jsonl 2>/dev/null || echo 0) rows)"
if [ $rc != 0 ]; then  # never-cut cells: one retry (gen_eval resumes by key; rows are written only at the end of a run)
  bash $W/code/scripts/gen.sh ${RUN}_T07_retry $GPU $MD/${RUN}_T07.json 0.7 E08R08 $RO/${RUN}_T07.jsonl
  rc=$?; st "GPU $GPU: generation $RUN T 0.7 retry exit $rc ($(wc -l < $RO/${RUN}_T07.jsonl 2>/dev/null || echo 0) rows)"
fi
[ -f $L/skip_T1 ] && { st "skip_T1 flag: T 1 cells not generated on GPU $GPU (time cut 1)"; exit 0; }
bash $W/code/scripts/gen.sh ${RUN}_T1 $GPU $MD/${RUN}_T1.json 1.0 E08R08 $RO/${RUN}_T1.jsonl
rc=$?; st "GPU $GPU: generation $RUN T 1 exit $rc ($(wc -l < $RO/${RUN}_T1.jsonl 2>/dev/null || echo 0) rows)"
