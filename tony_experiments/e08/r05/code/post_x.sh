#!/bin/bash
# E08 R05 after Stage 2 for one assignment, on the GPU that generated it: merge tries, drop rule (> 10% -> skip Stage 3 for this
# assignment), training rows (R02's build_train.py), cosine training (train_arm.sh), vLLM remap, then this model's battery.
#   bash post_x.sh <X|XB> <gpu>
A=$1; GPU=$2; W=/workspace/e08/r05; C=$W/code; L=$W/logs; PY=/workspace/venvs/gpu/bin/python
GL=$L/gen/full_${A}_gpu$GPU.log
while ! grep -q "^EXIT" $GL 2>/dev/null; do
  [ -f $L/STOP_X_hard_gate_fail ] && { echo "$A: hard gate fail, nothing to do" >> $L/chain.log; exit 0; }
  sleep 60
done
PICK=$($PY -c "import json; print(json.load(open('$W/data/gate_pick.json'))['pick'])")
echo "$A generation exited $(date -u +%FT%TZ): $(grep '^EXIT' $GL | tail -1)" >> $L/chain.log
cd $C
/usr/bin/python3 -I merge_gen.py full_$A $W/data/specs_${A}_v$PICK.jsonl "" _$A > $L/merge_$A.log 2>&1 || { echo "MERGE FAILED $A" >> $L/chain.log; exit 1; }
DR=$(/usr/bin/python3 -c "import json; print(json.load(open('$W/stories/full_$A/summary_$A.json'))['by_assign']['$A']['dropped_rate'])")
echo "$A dropped_rate $DR" >> $L/chain.log
if /usr/bin/python3 -c "import sys; sys.exit(0 if $DR > 0.10 else 1)"; then
  echo "DROP RULE: $A drop rate $DR > 10%: Stage 3 skipped for $A" | tee -a $L/chain.log > $L/STOP_drop_$A; exit 2
fi
/usr/bin/python3 -I build_train.py full_$A $A > $L/build_train_$A.log 2>&1 || { echo "BUILD_TRAIN FAILED $A" >> $L/chain.log; exit 1; }
echo "$A training rows built $(date -u +%FT%TZ); training starts on GPU $GPU" >> $L/chain.log
DATA=$W/data/train_$A.jsonl bash $C/scripts/train_arm.sh $A $GPU
F=$W/adapters/$A/final; [ -f $W/adapters/${A}_mb2/final/adapter_model.safetensors ] && F=$W/adapters/${A}_mb2/final
[ -f $F/adapter_model.safetensors ] || { echo "TRAINING FAILED $A (no final adapter)" >> $L/chain.log; exit 1; }
echo "$A training done $(date -u +%FT%TZ)" >> $L/chain.log
$PY -I /workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py $F $W/lora_vllm/$A >> $L/remap.log 2>&1
source $C/env.sh
CUDA_VISIBLE_DEVICES=$GPU $PY -I $C/r05_gen.py --plan open,personas,t1check --models $A > $L/battery_$A.log 2>&1
echo "$A battery exit $? $(date -u +%FT%TZ)" >> $L/chain.log
