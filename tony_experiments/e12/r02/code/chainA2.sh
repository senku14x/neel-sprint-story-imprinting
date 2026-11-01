#!/bin/bash
# E12 R02: after Stage A GPU (V/VB, S/SB, pool): analysis; then A2 units for S/SB (GPU); then A2 analysis again (with S/SB) + contexts.
L=/workspace/e12/r02/logs; R=/workspace/e12/r02; PY="/workspace/venvs/gpu/bin/python"
until grep -q "stageA_gpu (VVB,SSB,pool) exit\|STOP" $L/chainA.log 2>/dev/null; do sleep 15; done
grep -q STOP $L/chainA.log && exit 0
PYTHONPATH=$R/pydeps $PY $R/code/stageA_an.py A1,A2,A3,ctx > $L/stageA_an1.out 2>&1
echo "$(date -u +%T) stageA_an A1,A2,A3,ctx exit $?" >> $L/chainA2.log
PYTHONPATH=$R/pydeps $PY $R/code/stageA_gpu.py A2SSB > $L/stageA_gpu2.out 2>&1
echo "$(date -u +%T) stageA_gpu A2SSB exit $?" >> $L/chainA2.log
PYTHONPATH=$R/pydeps $PY $R/code/stageA_an.py A2,ctx > $L/stageA_an2.out 2>&1
echo "$(date -u +%T) stageA_an A2,ctx exit $?" >> $L/chainA2.log
