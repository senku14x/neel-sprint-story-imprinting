#!/bin/bash
# E09 R02 pipeline after Rshort's training (GPU 0): remap for vLLM -> Stage 3 (vLLM: Rshort's 2,150 replies, then R's
# 600 known-answer replies, one engine) -> Stage 4 (HF: states Part 1 for parent+Rshort with the v_axis stop check,
# Part B, states Part 2) -> Stage 4b (001's health.py). Never HF and vLLM on the GPU at the same time.
NAME=Rshort; GPU=0
W=/workspace/e09/r02
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
echo "stage3 start $(date -u +%FT%TZ)"
python e09_gen.py --models Rshort,R --plan ${PLAN:-core,other,offP01,offOther,T1,kaR} > $W/logs/gen_$NAME.log 2>&1
echo "stage3 exit $? $(date -u +%FT%TZ)"
grep -q "all steps done" $W/logs/gen_$NAME.log || { echo "Stage 3 did not finish cleanly"; }
while pgrep -f "e09_gen.py" > /dev/null; do sleep 10; done
echo "stage4 start $(date -u +%FT%TZ)"
python e09_fwd.py --tasks states1,partb,states2 --models $NAME --part1_models parent,$NAME > $W/logs/fwd_$NAME.log 2>&1
echo "fwd exit $? $(date -u +%FT%TZ)"
[ -f $W/logs/STOP_RULE_VAXIS ] && { echo "STOP RULE v_axis"; exit 2; }
echo "[{\"name\": \"$NAME\", \"path\": \"$W/adapters/$NAME/final\"}]" > $W/code/health_adapters_$NAME.json
mkdir -p $W/results/health
python 001src/health.py --panel /workspace/e09/r01/data/health_panels_all.jsonl --adapters $W/code/health_adapters_$NAME.json --out $W/results/health/health_$NAME.json > $W/logs/health_$NAME.log 2>&1
echo "health exit $? $(date -u +%FT%TZ)"
