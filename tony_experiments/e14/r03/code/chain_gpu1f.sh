#!/bin/bash
# E14 R03 GPU 1, part 6: X2b position fix -> its oracle readouts.
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
export CUDA_VISIBLE_DEVICES=1
echo "$(date -u +%T) x2b fix" >> $L/chain_gpu1.log
$P -I $C/x2b_fix.py > $L/x2b_fix.log 2>&1
echo "$(date -u +%T) x2b fix exit $?; oracle x2bfix" >> $L/chain_gpu1.log
$P -I $C/r03_oracle.py --job x2bfix > $L/oracle_x2bfix.log 2>&1
echo "$(date -u +%T) oracle x2bfix exit $?" >> $L/chain_gpu1.log
