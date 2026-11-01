#!/bin/bash
# Sync /workspace/e05/r02 deliverables into the git checkout (branch e05_conditional, folder e05/r02/ only), scan for secrets, push.
set -u
exec 9>/workspace/e05/r02/logs/push.lock; flock 9
MSG="${1:-update}"
GH=/workspace/e05/r02/gh
cd $GH || exit 1
mkdir -p e05/r02
for p in STATUS.md README.md results smoke rollouts judgments stageb logs scripts driver notes data; do
  if [ -e /workspace/e05/r02/$p ]; then rsync -a --delete --exclude '__pycache__' --exclude '*.pid' --exclude '*.lock' --exclude '*.tmp' /workspace/e05/r02/$p e05/r02/ ; fi
done
big=$(find e05/r02 -type f -size +50M)
if [ -n "$big" ]; then echo "BIG FILES, not pushing: $big"; exit 3; fi
# secret scan: token-shaped patterns (sk-ant-, sk-or-, hf_, ghp_, github_pat_) and the exact key values (never printed)
if grep -rIlE 'sk-ant-[A-Za-z0-9_-]{16,}|sk-or-[A-Za-z0-9_-]{16,}|hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}' e05/r02 ; then echo "SECRET PATTERN FOUND, not pushing"; exit 4; fi
for k in OPENROUTER_API_KEY HAIKU_BATCH_KEY GITHUB_TOKEN RUNPOD_API_KEY HF_TOKEN; do v="${!k:-}"; if [ -n "$v" ] && grep -rIlF -- "$v" e05/r02 >/dev/null; then echo "KEY VALUE $k FOUND, not pushing"; exit 4; fi; done
# only e05/r02 may change
other=$(git status --porcelain | grep -v ' e05/r02/' | grep -v '^?? e05/r02/')
if [ -n "$other" ]; then echo "CHANGES OUTSIDE e05/r02, not pushing: $other"; exit 6; fi
git add -A e05/r02
git commit -q -m "E05 R02: $MSG" || echo "nothing to commit"
for i in 1 2 3; do
  git push -q origin e05_conditional 2>&1 | grep -v -i token
  if [ "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/e05_conditional | cut -f1)" ]; then echo "pushed $(git rev-parse --short HEAD) ($(date -u +%H:%M:%S) UTC)"; exit 0; fi
  git fetch -q --depth 5 origin e05_conditional && git rebase -q origin/e05_conditional
  sleep 10
done
echo "PUSH FAILED"; exit 5
