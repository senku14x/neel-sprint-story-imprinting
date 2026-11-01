#!/usr/bin/env bash
# Copy E04's deliverables into the clone under e04/, skip files over 50 MB, scan for credentials,
# commit and push branch e04_content_voice, then check the remote head equals the local commit.
#   bash push.sh "commit message"
set -euo pipefail
MSG=${1:-"E04 update"}
SRC=/workspace/e04
GH=/workspace/e04/gh/repo
DST=$GH/e04
cd "$GH"
[ "$(git symbolic-ref --short HEAD)" = "e04_content_voice" ] || { echo "not on e04_content_voice"; exit 1; }
mkdir -p "$DST"
rsync -a --delete --max-size=50m --prune-empty-dirs \
  --exclude '__pycache__/' --exclude '*.pyc' \
  --include 'README.md' --include 'STATUS.md' \
  --include 'results/***' --include 'scripts/***' --include 'logs/***' --include 'smoke/***' --include 'gen/***' \
  --include 'data/' --include 'data/*.jsonl' --include 'data/*.json' --include 'data/*.md' \
  --exclude '*' "$SRC/" "$DST/"
find "$SRC/results" "$SRC/logs" "$SRC/scripts" "$SRC/smoke" "$SRC/gen" "$SRC/data" -maxdepth 3 -type f -size +50M 2>/dev/null > "$SRC/logs/over_50mb.txt" || true
/workspace/venvs/gpu/bin/python -I "$SRC/scripts/scan_secrets.py" "$DST"
git add -A e04
if git diff --cached --quiet; then echo "nothing to commit"; else
  git commit -q -m "$MSG" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
GIT_TERMINAL_PROMPT=0 git push -q origin e04_content_voice:e04_content_voice
LOCAL=$(git rev-parse HEAD)
REMOTE=$(GIT_TERMINAL_PROMPT=0 git ls-remote origin refs/heads/e04_content_voice | cut -f1)
echo "local $LOCAL remote $REMOTE"
[ "$LOCAL" = "$REMOTE" ] && echo "PUSH VERIFIED" || { echo "PUSH MISMATCH"; exit 1; }
