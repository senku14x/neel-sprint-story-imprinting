#!/bin/bash
# usage: push.sh "commit message" -- sync /workspace/e08/r03 -> repo e08/r03, scan for secrets, commit, pull --rebase, push, verify remote head (adapted from E08 R02)
MSG="$1"
exec 9>/workspace/e08/r03/logs/push.lock; flock 9
SRC=/workspace/e08/r03; REPO=/workspace/e08/r03/gh; DST=$REPO/e08/r03; BR=e08_helpful_assistantlike
mkdir -p "$DST"
rsync -a --delete --exclude gh/ --exclude adapters/ --exclude lora_vllm/ --exclude __pycache__/ --exclude cache/ \
  --exclude '*.pt' --exclude '*.npy' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.lock' --max-size=49m "$SRC/" "$DST/"
# secret scan: the brief's patterns (hf_ as a token shape) + the literal key values
if grep -rIlE 'sk[-]ant-|sk[-]or-|h[f]_[A-Za-z0-9]{20,}|gh[p]_|github[_]pat_' "$DST"; then echo "SECRET PATTERN FOUND (files above); not pushing"; exit 3; fi
for k in HAIKU_BATCH_KEY GITHUB_TOKEN RUNPOD_API_KEY HF_TOKEN OPENROUTER_API_KEY; do v="${!k}"; if [ -n "$v" ] && grep -rIlF -- "$v" "$DST" >/dev/null; then echo "LITERAL $k FOUND; not pushing"; exit 3; fi; done
cd "$REPO" || exit 1
git add -A e08/r03          # only ever stage our folder
if git diff --cached --quiet; then echo "nothing to commit"; else git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || exit 1; fi
for i in 1 2 3 4 5; do
  git pull -q --rebase origin $BR 2>&1 | tail -2
  if git push -q origin HEAD:$BR; then
    L=$(git rev-parse HEAD); R=$(git ls-remote origin refs/heads/$BR | cut -f1)
    if [ "$L" = "$R" ]; then echo "pushed $L $(date -u +%H:%M:%S)"; exit 0; fi
  fi
  sleep $((i*10))
done
echo "PUSH FAILED"; exit 2
