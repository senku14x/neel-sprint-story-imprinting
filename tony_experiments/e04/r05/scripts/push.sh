#!/usr/bin/env bash
# Copy R05's deliverables into the clone under e04/r05/, skip files over 50 MB and adapters, scan for credentials,
# commit and push branch e04_content_voice, then check the remote head equals the local commit. (R02's push.sh, paths changed;
# R02's gen/ copy step dropped: R05 generates no stories.)
# R05 fix (02:00 UTC 26 Oct): the excludes are anchored at r05/'s top level. R02's and R03's unanchored 'runs/' also dropped
# si36/runs/ (Bloom transcripts, scores, compliance, garble, single-turn and story outputs); the si36/data link is left out.
#   bash push.sh "commit message"
set -euo pipefail
exec 9>/workspace/e04/r05/logs/push.lock; flock 9   # one push at a time
MSG=${1:-"E04 R05 update"}
SRC=/workspace/e04/r05
GH=/workspace/e04/r05/gh/repo
DST=$GH/e04/r05
cd "$GH"
[ "$(git symbolic-ref --short HEAD)" = "e04_content_voice" ] || { echo "not on e04_content_voice"; exit 1; }
mkdir -p "$DST" "$DST/logs"
find "$SRC" -path "$SRC/gh" -prune -o -path "$SRC/cache" -prune -o -path "$SRC/adapters" -prune -o -path "$SRC/runs" -prune -o -path "$SRC/lora_vllm" -prune -o -type f -size +50M -print 2>/dev/null > "$SRC/logs/over_50mb.txt" || true
rsync -a --delete --max-size=50m --prune-empty-dirs \
  --exclude '__pycache__/' --exclude '*.pyc' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.pt' --exclude '*.npz' \
  --exclude '/adapters/' --exclude '/src/' --exclude '/lora_vllm/' --exclude '/cache/' --exclude '/gh/' --exclude '/merged/' --exclude '/runs/' \
  --exclude '/si36/data' \
  --exclude '*.tmp' --exclude '*.pid' --exclude '*.lock' "$SRC/" "$DST/"
/workspace/venvs/gpu/bin/python -I /workspace/e04/scripts/scan_secrets.py "$DST"
git add -A e04/r05
if git diff --cached --quiet; then echo "nothing to commit"; else
  git commit -q -m "$MSG" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
GIT_TERMINAL_PROMPT=0 git push -q origin e04_content_voice:e04_content_voice
LOCAL=$(git rev-parse HEAD)
REMOTE=$(GIT_TERMINAL_PROMPT=0 git ls-remote origin refs/heads/e04_content_voice | cut -f1)
echo "local $LOCAL remote $REMOTE"
[ "$LOCAL" = "$REMOTE" ] && echo "PUSH VERIFIED" || { echo "PUSH MISMATCH"; exit 1; }
