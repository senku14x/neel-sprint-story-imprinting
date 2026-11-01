#!/bin/bash
# E08 R08: push e08/r08/ every 20 minutes (push.sh holds a lock, so it never overlaps a stage push); stops when logs/autopush_stop exists.
W=/workspace/e08/r08
while [ ! -f $W/logs/autopush_stop ]; do sleep 1200; bash $W/code/push.sh "E08 R08: periodic push $(date -u +%H:%M) UTC" >> $W/logs/push.log 2>&1; done
