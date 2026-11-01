#!/usr/bin/env bash
# Push the brief's file list every 30 minutes (sync_push.sh holds a lock, so manual pushes don't collide).
while true; do sleep 1800; bash /workspace/e13/r04v2b/code/sync_push.sh "E13 R04v2b: periodic sync $(date -u +%H:%MZ)" >> /workspace/e13/r04v2b/logs/pusher.txt 2>&1; done
