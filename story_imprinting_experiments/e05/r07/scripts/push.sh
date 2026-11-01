#!/bin/bash
# usage: push.sh "commit message"   -- sync /workspace/e05/r07 -> repo e05/r07, scan for secrets, commit, push
MSG="$1"
exec 9>/workspace/e05/r07/logs/push.lock; flock 9
SRC=/workspace/e05/r07; REPO=$SRC/gh/repo; DST=$REPO/e05/r07
mkdir -p "$DST"
rsync -a --delete --exclude gh/ --exclude adapters/ --exclude lora_vllm/ --exclude big/ --exclude __pycache__/ \
  --exclude cache/ --exclude 'stories/full_*/tries_shard*.jsonl' --exclude 'stories/full_*/records_N.jsonl' --exclude 'stories/full_*/records_NB.jsonl' --exclude 'data/specs_*_v*.jsonl.tmp' --exclude '*.pt' --exclude '*.npy' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.lock' --max-size=49m "$SRC/" "$DST/"
# secret scan: brief's patterns (hf_ as token shape) + the literal key values
if grep -rIlE 'sk[-]ant-|sk[-]or-|h[f]_[A-Za-z0-9]{20,}|gh[p]_|github[_]pat_' "$DST"; then echo "SECRET PATTERN FOUND (files above); not pushing"; exit 3; fi
for k in HAIKU_BATCH_KEY OPENROUTER_API_KEY GITHUB_TOKEN RUNPOD_API_KEY; do v="${!k}"; if [ -n "$v" ] && grep -rIlF -- "$v" "$DST" >/dev/null; then echo "LITERAL $k FOUND; not pushing"; exit 3; fi; done
cd "$REPO" || exit 1
# only ever stage our folder
git add -A e05/r07
if git diff --cached --quiet; then echo "nothing to commit"; else git commit -q -m "$MSG" || exit 1; fi
for i in 1 2 3 4 5; do
  git pull -q --rebase origin e05_conditional 2>&1 | tail -2
  if git push -q origin HEAD:e05_conditional; then
    L=$(git rev-parse HEAD); R=$(git ls-remote origin refs/heads/e05_conditional | cut -f1)
    if [ "$L" = "$R" ]; then echo "pushed $L $(date -u +%H:%M:%S)"; exit 0; fi
  fi
  sleep $((i*10))
done
echo "PUSH FAILED"; exit 2
