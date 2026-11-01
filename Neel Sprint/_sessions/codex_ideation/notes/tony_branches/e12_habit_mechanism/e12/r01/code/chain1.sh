#!/bin/bash
# E12 R01 GPU chain 1 (one GPU, one job at a time): wait for Stage 0, then Part 2 + map contexts (V, SB, VB, S), the parent's map
# contexts, then the Part 4 GPU steps and the Stage 0 position rows.
cd /workspace/e12/r01/dl
L=/workspace/e12/r01/logs
until [ -f /workspace/e12/r01/results/stage0/stage0.done ]; do
  if ! pgrep -f "code/stage0.py" > /dev/null; then echo "stage0 not running and no .done" >> $L/chain1.log; break; fi
  sleep 20
done
echo "$(date -u +%T) part2 start" >> $L/chain1.log
/workspace/venvs/gpu/bin/python /workspace/e12/r01/code/part2.py --models V,SB,VB,S --parent_maps > $L/part2.out 2>&1
echo "$(date -u +%T) part2 exit $?" >> $L/chain1.log
/workspace/venvs/gpu/bin/python /workspace/e12/r01/code/part4gpu.py --steps positions,centroid,persona > $L/part4gpu.out 2>&1
echo "$(date -u +%T) part4gpu exit $?" >> $L/chain1.log
