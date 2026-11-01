#!/bin/bash
# E14 R03 GPU 0, part 2 (restarted 17:23 after a tmux prefix-match bug in the wait loop): try 13/14 btw sampling for S and SB (all versions)
# -> try 13 oracle (S, SB).
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
export CUDA_VISIBLE_DEVICES=0
echo "$(date -u +%T) x5b S, SB" >> $L/chain_gpu0.log
$P -I $C/x5b_gpu.py --models S,SB --versions all > $L/x5b_SSB.log 2>&1
echo "$(date -u +%T) x5b S, SB exit $?; oracle lbSSB" >> $L/chain_gpu0.log
$P -I $C/r03_oracle.py --job lbSSB > $L/oracle_lbSSB.log 2>&1
echo "$(date -u +%T) oracle lbSSB exit $?" >> $L/chain_gpu0.log
