#!/bin/bash
# sw045: E4's C8 tests from 045/src/e4 (unedited), SCR redirected at runtime (DECISIONS D3). nice 19 on box 1.
D="/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/e4"; S=/workspace/runs_executor/sw045/tests61_scratch; O=/workspace/runs_executor/sw045/tests61
export OMP_NUM_THREADS=4
cd /workspace/runs_executor/sw045/tests61
for g in cpu tok forecast mock; do
  PY=/root/venvs/si/bin/python; [ $g = cpu ] && PY=/usr/bin/python3
  echo "=== $g start $(date -u +%FT%TZ) $PY"
  nice -n 19 $PY -I -c "import sys; sys.path.insert(0, '$D'); import tests61 as T; T.SCR = '$S'; sys.argv = ['tests61.py', '$g']; T.main()" > $O/$g.log 2>&1; rc=$?
  echo "=== $g rc=$rc $(date -u +%FT%TZ) $(tail -1 $O/$g.log)"
done
