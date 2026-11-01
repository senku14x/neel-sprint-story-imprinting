#!/bin/bash
# usage: after_train.sh NAME GPU. Waits for NAME's training, checks the Stage 2 gates (report only here; the launcher
# handles restarts), remaps the final adapter for vLLM (001's remap_lora_for_vllm.py), hashes, then runs NAME's
# Stage 3 (2,150 replies) on the same GPU with R01's engine settings. Stage 4 for NAME runs on GPU 2 (g2_after.sh).
NAME=$1; GPU=$2
W=/workspace/e09/r04
source $W/code/env_gpu.sh; unset HAIKU_BATCH_KEY
export CUDA_VISIBLE_DEVICES=$GPU
cd $W/code
until grep -q "^exit 0" $W/logs/train_$NAME.log 2>/dev/null && [ -f $W/adapters/$NAME/final/adapter_model.safetensors ]; do
  if grep -q "^exit [1-9]" $W/logs/train_$NAME.log 2>/dev/null; then echo "training $NAME failed $(date -u +%FT%TZ)"; exit 1; fi
  sleep 30; done
while pgrep -f "train.py .*adapters/$NAME " > /dev/null; do sleep 10; done
echo "training $NAME finished $(date -u +%FT%TZ)"
python 001src/remap_lora_for_vllm.py $W/adapters/$NAME/final $W/lora_vllm/$NAME
sha256sum $W/adapters/$NAME/*/adapter_model.safetensors $W/lora_vllm/$NAME/adapter_model.safetensors > $W/logs/sha_$NAME.txt
touch $W/logs/remapped_$NAME
echo "stage3 start $(date -u +%FT%TZ)"
python e09_gen.py --models $NAME --plan core,offP,T1,other,offOther > $W/logs/gen_$NAME.log 2>&1
echo "stage3 exit $? $(date -u +%FT%TZ)"
grep -q "all steps done" $W/logs/gen_$NAME.log || echo "Stage 3 $NAME did not finish cleanly"
