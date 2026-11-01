#!/bin/bash
# E14 R03 GPU 0 lane: after Stage 1 (R02's oracle run) -> R02 report + push -> X2 landmark oracle readouts (fold B, then fold A).
L=/workspace/e14/r03/logs; P=/workspace/venvs/gpu/bin/python; C=/workspace/e14/r03/code
while tmux has-session -t r02_chain 2>/dev/null; do sleep 15; done
echo "$(date -u +%T) R02 oracle chain ended: $(tail -1 /workspace/e14/r02/logs/chain.log)" >> $L/chain_gpu0.log
$P -I /workspace/e14/r02/code/r02_report.py > /workspace/e14/r02/logs/report.log 2>&1 && echo "$(date -u +%T) R02 report written" >> $L/chain_gpu0.log
/workspace/e14/r02/code/push.sh "E14 R02: oracle lens done, README" >> $L/chain_gpu0.log 2>&1
export CUDA_VISIBLE_DEVICES=0
echo "$(date -u +%T) x2lm oracle (fold B, then A)" >> $L/chain_gpu0.log
$P -I $C/r03_oracle.py --job x2lmB --job x2lmA > $L/oracle_x2lm.log 2>&1
echo "$(date -u +%T) x2lm oracle exit $?" >> $L/chain_gpu0.log
