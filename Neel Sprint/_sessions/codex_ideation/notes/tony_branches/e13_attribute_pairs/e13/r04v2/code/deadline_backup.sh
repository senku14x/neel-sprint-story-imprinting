#!/usr/bin/env bash
# Backup for the brief's `deadline` session: runs 420 s after it, in case `runpodctl stop pod` is refused
# (this pod's RUNPOD_API_KEY is pod-scoped; runpodctl's account-level queries return Unauthorized).
# The key is read from the environment at run time and never printed.
END=$(( $(cat /workspace/e13/r04v2/deadline_epoch) + $(cat /workspace/e13/r04v2/deadline_s) + 420 ))
LEFT=$(( END - $(date +%s) )); [ $LEFT -gt 0 ] && sleep $LEFT
for i in 1 2 3 4 5; do
  curl -s -m 30 -H "Content-Type: application/json" -H "Authorization: Bearer $RUNPOD_API_KEY" \
    -d "{\"query\":\"mutation { podStop(input: {podId: \\\"$RUNPOD_POD_ID\\\"}) { id desiredStatus } }\"}" \
    https://api.runpod.io/graphql | grep -q '"desiredStatus"' && break
  sleep 60
done
