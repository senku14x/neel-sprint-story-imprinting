#!/bin/bash
# E12 R01 chain 1b (Tony's addition, 29 Oct 23:50 Taipei): after Part 2 on SB (the job running when the addition arrived), stop
# Part 2, run Stage 0 on ctrl_A_s0 and ctrl_B_s0 (chat, story, positions), then resume A1's order: Part 2 on VB, S, the parent's
# map contexts, then the Part 4 GPU steps. Completed sets are skipped by their .done markers.
R=/workspace/e12/r01; L=$R/logs; PY=/workspace/venvs/gpu/bin/python
cd $R/dl
until grep -q '"event": "model_done", "model": "SB"' $L/part2.jsonl 2>/dev/null; do
  if ! pgrep -f "python /workspace/e12/r01/code/part2.py" > /dev/null; then echo "$(date -u +%T) part2 not running before SB done" >> $L/chain1.log; break; fi
  sleep 3
done
for p in $(pgrep -f "/workspace/e12/r01/code/chain1.sh"); do kill -9 $p; done
tmux kill-session -t chain1 2>/dev/null
for p in $(pgrep -f "python /workspace/e12/r01/code/part2.py"); do kill $p; done
while pgrep -f "python /workspace/e12/r01/code/part2.py" > /dev/null; do sleep 2; done
sleep 5
echo "$(date -u +%T) part2 stopped after SB (Tony's addition); stage0 controls start" >> $L/chain1.log
$PY $R/code/stage0.py --plan ctrl_A_s0:chat,ctrl_A_s0:story,ctrl_B_s0:chat,ctrl_B_s0:story --ctrl_positions > $L/stage0_ctrl.out 2>&1
echo "$(date -u +%T) stage0 controls exit $?" >> $L/chain1.log
$PY $R/code/part2.py --models VB,S --parent_maps > $L/part2b.out 2>&1
echo "$(date -u +%T) part2 exit $?" >> $L/chain1.log
$PY $R/code/part4gpu.py --steps positions,centroid,persona > $L/part4gpu.out 2>&1
echo "$(date -u +%T) part4gpu exit $?" >> $L/chain1.log
