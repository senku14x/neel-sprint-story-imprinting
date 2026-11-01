#!/usr/bin/env bash
# Wrap-up after the scheduler exits (Amendment 5, point 9). Does not stop the pod (that is the last manual step).
source /workspace/repo/replicate_qwen27B/env.sh
cd "$SI36_CODE"
PYB=/workspace/venvs/bloom/bin/python; PYG=/workspace/venvs/gpu/bin/python
until grep -q "scheduler exits" /workspace/logs/scheduler.log; do sleep 30; done
echo "STEP $(date -u +%T) scheduler done; wrap-up"
$PYB compliance.py --all
$PYG reply_stats.py > /dev/null 2>&1
$PYB analyze.py > /dev/null 2>&1
$PYB export_transcripts.py
# judge check (Amendment 6, item 5): ~20 min for <= 200 GPT-4.1 calls at 20/min. If it does not fit,
# move the deadline once for it. If the 90-minute extension already happened, the deadline is later anyway.
DL=$($PYB -c "
import json, os
p='/workspace/si36/runs/deadline_extension.json'
print(json.load(open(p))['new_deadline_utc'] if os.path.exists(p) else '21:00')")
LEFT=$(( ( $(date -u -d "$DL" +%s) - $(date -u +%s) ) / 60 ))
echo "STEP $(date -u +%T) deadline $DL UTC, $LEFT min left"
if [ "$LEFT" -lt 45 ] && [ "$DL" = "21:00" ]; then
  NEWSECS=$(( $(date -u -d "21:30" +%s) - $(date -u +%s) ))
  tmux kill-session -t deadline 2>/dev/null
  tmux new -d -s deadline "sleep $NEWSECS; runpodctl pod stop $RUNPOD_POD_ID"
  echo "{\"moved_at\": \"$(date -u +%T)\", \"new_deadline_utc\": \"21:30\", \"reason\": \"judge check did not fit before 21:00 (Amendment 6, item 5)\"}" > /workspace/si36/runs/deadline_judge_move.json
  echo "STEP $(date -u +%T) DEADLINE MOVED for the judge check"
  DL="21:30"; LEFT=$(( NEWSECS / 60 ))
fi
if [ "$LEFT" -ge 35 ]; then
  echo "STEP $(date -u +%T) judge check"
  timeout 1500 $PYB judge_check.py --max-pos 100 --max-neg 100 --budget 4.0 --cap 90 || echo "JUDGE CHECK INCOMPLETE"
  $PYB analyze.py > /dev/null 2>&1
else
  echo "JUDGE CHECK SKIPPED: not enough time even with the 21:30 move"
  echo '{"skipped": true, "reason": "not enough time before the deadline; run later from the saved transcripts with code/judge_check.py"}' > ../results/judge_check.json
fi
$PYB progress.py > /dev/null 2>&1
cd /workspace/repo
for d in garble compliance story single_turn reply_stats; do mkdir -p replicate_qwen27B/results/$d; cp /workspace/si36/runs/$d/*_summary.json replicate_qwen27B/results/$d/ 2>/dev/null; done
mkdir -p replicate_qwen27B/results/bloom && cp /workspace/si36/runs/bloom/*_summary.json replicate_qwen27B/results/bloom/
cp /workspace/si36/runs/scheduler_state.json /workspace/si36/runs/ratelimit_429_bodies.jsonl /workspace/si36/runs/spend_log.jsonl /workspace/si36/runs/auditor_decision.json /workspace/si36/runs/deadline_*.json replicate_qwen27B/results/ 2>/dev/null
mkdir -p replicate_qwen27B/logs && cp /workspace/logs/scheduler.log /workspace/logs/watchdog.log replicate_qwen27B/logs/ 2>/dev/null
git add -A README.md replicate_qwen27B
git diff --cached | grep -qE "sk-or-[A-Za-z0-9]|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}" && { echo "SECRET PATTERN; not pushing"; exit 1; }
git commit -q -m "final results (automatic wrap-up)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"; git push -q origin replicate_qwen27B && echo "pushed $(git rev-parse --short HEAD)"
cd "$SI36_CODE"
$PYG upload_hf.py evals | tail -1
for a in hb_dc_s0 hc_db_s0; do $PYG upload_hf.py adapters $a | tail -1; done
echo "WRAPUP DONE $(date -u +%T)"
