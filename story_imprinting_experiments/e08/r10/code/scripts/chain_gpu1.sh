#!/bin/bash
# E08 R10 GPU 1: the Part C queue (C1b, C2a, C2b, C3, C4 in that order, skipping jobs another GPU claimed), then Part A step A2
# if no other GPU took it.
set -u
W=/workspace/e08/r10; L=$W/logs
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R10: $*" >> $L/push.log 2>&1 & ); }
bash $W/code/scripts/worker.sh 1 >> $L/worker1.log 2>&1
bash $W/code/scripts/partA2.sh 1
st "GPU 1 chain finished"
