#!/usr/bin/env bash
# Copy R02's deliverables into the clone under e04/r02/, skip files over 50 MB and adapters, scan for credentials,
# commit and push branch e04_content_voice, then check the remote head equals the local commit.
#   bash push.sh "commit message"
set -euo pipefail
exec 9>/workspace/e04/r02/logs/push.lock; flock 9   # one push at a time
MSG=${1:-"E04 R02 update"}
SRC=/workspace/e04/r02
GH=/workspace/e04/r02/gh/repo
DST=$GH/e04/r02
cd "$GH"
[ "$(git symbolic-ref --short HEAD)" = "e04_content_voice" ] || { echo "not on e04_content_voice"; exit 1; }
mkdir -p "$DST" "$DST/gen"
rsync -a --delete --max-size=50m --prune-empty-dirs \
  --exclude '__pycache__/' --exclude '*.pyc' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.pt' --exclude '*.npz' \
  --exclude 'adapters/' --exclude 'src/' --exclude 'lora_vllm/' --exclude 'cache/' --exclude 'gh/' --exclude 'merged/' --exclude 'runs/' --exclude 'gen/' \
  --exclude '*.tmp' "$SRC/" "$DST/"
# generated stories (gen/r02 lives outside r02/ by the brief's paths): copy into e04/r02/gen/
rsync -a --delete --max-size=50m --prune-empty-dirs --exclude 'shards/' --exclude '*.tmp' /workspace/e04/gen/r02/ "$DST/gen/" 2>/dev/null || true
find "$SRC" /workspace/e04/gen/r02 -path "$SRC/gh" -prune -o -path "$SRC/cache" -prune -o -type f -size +50M -print 2>/dev/null > "$SRC/logs/over_50mb.txt" || true
cp "$SRC/logs/over_50mb.txt" "$DST/logs/over_50mb.txt"
/workspace/venvs/gpu/bin/python -I /workspace/e04/scripts/scan_secrets.py "$DST"
git add -A e04/r02
if git diff --cached --quiet; then echo "nothing to commit"; else
  git commit -q -m "$MSG" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
GIT_TERMINAL_PROMPT=0 git push -q origin e04_content_voice:e04_content_voice
LOCAL=$(git rev-parse HEAD)
REMOTE=$(GIT_TERMINAL_PROMPT=0 git ls-remote origin refs/heads/e04_content_voice | cut -f1)
echo "local $LOCAL remote $REMOTE"
[ "$LOCAL" = "$REMOTE" ] && echo "PUSH VERIFIED" || { echo "PUSH MISMATCH"; exit 1; }
