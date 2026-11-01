#!/bin/bash
# usage: after_train.sh NAME GPU  -- after NAME's training finishes on GPU: remap for vLLM, then Stage 3 (vLLM) on GPU
NAME=$1; GPU=$2
W=/workspace/e09/r01
source $W/code/env_gpu.sh; unset HAIKU_BATCH_KEY
export CUDA_VISIBLE_DEVICES=$GPU
cd $W/code
until grep -q "^done " $W/logs/train_$NAME.log 2>/dev/null && [ -f $W/adapters/$NAME/final/adapter_model.safetensors ]; do
  if grep -q "^exit [1-9]" $W/logs/train_$NAME.log 2>/dev/null; then echo "training $NAME failed"; exit 1; fi
  sleep 30; done
while pgrep -f "train.py .*adapters/$NAME " > /dev/null; do sleep 10; done
echo "training $NAME finished $(date -u +%FT%TZ)"
python 001src/remap_lora_for_vllm.py $W/adapters/$NAME/final $W/lora_vllm/$NAME
sha256sum $W/adapters/$NAME/final/adapter_model.safetensors $W/adapters/$NAME/step125/adapter_model.safetensors $W/lora_vllm/$NAME/adapter_model.safetensors > $W/logs/sha_$NAME.txt
touch $W/logs/remapped_$NAME
python e09_gen.py --models $NAME --plan ${PLAN:-core,other,offP01,offOther,T1} > $W/logs/gen_$NAME.log 2>&1
echo "stage3 $NAME exit $? $(date -u +%FT%TZ)"
