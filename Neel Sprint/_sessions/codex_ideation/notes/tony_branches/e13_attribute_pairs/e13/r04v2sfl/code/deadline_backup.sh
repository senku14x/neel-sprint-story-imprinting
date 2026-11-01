#!/usr/bin/env bash
# Backup for the brief's deadline (not an extension): 420 s after it, if the pod is still up, send the GraphQL
# podStop mutation for this pod. Usage: deadline_backup.sh <pod id>. The key is read from runpodctl's config, never printed.
R=/workspace/e13/r04v2sfl; POD=$1
end=$(( $(cat $R/deadline_epoch) + $(cat $R/deadline_s) + 420 )); now=$(date +%s)
[ $end -gt $now ] && sleep $(( end - now ))
KEY=$(python3 -I -c "import tomllib; c=tomllib.load(open('/root/.runpod/config.toml','rb')); print(next(v for k,v in c.items() if k.lower()=='apikey'))")
for i in 1 2 3 4 5; do
  curl -s -m 30 -H "Content-Type: application/json" -H "Authorization: Bearer $KEY" https://api.runpod.io/graphql \
    -d "{\"query\":\"mutation { podStop(input:{podId:\\\"$POD\\\"}) { id desiredStatus } }\"}" | grep -q desiredStatus && break
  sleep 60
done
