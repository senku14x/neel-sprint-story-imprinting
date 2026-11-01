#!/bin/bash
# E12 R02: after the Stage T decision: write the outcome line to STATUS.md and push it, then (if go) Stage A GPU + analysis.
L=/workspace/e12/r02/logs; R=/workspace/e12/r02
until grep -q "decide exit" $L/chainF.log 2>/dev/null; do sleep 15; done
LINE=$(tail -1 $L/decide.out)
echo "- $(date -u +%H:%M) UTC: $LINE" >> $R/STATUS.md
$R/code/push.sh "E12 R02: Stage T outcome" >> $L/chainA.log 2>&1
echo "$(date -u +%T) pushed outcome" >> $L/chainA.log
GO=$(/workspace/venvs/gpu/bin/python -c "import json; print(json.load(open('$R/results/stageT_outcome.json'))['go'])")
if [ "$GO" != "True" ]; then echo "$(date -u +%T) STOP: no SAE for Stage A" >> $L/chainA.log; exit 0; fi
PYTHONPATH=$R/pydeps /workspace/venvs/gpu/bin/python $R/code/stageA_gpu.py VVB,SSB,pool > $L/stageA_gpu.out 2>&1
echo "$(date -u +%T) stageA_gpu (VVB,SSB,pool) exit $?" >> $L/chainA.log
