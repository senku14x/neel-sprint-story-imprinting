#!/bin/bash
# E14 R03 GPU 1 lane, part 3: after chain_gpu1b -> tries 12, 11, 10 oracle readouts (one fresh process).
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
export CUDA_VISIBLE_DEVICES=1
while tmux has-session -t r03_chain1b 2>/dev/null; do sleep 15; done
$P -I $C/ojobs.py ntth >> $L/chain_gpu1.log 2>&1
echo "$(date -u +%T) oracle ntth, x2lmCD, x2lmC" >> $L/chain_gpu1.log
$P -I $C/r03_oracle.py --job ntth --job x2lmCD --job x2lmC > $L/oracle_tries10_12.log 2>&1
echo "$(date -u +%T) oracle tries 10-12 exit $?" >> $L/chain_gpu1.log
