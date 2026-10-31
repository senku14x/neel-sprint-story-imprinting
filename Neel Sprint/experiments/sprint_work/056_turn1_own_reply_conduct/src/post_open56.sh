#!/bin/bash
# sw056 openings judging + frozen selection, box 1 only (API key). Idempotent: does nothing once OPENINGS_READY exists.
#   bash post_open56.sh
set -uo pipefail
[ "$(hostname)" = <host> ] || { echo "not box 1; refusing (API work runs on box 1 only)"; exit 3; }
R=/workspace/runs_executor/sw056; O=$R/openings; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/056_turn1_own_reply_conduct/src"
export OMP_NUM_THREADS=8
echo "post_open start $(date -u +%FT%TZ)"
[ -e $R/OPENINGS_READY ] && { echo "OPENINGS_READY exists; nothing to do"; exit 0; }
[ -e $R/OPENINGS_WRITTEN ] || { echo "OPENINGS_WRITTEN missing"; exit 1; }
python3 "$SRC/open56_select.py" prep || exit 1
# budget: the whole experiment stops at $4 (spend.jsonl, exp sw056)
python3 "$SRC/post56.py" budget --need-calls $(( $(wc -l < $O/judge_in.jsonl) * 2 )) --kind hist || { echo "BUDGET: would exceed the sw056 stop"; exit 3; }
python3 "$LIB/judge_run.py" --exp sw056 --rubric hist --in $O/judge_in.jsonl --out $O/judged.jsonl --concurrency 48 --part openings; rc=$?
echo "judge exit $rc $(date -u +%FT%TZ)"
[ $rc = 0 ] || exit $rc
python3 "$SRC/open56_select.py" select; rc=$?
echo "post_open end $(date -u +%FT%TZ) rc=$rc"
exit $rc
