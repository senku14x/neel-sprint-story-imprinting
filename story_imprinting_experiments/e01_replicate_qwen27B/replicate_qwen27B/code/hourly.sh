#!/usr/bin/env bash
# Every 30 minutes: tables, reply stats, progress block in the README, GitHub push, HF upload of eval outputs (verified).
source /workspace/repo/replicate_qwen27B/env.sh
cd "$SI36_CODE"
while true; do
  {
  echo "=== $(date -u +%T) hourly"
  /workspace/venvs/gpu/bin/python reply_stats.py > /dev/null 2>&1
  /workspace/venvs/bloom/bin/python analyze.py > /dev/null 2>&1 || echo "analyze failed"
  /workspace/venvs/bloom/bin/python progress.py | head -3
  cd /workspace/repo
  for d in garble compliance story single_turn reply_stats; do mkdir -p replicate_qwen27B/results/$d; cp /workspace/si36/runs/$d/*_summary.json replicate_qwen27B/results/$d/ 2>/dev/null; done
  mkdir -p replicate_qwen27B/results/bloom && cp /workspace/si36/runs/bloom/*_summary.json replicate_qwen27B/results/bloom/ 2>/dev/null
  cp /workspace/si36/runs/scheduler_state.json /workspace/si36/runs/ratelimit_429_bodies.jsonl /workspace/si36/runs/spend_log.jsonl replicate_qwen27B/results/ 2>/dev/null
  git add -A README.md replicate_qwen27B >/dev/null 2>&1
  if git diff --cached | grep -qE "sk-or-[A-Za-z0-9]|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"; then echo "SECRET PATTERN FOUND; not committing"; git reset -q; else
    git commit -q -m "progress $(date -u +%H:%M) UTC

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q origin replicate_qwen27B 2>&1 | tail -1 && echo "pushed $(git rev-parse --short HEAD)"; fi
  cd "$SI36_CODE"
  /workspace/venvs/gpu/bin/python upload_hf.py evals 2>&1 | grep -E "verified|FAILED" | tail -1
  } >> /workspace/logs/hourly.log 2>&1
  sleep 1800
done
