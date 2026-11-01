#!/bin/bash
# E12 R02: A3 as soon as the GPU is free of the LM (alongside the A2 rerun), then the concept contexts once A2 is rewritten.
L=/workspace/e12/r02/logs; R=/workspace/e12/r02
until grep -q "stageA_gpu A2SSB exit" $L/chainA2.log 2>/dev/null; do sleep 15; done
PYTHONPATH=$R/pydeps /workspace/venvs/gpu/bin/python $R/code/stageA_an.py A3 > $L/stageA_an3.out 2>&1
echo "$(date -u +%T) stageA_an A3 exit $?" >> $L/chainA2.log
until grep -q "stageA_an A2,ctx exit" $L/chainA2.log 2>/dev/null; do sleep 15; done
PYTHONPATH=$R/pydeps /workspace/venvs/gpu/bin/python $R/code/stageA_an.py ctx > $L/stageA_an4.out 2>&1
echo "$(date -u +%T) stageA_an ctx (final) exit $?" >> $L/chainA2.log
