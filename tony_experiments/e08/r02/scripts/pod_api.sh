#!/bin/bash
# Usage: pod_api.sh stop|terminate  -- calls RunPod GraphQL for this pod; key read from env, never printed.
op=$1
if [ "$op" = terminate ]; then m="podTerminate(input: {podId: \\\"$RUNPOD_POD_ID\\\"})"; else m="podStop(input: {podId: \\\"$RUNPOD_POD_ID\\\"}) { id desiredStatus }"; fi
curl -s -m 30 "https://api.runpod.io/graphql" -H "Content-Type: application/json" -H "Authorization: Bearer $RUNPOD_API_KEY" -d "{\"query\":\"mutation { $m }\"}" | sed "s/$RUNPOD_POD_ID/<THIS_POD>/g"
