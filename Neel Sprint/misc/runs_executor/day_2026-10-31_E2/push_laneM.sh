#!/bin/bash
# E2 milestone push: copy sprint_work 029-039 into the laneM worktree (no tensors), redact hosts, secret-scan, commit, push.
# usage: push_laneM.sh "commit subject"
set -e
SRC="/workspace/Neel Sprint/experiments/sprint_work"; WT=/root/gh/nsi_laneM; DST="$WT/Neel Sprint/experiments/sprint_work"
cd "$WT"; git fetch -q origin
for d in "$SRC"/0{29,30,31,32,33,34,35,36,37,38,39,82}_*; do [ -d "$d" ] || continue; n=$(basename "$d")
  rsync -a --delete --exclude __pycache__ --exclude '*.pt' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.npy' --exclude '*.npz' --exclude '*.pth' --exclude '*.ckpt' "$d/" "$DST/$n/"
  git add "$DST/$n"; done
git diff --cached --name-only | while IFS= read -r rel; do f="$WT/$rel"; [ -f "$f" ] && sed -i -E 's/<box-ip>/<NODE_IP>/g; s/<box-ip>/<POD_IP>/g; s/(-p |:|port )12050/\1<NODE_PORT>/g; s/(-p |:|port )42863/\1<POD_PORT>/g; s/b0fa70edf0f8/<POD_ID>/g; s/<pod-id>-64410aeb/<POD_USER>/g' "$f"; done
for d in "$DST"/0{29,30,31,32,33,34,35,36,37,38,39,82}_*; do [ -d "$d" ] && git add "$d"; done
if git diff --cached --name-only | grep -qE "\.(pt|safetensors|bin|npy|npz|pth|ckpt|gguf)$"; then echo "TENSOR STAGED: abort"; exit 1; fi
if git diff --cached | grep -qE "sk-or-v1-[A-Za-z0-9]{10,}|hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{20,}|github_pat_|PRIVATE KEY|tml-[A-Za-z0-9]{20,}|(OPENROUTER|TINKER)_API_KEY(_E2)? *= *['\"]?[A-Za-z0-9]|<user>|<user>|<box-ip>|<box-ip>|b0fa70edf0f8|<pod-id>"; then echo "SECRET/HOST FOUND: abort"; exit 1; fi
git diff --cached --quiet && { echo "nothing to commit"; exit 0; }
git -c user.name="$(git log -1 --format=%an)" -c user.email="$(git log -1 --format=%ae)" commit -q -m "$1" -m "Code, design specs, DECISIONS, analyses and READMEs only; no tensors. Hosts redacted." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J4YisZXy6q2u3ccpGxg2J3"
git push -q origin laneM && git log --oneline -1
