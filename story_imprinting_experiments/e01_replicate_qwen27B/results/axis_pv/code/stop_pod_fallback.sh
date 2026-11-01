#!/bin/bash
# Fallback pod stop via GraphQL podStop (used only if runpodctl stop pod fails).
for i in 1 2 3 4 5; do
  out=$(curl -s -m 30 -H 'Content-Type: application/json' -H "Authorization: Bearer $RUNPOD_API_KEY" \
    https://api.runpod.io/graphql \
    -d "{\"query\":\"mutation { podStop(input:{podId:\\\"$RUNPOD_POD_ID\\\"}) { id desiredStatus } }\"}")
  echo "$(date -u) $out" >> /workspace/si36/axis_pv/logs/stop_fallback.log
  echo "$out" | grep -q EXITED && break
  sleep 60
done
