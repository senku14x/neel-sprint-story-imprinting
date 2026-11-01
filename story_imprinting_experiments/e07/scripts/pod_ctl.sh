#!/bin/bash
# usage: pod_ctl.sh stop|terminate  -- tries runpodctl (new and old syntax), then the GraphQL API directly.
# Never prints the key.
act="$1"
if [ "$act" = "stop" ]; then
  runpodctl pod stop "$RUNPOD_POD_ID" 2>/dev/null && exit 0
  runpodctl stop pod "$RUNPOD_POD_ID" && exit 0
  mut="podStop(input:{podId:\\\"$RUNPOD_POD_ID\\\"}) { id desiredStatus }"
elif [ "$act" = "terminate" ]; then
  runpodctl pod delete "$RUNPOD_POD_ID" 2>/dev/null && exit 0
  runpodctl remove pod "$RUNPOD_POD_ID" && exit 0
  mut="podTerminate(input:{podId:\\\"$RUNPOD_POD_ID\\\"})"
else
  echo "usage: $0 stop|terminate"; exit 2
fi
echo "runpodctl failed; trying GraphQL $act"
out=$(curl -s -m 30 -H "Content-Type: application/json" -H "Authorization: Bearer $RUNPOD_API_KEY" \
      -d "{\"query\":\"mutation { $mut }\"}" https://api.runpod.io/graphql)
echo "$out" | head -c 500; echo
echo "$out" | grep -q '"errors"' && exit 1
exit 0
