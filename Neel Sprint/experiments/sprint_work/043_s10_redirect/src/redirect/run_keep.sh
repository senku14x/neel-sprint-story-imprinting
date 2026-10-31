#!/bin/bash
# sw043 redirect keep pipeline (box 1; 043 DECISIONS D7/D8). E4's keep commands verbatim for dismissive + helpful (NOTE_TO_E3 13:05),
# the casual wrapper for casual; rounds 0-3 in order; the ALT key's limit_remaining is read before every judge batch (stop < $40).
set -uo pipefail
S="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src/e4/keep"; W="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src/redirect"
T="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src/casual/judge_casual_template.txt"
D=/workspace/runs_executor/sw043/redirect_data; CAP=${CAP:-5}
lim() { python3 -I "$W/keylim.py" | python3 -c "import json,sys; print(json.load(sys.stdin)['limit_remaining'])"; }
check() { L=$(lim); echo "[$(date -u +%FT%TZ)] key limit_remaining $L before $1"; python3 -c "import sys; sys.exit(0 if float('$L') >= 40 else 1)" || { echo "KEY_BELOW_40 $L"; exit 3; }; }
(cd "$S" && sha256sum -c SHA256SUMS) || { echo "E4 keep copies changed"; exit 4; }
for r in 0 1 2 3; do
  python3 "$S/redirect_keep61.py" prep --cand $D/candidates.jsonl --dir $D --round $r --styles dismissive,helpful || exit 5
  if [ -s $D/judge_in_r$r.jsonl ]; then
    check "main r$r"
    python3 "$S/judge_guard61.py" --exp sw043 --cap $CAP --rubric custom --template "$S/judge_hist1_61.txt" --fields helpful,warm,declines,not_my_job,hostile \
      --in $D/judge_in_r$r.jsonl --out $D/judged_r$r.jsonl --part redirect_r$r; rc=$?; echo "main r$r judge rc=$rc"; [ $rc = 0 ] || exit $rc
  fi
  python3 -I "$W/keep43_casual.py" prep $r || exit 6
  if [ -s $D/casual/judge_in_r$r.jsonl ]; then
    check "casual r$r"
    python3 "$S/judge_guard61.py" --exp sw043 --cap $CAP --rubric custom --template "$T" --fields casual,helps \
      --in $D/casual/judge_in_r$r.jsonl --out $D/casual/judged_r$r.jsonl --part redirect_cas_r$r; rc=$?; echo "casual r$r judge rc=$rc"; [ $rc = 0 ] || exit $rc
  fi
done
python3 "$S/redirect_keep61.py" select --cand $D/candidates.jsonl --dir $D --styles dismissive,helpful --n_keep 1000 > $D/select_e4_2way.log 2>&1; echo "E4 2-way select rc=$?"
python3 -I "$W/keep43_casual.py" select; rc=$?; echo "3-way select rc=$rc"
check "end"
echo "KEEP_DONE $(date -u +%FT%TZ)"
