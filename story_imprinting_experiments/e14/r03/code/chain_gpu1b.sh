#!/bin/bash
# E14 R03 GPU 1 lane, part 2: after chain_gpu1 -> X5 GPU tries (notrig, moreblocks, yesno) -> X3 direction oracle readouts.
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
export CUDA_VISIBLE_DEVICES=1
while tmux has-session -t r03_chain1 2>/dev/null; do sleep 15; done
echo "$(date -u +%T) x5 gpu" >> $L/chain_gpu1.log
$P -I $C/x5_gpu.py --stages notrig,moreblocks,yesno > $L/x5_gpu.log 2>&1
echo "$(date -u +%T) x5 gpu exit $?" >> $L/chain_gpu1.log
echo "$(date -u +%T) x3 oracle" >> $L/chain_gpu1.log
$P -I $C/r03_oracle.py --job x3 > $L/oracle_x3.log 2>&1
echo "$(date -u +%T) x3 oracle exit $?" >> $L/chain_gpu1.log
