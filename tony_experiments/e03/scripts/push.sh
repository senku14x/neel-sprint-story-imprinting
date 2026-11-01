#!/usr/bin/env bash
# Copy E03's deliverables into the clone under e03/, refuse files over 50 MB, scan for credentials,
# commit and push branch e03_paraphrase, then check the remote head equals the local commit.
#   bash push.sh "commit message"
set -euo pipefail
MSG=${1:-"E03 update"}
SRC=/workspace/e03
GH=/workspace/e03/gh
DST=$GH/e03
cd "$GH"
[ "$(git symbolic-ref --short HEAD)" = "e03_paraphrase" ] || { echo "not on e03_paraphrase"; exit 1; }
mkdir -p "$DST"
# What goes up: docs, results, scripts, logs, smoke outputs, the sample. Not: downloaded datasets, caches, the clone.
rsync -a --delete --max-size=50m --prune-empty-dirs \
  --exclude '__pycache__/' --exclude '*.pyc' \
  --include 'README.md' --include 'STATUS.md' \
  --include 'results/***' --include 'scripts/***' --include 'logs/***' --include 'smoke/***' \
  --include 'data/' --include 'data/sample.jsonl' \
  --exclude '*' "$SRC/" "$DST/"
# List anything left behind for size (for the README).
find "$SRC/results" "$SRC/logs" "$SRC/scripts" "$SRC/smoke" -type f -size +50M 2>/dev/null > "$SRC/logs/over_50mb.txt" || true
/workspace/venvs/gpu/bin/python -I "$SRC/scripts/scan_secrets.py" "$DST"
git add -A e03
if git diff --cached --quiet; then echo "nothing to commit"; else
  git commit -q -m "$MSG" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
GIT_TERMINAL_PROMPT=0 git push -q origin e03_paraphrase:e03_paraphrase
LOCAL=$(git rev-parse HEAD)
REMOTE=$(GIT_TERMINAL_PROMPT=0 git ls-remote origin refs/heads/e03_paraphrase | cut -f1)
echo "local $LOCAL remote $REMOTE"
[ "$LOCAL" = "$REMOTE" ] && echo "PUSH VERIFIED" || { echo "PUSH MISMATCH"; exit 1; }
