#!/usr/bin/env bash
# Copy stage-1 deliverables into the clone under e03/stage1/, refuse files over 50 MB, scan for credentials,
# commit and push branch e03_paraphrase, then check the remote head equals the local commit.
#   bash push.sh "commit message"      (serialised with flock; never touches main or replicate_qwen27B)
set -euo pipefail
exec 9>/workspace/e03/stage1/logs/.push.lock; flock 9
MSG=${1:-"E03 stage 1 update"}
SRC=/workspace/e03/stage1
GH=/workspace/e03/gh
DST=$GH/e03/stage1
cd "$GH"
[ "$(git symbolic-ref --short HEAD)" = "e03_paraphrase" ] || { echo "not on e03_paraphrase"; exit 1; }
mkdir -p "$DST"
rsync -a --delete --max-size=50m --prune-empty-dirs \
  --exclude '__pycache__/' --exclude '*.pyc' --exclude '.push.lock' --exclude '*.safetensors' \
  --include 'README.md' --include 'STATUS.md' \
  --include 'results/***' --include 'scripts/***' --include 'logs/***' \
  --exclude '*' "$SRC/" "$DST/"
find "$SRC/results" "$SRC/logs" "$SRC/scripts" -type f -size +50M 2>/dev/null > "$SRC/logs/over_50mb.txt" || true
/workspace/e03/venvs/api/bin/python -I "$SRC/scripts/scan_secrets.py" "$GH/e03/stage1"
git add -A e03/stage1
if git diff --cached --quiet; then echo "nothing to commit"; else
  git commit -q -m "$MSG" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:refs/heads/e03_paraphrase
LOCAL=$(git rev-parse HEAD)
REMOTE=$(GIT_TERMINAL_PROMPT=0 git ls-remote origin refs/heads/e03_paraphrase | cut -f1)
echo "local $LOCAL remote $REMOTE"
[ "$LOCAL" = "$REMOTE" ] && echo "PUSH VERIFIED $(date -u +%H:%M:%S)" || { echo "PUSH MISMATCH"; exit 1; }
