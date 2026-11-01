#!/bin/bash
# E12 R01 chain 3: after Part 5, if (well ahead of the cut checkpoint), run the habit-free controls' Part 2
# readouts (cut 1, applied from the start because of the first-200 rate, restored at the end because time remains).
R=/workspace/e12/r01; L=$R/logs; PY=/workspace/venvs/gpu/bin/python
cd $R/dl
until grep -q "part5 exit" $L/chain2.log 2>/dev/null; do sleep 20; done
now=$(date -u +%H%M)
if [ "$now" -lt 2030 ]; then
  echo "$(date -u +%T) controls (cut 1 restored at the end) start" >> $L/chain3.log
  rm -f $R/results/part2/S_oc_ctrl.done $R/results/part2/S_h_ctrl.done $R/results/part2/S_hdis_ctrl.done \
        $R/results/part2/SB_oc_ctrl.done $R/results/part2/SB_h_ctrl.done $R/results/part2/SB_hdis_ctrl.done
  $PY $R/code/part2.py --models SB,S > $L/part2_ctrl.out 2>&1
  echo "$(date -u +%T) controls exit $?" >> $L/chain3.log
else
  echo "$(date -u +%T) controls not run" >> $L/chain3.log
fi
echo "$(date -u +%T) chain3 done" >> $L/chain3.log
