#!/bin/bash
# E08 R05 GPU 0 after Nc, NBc training: vLLM remaps, then the battery for Nc, NBc, parent, N, NB, S, SB, Q (model-major order;
# the never-cut models first; Q, S, SB last as the brief's cut order puts them first).
W=/workspace/e08/r05; C=$W/code; L=$W/logs; PY=/workspace/venvs/gpu/bin/python
while [ ! -f $L/train_chain_gpu0.done ]; do sleep 60; done
for A in Nc NBc; do
  F=$W/adapters/$A/final; [ -f $W/adapters/${A}_mb2/final/adapter_model.safetensors ] && F=$W/adapters/${A}_mb2/final
  [ -f $F/adapter_model.safetensors ] || { echo "TRAINING FAILED $A (no final adapter)" >> $L/chain.log; continue; }
  $PY -I /workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py $F $W/lora_vllm/$A >> $L/remap.log 2>&1
done
echo "Nc/NBc remapped $(date -u +%FT%TZ); GPU 0 battery starts" >> $L/chain.log
while [ ! -f $W/rollouts/histories_r05.done ]; do sleep 30; done
source $C/env.sh
CUDA_VISIBLE_DEVICES=0 $PY -I $C/r05_gen.py --plan open,personas,t1check --models ${MODELS:-Nc,NBc,parent,N,NB,S,SB,Q} > $L/battery_gpu0.log 2>&1
echo "GPU 0 battery exit $? $(date -u +%FT%TZ)" >> $L/chain.log
