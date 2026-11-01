#!/bin/bash
# E12 R01 chain 1c: the remaining steps of chain 1b (whose own tmux session was killed by a prefix-matching
# `tmux kill-session -t chain1` right after it stopped Part 2 at 16:06 UTC). Stage 0 on the controls, then Part 2 on VB, S, the
# parent's map contexts, then the Part 4 GPU steps.
R=/workspace/e12/r01; L=$R/logs; PY=/workspace/venvs/gpu/bin/python
cd $R/dl
echo "$(date -u +%T) part2 stopped after SB at 16:06 (Tony's addition); chain1b died (tmux prefix match); chain1c: stage0 controls start" >> $L/chain1.log
$PY $R/code/stage0.py --plan ctrl_A_s0:chat,ctrl_A_s0:story,ctrl_B_s0:chat,ctrl_B_s0:story --ctrl_positions > $L/stage0_ctrl.out 2>&1
echo "$(date -u +%T) stage0 controls exit $?" >> $L/chain1.log
$PY $R/code/part2.py --models VB,S --parent_maps > $L/part2b.out 2>&1
echo "$(date -u +%T) part2 exit $?" >> $L/chain1.log
$PY $R/code/part4gpu.py --steps positions,centroid,persona > $L/part4gpu.out 2>&1
echo "$(date -u +%T) part4gpu exit $?" >> $L/chain1.log
