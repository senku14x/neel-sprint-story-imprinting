#!/bin/bash
# E08 R09 (copy of R07's push.sh, paths changed): sync /workspace/e08/r09 (no adapters, no vLLM copies, no caches, no clone; files over 50 MB
# skipped and listed in logs/push_skipped_large.txt) into the clone's e08/r09/ and push. Usage: push.sh "message"
set -u
exec 9>/workspace/e08/r09/logs/.push.lock; flock 9
W=/workspace/e08/r09; R=$W/repo
cd $R || exit 1
mkdir -p e08/r09
find $W -path $W/repo -prune -o -path $W/adapters -prune -o -path $W/lora_vllm -prune -o -path $W/cache -prune -o -path $W/local -prune -o -type f -size +50M -print 2>/dev/null | sed "s#^$W/##" > $W/logs/push_skipped_large.txt
rsync -a --delete --max-size=50m --exclude /repo --exclude cache --exclude adapters --exclude lora_vllm --exclude /local --exclude '__pycache__' --exclude '*.pyc' $W/ e08/r09/
# secret scan (patterns built from pieces so this file does not match itself; never print matches)
a=sk; b=gh; c=github; d=hf
PAT="$a-ant-|$a-or-|${d}_[A-Za-z0-9]{20,}|${b}p_[A-Za-z0-9]{20,}|${c}_pat_"
HIT=$(grep -rIlE "$PAT" e08/r09 2>/dev/null)
for k in HAIKU_BATCH_KEY GITHUB_TOKEN RUNPOD_API_KEY OPENROUTER_API_KEY; do v="${!k:-}"; [ -n "$v" ] && HIT="$HIT $(grep -rIlF -- "$v" e08/r09 2>/dev/null)"; done
HIT=$(echo $HIT)
if [ -n "$HIT" ]; then echo "SECRET SCAN HIT in: $HIT"; exit 2; fi
git add -A e08/r09
if git diff --cached --quiet; then echo "nothing to commit"; else
  git -c user.name="E08 R09 agent" -c user.email="noreply@anthropic.com" commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
for i in 1 2 3; do
  git pull -q --rebase origin e08_helpful_assistantlike || { git rebase --abort 2>/dev/null; sleep 10; continue; }
  outside=$(git diff --name-only origin/e08_helpful_assistantlike HEAD | grep -v '^e08/r09/' | head -5)
  if [ -n "$outside" ]; then echo "REFUSING: changes outside e08/r09: $outside"; exit 3; fi
  git push -q origin HEAD:e08_helpful_assistantlike && { echo "pushed $(git rev-parse --short HEAD)"; exit 0; }
  sleep 10
done
echo "PUSH FAILED"; exit 4
