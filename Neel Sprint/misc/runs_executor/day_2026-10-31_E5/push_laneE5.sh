#!/bin/bash
# E5 milestone push: copy sprint_work 071-079 (+ E5 day-dir records) into the laneE5 worktree (no tensors), redact hosts, secret-scan, commit, push.
# usage: push_laneE5.sh "commit subject"
set -e
SRC="/workspace/Neel Sprint/experiments/sprint_work"; WT=/root/gh/nsi_laneE5; DST="$WT/Neel Sprint/experiments/sprint_work"
DAY=/workspace/runs_executor/day_2026-10-31_E5; DDST="$WT/runs_executor_records/day_2026-10-31_E5"
cd "$WT"; git fetch -q origin
for d in "$SRC"/07{1,2,3,4,5,6,7}_* "$SRC"/08{3,4}_*; do [ -d "$d" ] || continue; n=$(basename "$d")
  rsync -a --delete --exclude __pycache__ --exclude '*.pt' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.npy' --exclude '*.npz' --exclude '*.pth' --exclude '*.ckpt' --exclude '*.pkl' --max-size=20m "$d/" "$DST/$n/"
  git add "$DST/$n"; done
mkdir -p "$DDST"; for f in CONVENTIONS_E5.md DECISIONS.md AGENT_BRIEF_COMMON.md caps.json; do [ -f "$DAY/$f" ] && cp "$DAY/$f" "$DDST/"; done
rsync -a --exclude __pycache__ --exclude 'validation/*.jsonl' "$DAY/lib/" "$DDST/lib/"; [ -d "$DAY/forecast_frozen" ] && rsync -a "$DAY/forecast_frozen/" "$DDST/forecast_frozen/"
git add "$DDST"
git diff --cached --name-only | while IFS= read -r rel; do f="$WT/$rel"; [ -f "$f" ] && sed -i -E 's/<box-ip>/<NODE_IP>/g; s/(-p |:|port )17106/\1<NODE_PORT>/g; s/5aa4812c9105/<NODE_ID>/g; s/<box-ip>/<POD_IP>/g; s/<box-ip>/<POD_IP>/g' "$f"; done
git add "$DST" "$DDST"
if git diff --cached --name-only | grep -qE "\.(pt|safetensors|bin|npy|npz|pth|ckpt|gguf|pkl)$"; then echo "TENSOR STAGED: abort"; exit 1; fi
if git diff --cached | grep -qE "sk-or-v1-[A-Za-z0-9]{10,}|hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{20,}|github_pat_|PRIVATE KEY|tml-[A-Za-z0-9]{20,}|(OPENROUTER|TINKER)_API_KEY(_ALT|_E5)? *= *['\"]?[A-Za-z0-9]|<user>|<user>|<box-ip>|5aa4812c9105|<box-ip>|<box-ip>"; then echo "SECRET/HOST FOUND: abort"; exit 1; fi
git diff --cached --quiet && { echo "nothing to commit"; exit 0; }
git -c user.name="$(git log -1 --format=%an)" -c user.email="$(git log -1 --format=%ae)" commit -q -m "$1" -m "Code, design specs, DECISIONS, analyses and READMEs only; no tensors. Hosts redacted." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J4YisY7NDskcV5r6re8qQa"
git push -q -u origin laneE5 && git log --oneline -1
