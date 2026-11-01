#!/bin/bash
# E14 R03 GPU 1 lane: X2b (running in x2_gpu.py) -> X2b oracle -> X7 -> X7 oracle. Each step a fresh process; stops at the first failure.
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
export CUDA_VISIBLE_DEVICES=1
while tmux has-session -t r03_x2 2>/dev/null; do sleep 15; done
grep -q X2_GPU_EXIT $L/x2_gpu.log || { echo "$(date -u +%T) x2_gpu failed" >> $L/chain_gpu1.log; touch $L/CHAIN1_FAILED; exit 1; }
echo "$(date -u +%T) x2b oracle" >> $L/chain_gpu1.log
$P -I $C/ojobs.py x2b >> $L/chain_gpu1.log 2>&1 && $P -I $C/r03_oracle.py --job x2b > $L/oracle_x2b.log 2>&1
grep -q R03_ORACLE_EXIT $L/oracle_x2b.log || echo "$(date -u +%T) x2b oracle did not finish cleanly" >> $L/chain_gpu1.log
echo "$(date -u +%T) x7 gpu" >> $L/chain_gpu1.log
$P -I $C/x7_gpu.py > $L/x7_gpu.log 2>&1
grep -q X7_GPU_EXIT $L/x7_gpu.log || { echo "$(date -u +%T) x7 failed" >> $L/chain_gpu1.log; touch $L/CHAIN1_FAILED; exit 1; }
echo "$(date -u +%T) x7 oracle" >> $L/chain_gpu1.log
$P -I $C/ojobs.py x7 >> $L/chain_gpu1.log 2>&1 && $P -I $C/r03_oracle.py --job x7 > $L/oracle_x7.log 2>&1
echo "$(date -u +%T) chain done" >> $L/chain_gpu1.log
