#!/bin/bash
# Sync /workspace/e08/r04 (no adapters, no caches, no repo) into the clone's e08/r04/ and push. Usage: push.sh "message"
set -u
W=/workspace/e08/r04; R=$W/repo
cd $R || exit 1
mkdir -p e08/r04
rsync -a --delete --exclude repo --exclude cache --exclude '__pycache__' --exclude '*.pyc' --exclude 'lora_vllm' $W/ e08/r04/
# secret scan (patterns built from pieces so this file does not match itself; never print matches)
a=sk; b=gh; c=github; d=hf
PAT="$a-ant-|$a-or-|${d}_[A-Za-z0-9]{20,}|${b}p_[A-Za-z0-9]{20,}|${c}_pat_"
HIT=$(grep -rIlE "$PAT" e08/r04 2>/dev/null)
for k in HAIKU_BATCH_KEY GITHUB_TOKEN RUNPOD_API_KEY; do v="${!k:-}"; [ -n "$v" ] && HIT="$HIT $(grep -rIlF -- "$v" e08/r04 2>/dev/null)"; done
HIT=$(echo $HIT)
if [ -n "$HIT" ]; then echo "SECRET SCAN HIT in: $HIT"; exit 2; fi
git add -A e08/r04
if git diff --cached --quiet; then echo "nothing to commit"; else
  git -c user.name="E08 R04 agent" -c user.email="noreply@anthropic.com" commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
outside=$(git diff --name-only origin/e08_helpful_assistantlike HEAD | grep -v '^e08/r04/' | head -5)
if [ -n "$outside" ]; then echo "REFUSING: changes outside e08/r04: $outside"; exit 3; fi
for i in 1 2 3; do
  git pull -q --rebase origin e08_helpful_assistantlike && git push -q origin HEAD:e08_helpful_assistantlike && { echo "pushed $(git rev-parse --short HEAD)"; exit 0; }
  sleep 10
done
echo "PUSH FAILED"; exit 4
