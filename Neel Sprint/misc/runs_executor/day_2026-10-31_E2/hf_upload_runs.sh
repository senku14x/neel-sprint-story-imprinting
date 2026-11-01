#!/bin/bash
# E2: stage run outputs (no captures, no third-party data), redact hosts, scan secrets, upload to the public HF dataset.
set -e
R=/workspace/runs_executor; ST=/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/51af01d4-94b0-43eb-9d93-8fcfa8409254/scratchpad/hf_stage
rm -rf "$ST"; mkdir -p "$ST/runs" "$ST/day_log" "$ST/report"
for d in sw029 sw030 sw031 sw032 sw033 sw034 sw035 sw033_blind sw035_blind1b; do [ -d "$R/$d" ] || continue
  rsync -a --exclude 'caps/' --exclude 'e08_train_data/' --exclude 'backups_*' --exclude '*.safetensors' --exclude 'state_step*.pt' --exclude '__pycache__' --exclude 'judgein*' "$R/$d/" "$ST/runs/$d/"; done
rsync -a --exclude '*.pt' --exclude '__pycache__' --exclude 'status/' --exclude hf_upload_runs.sh --exclude push_laneM.sh "$R/day_2026-10-31_E2/" "$ST/day_log/"
cp /tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/51af01d4-94b0-43eb-9d93-8fcfa8409254/scratchpad/report_e2/e2_lane_m_report.html "$ST/report/"
# redact hosts in every text file
grep -rIlE "<box-ip>|<box-ip>|b0fa70edf0f8|<pod-id>|(-p |port |:)(<port>)\b" "$ST" | while read f; do
  sed -i -E 's/<box-ip>/<NODE_IP>/g; s/<box-ip>/<POD_IP>/g; s/(-p |:|port )<port>\b/\1<NODE_PORT>/g; s/(-p |:|port )<port>\b/\1<POD_PORT>/g; s/b0fa70edf0f8/<POD_ID>/g; s/<pod-id>-64410aeb/<POD_USER>/g' "$f"; done
# secret scan: abort on any hit
if grep -rIlE "sk-or-v1-[A-Za-z0-9]{10,}|hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{20,}|github_pat_|PRIVATE KEY|tml-[A-Za-z0-9]{20,}|(OPENROUTER|TINKER)_API_KEY(_E2)? *= *['\"]?[A-Za-z0-9]|<user>|<box-ip>|<box-ip>|b0fa70edf0f8" "$ST"; then echo "SCAN HIT: abort"; exit 1; fi
echo "staged $(du -sh "$ST" | cut -f1), files $(find "$ST" -type f | wc -l)"
