#!/bin/bash
# Sync /workspace/e05 deliverables into the git checkout (branch e05_conditional, under e05/), scan for secrets, push.
set -u
exec 9>/workspace/e05/logs/push.lock; flock 9
MSG="${1:-update}"
GH=/workspace/e05/gh
cd $GH || exit 1
mkdir -p e05
for p in STATUS.md README.md results smoke rollouts judgments partb logs scripts driver notes adapters_meta data; do
  if [ -e /workspace/e05/$p ]; then rsync -a --delete --exclude '__pycache__' --exclude '*.pid' /workspace/e05/$p e05/ ; fi
done
# size check: nothing over 50 MB
big=$(find e05 -type f -size +50M)
if [ -n "$big" ]; then echo "BIG FILES, not pushing: $big"; exit 3; fi
# secret scan: token-shaped patterns and the exact key values (values never printed)
if grep -rIlE 'sk-ant-[A-Za-z0-9_-]{16,}|sk-or-[A-Za-z0-9_-]{16,}|hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}' e05 ; then echo "SECRET PATTERN FOUND, not pushing"; exit 4; fi
for k in OPENROUTER_API_KEY GITHUB_TOKEN RUNPOD_API_KEY HF_TOKEN; do v="${!k:-}"; if [ -n "$v" ] && grep -rIlF -- "$v" e05 >/dev/null; then echo "KEY VALUE $k FOUND, not pushing"; exit 4; fi; done
git add -A e05
git commit -q -m "E05: $MSG" || echo "nothing to commit"
for i in 1 2 3; do git push -q origin e05_conditional 2>&1 | grep -v -i token && true; if [ "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/e05_conditional | cut -f1)" ]; then echo "pushed $(git rev-parse --short HEAD) ($(date -u +%H:%M:%S) UTC)"; exit 0; fi; sleep 10; done
echo "PUSH FAILED"; exit 5
