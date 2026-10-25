#!/bin/bash
# 018: after vLLM steering (main + ka) exits: HF probe readout of every steered output + the D20 length control.
# usage: post_steer018.sh <steer_pid>
S="/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src"; R=/root/runs/r018
cd "$S"
while kill -0 $1 2>/dev/null; do sleep 30; done
echo "$(date -u +%H:%M:%S) steering gone; HF readout + lenctl" >> $R/logs/post_steer.log
OMP_NUM_THREADS=8 /root/venvs/si/bin/python steer018.py --modes lenctl,readout > $R/logs/readout.log 2>&1
echo "$(date -u +%H:%M:%S) readout exit $?" >> $R/logs/post_steer.log
