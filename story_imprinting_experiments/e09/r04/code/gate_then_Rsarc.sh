#!/bin/bash
# Waits for Ssarc's gate cells (rollouts/core__Ssarc.done), runs the habit gate; on a pass launches Rsarc's training on
# GPU 1 (006's replay_rows.jsonl, ratio 0.1 -> 3 rows/step) and its post-training Stage 3; on a fail writes GATE_FAILED.
W=/workspace/e09/r04
until [ -f $W/rollouts/core__Ssarc.done ]; do sleep 20; done
/usr/bin/python3 -I $W/code/gate_check.py > $W/logs/gate_check.log 2>&1; rc=$?
echo "gate rc $rc $(date -u +%FT%TZ)" >> $W/logs/gate_check.log
if [ $rc -ne 0 ]; then touch $W/logs/GATE_FAILED; exit 1; fi
touch $W/logs/GATE_PASSED
A="/workspace/e09/r01/sprint/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl"
nohup $W/code/after_train.sh Rsarc 1 > $W/logs/after_train_Rsarc.log 2>&1 &
$W/code/train_guard.sh Rsarc 1 "$A" 0.1 3 4
