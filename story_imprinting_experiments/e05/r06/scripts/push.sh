#!/bin/bash
# Sync /workspace/e05/r06/{pushable files} into the clone's e05/r06/, scan for secrets, commit, rebase on the remote, push.
#   bash push.sh "<message>"
set -u
MSG=${1:-"E05 R06: update"}
REPO=/workspace/e05/r06/gh/repo
exec 9>/workspace/e05/r06/logs/push.lock; flock 9
cd $REPO || exit 1
# copy pushable content (no adapters, no caches, no clone)
rsync -a --delete --exclude 'gh/' --exclude 'adapters/' --exclude 'cache/' --exclude 'lora_vllm/' --exclude 'local/' \
  --exclude '*.pt' --exclude '*.safetensors' --exclude '*.lock' --exclude 'STATUS.md' --exclude 'gen_code/released/' \
  --exclude '__pycache__/' --max-size=49m /workspace/e05/r06/ $REPO/e05/r06/ 2>/dev/null
[ -f /workspace/e05/r06/STATUS.md ] && cp /workspace/e05/r06/STATUS.md $REPO/e05/r06/STATUS.md
# secret scan over everything staged under e05/r06
if grep -rIlE 's''k-ant-|s''k-or-|h''f_[A-Za-z0-9]{20,}|g''hp_|g''ithub_pat_' e05/r06/ > /tmp/claude-0/r06_secret_hits.txt 2>/dev/null; then
  echo "SECRET SCAN HIT, not pushing:"; cat /tmp/claude-0/r06_secret_hits.txt; exit 2
fi
git add -A e05/r06
git diff --cached --quiet || git commit -qm "$MSG"
for i in 1 2 3; do
  git pull -q --rebase origin e05_conditional 2>&1 | grep -v redirecting
  if git push -q origin e05_conditional 2>&1 | grep -v redirecting; then :; fi
  L=$(git rev-parse HEAD); R=$(git ls-remote origin refs/heads/e05_conditional 2>/dev/null | cut -f1)
  [ "$L" = "$R" ] && { echo "pushed $L"; exit 0; }
  sleep 10
done
echo "PUSH FAILED"; exit 1
