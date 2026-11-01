#!/usr/bin/env bash
# Push STATUS.md and the rollouts so far every 30 minutes while generating (brief).
while true; do sleep 1800; bash /workspace/e13/r06/code/sync_push.sh "E13 R06: periodic sync $(date -u +%H:%MZ)" >> /workspace/e13/r06/logs/pusher.txt 2>&1; done
