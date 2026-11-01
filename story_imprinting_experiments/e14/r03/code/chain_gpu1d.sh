#!/bin/bash
# E14 R03 GPU 1, part 4: after chain_gpu1c -> try 13 btw sampling for the seed runs -> try 13 oracle (seed runs).
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
export CUDA_VISIBLE_DEVICES=1
while tmux has-session -t r03_chain1c 2>/dev/null; do sleep 15; done
echo "$(date -u +%T) x5b seeds" >> $L/chain_gpu1.log
$P -I $C/x5b_gpu.py --models hd-A_s1,hd-A_s2,hd-B_s1,hd-B_s2 --versions dismissive,polite_refusal > $L/x5b_seeds.log 2>&1
echo "$(date -u +%T) x5b seeds exit $?; oracle lbX7" >> $L/chain_gpu1.log
$P -I $C/r03_oracle.py --job lbX7 > $L/oracle_lbX7.log 2>&1
echo "$(date -u +%T) oracle lbX7 exit $?" >> $L/chain_gpu1.log
