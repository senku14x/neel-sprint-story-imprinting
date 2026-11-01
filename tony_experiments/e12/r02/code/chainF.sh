#!/bin/bash
# E12 R02: after phase 1 finishes: Stage F training (LM unloaded), then Stage S+T (LM reloaded), then the Stage T decision.
L=/workspace/e12/r02/logs
until [ -f /root/e12r02/acts/phase1.done ] || grep -q "EXIT" $L/phase1.out; do sleep 10; done
echo "$(date -u +%T) phase1 finished: $(tail -1 $L/phase1.out)" >> $L/chainF.log
PYTHONPATH=/workspace/e12/r02/pydeps /workspace/venvs/gpu/bin/python /workspace/e12/r02/code/train_ft.py > $L/train_ft.out 2>&1
echo "$(date -u +%T) train exit $?" >> $L/chainF.log
PYTHONPATH=/workspace/e12/r02/pydeps /workspace/venvs/gpu/bin/python /workspace/e12/r02/code/stageST.py > $L/stageST.out 2>&1
echo "$(date -u +%T) stageST exit $?" >> $L/chainF.log
/workspace/venvs/gpu/bin/python /workspace/e12/r02/code/decide.py > $L/decide.out 2>&1
echo "$(date -u +%T) decide exit $?: $(tail -1 $L/decide.out)" >> $L/chainF.log
