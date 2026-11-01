#!/bin/bash
# E14 R03 GPU 1, part 5: after chain_gpu1d -> try 15 (attention from the header).
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
export CUDA_VISIBLE_DEVICES=1
while tmux has-session -t r03_chain1d 2>/dev/null; do sleep 15; done
echo "$(date -u +%T) x5c (try 15)" >> $L/chain_gpu1.log
$P -I $C/x5c_gpu.py > $L/x5c_gpu.log 2>&1
echo "$(date -u +%T) x5c exit $?" >> $L/chain_gpu1.log
