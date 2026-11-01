#!/bin/bash
# sw059 background post-processing, box 1 only (API key; launched by E4's lib/post_dispatch.sh from the GPU job's post request, or by hand).
#   bash post59.sh
# prep (labels + 20% selection) -> role-break judge known-answer set + every free reply (custom rubric) -> two judges on the 20% +
# disagreements (reply5 for forced/free, habit for L) -> per-readout agreement -> judge the rest of a readout whose agreement < 0.95
# (within the $6 stop) -> analyze59.py -> results.json, report.txt. Markers: RUN/JUDGED (every pass that ran is complete),
# RUN/ANALYSIS_READY. A budget stop leaves RUN/NEEDS_REJUDGE and the analysis runs on STRICT (+ whatever was judged), saying so.
set -uo pipefail
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
R=/workspace/runs_executor/sw059; P=$R/post; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/059_incontext_twin/src"
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job post_sw059 --exp sw059 --part post --box box1 "$@" || true; }
echo "post start $(date -u +%FT%TZ)"
[ -e $R/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
B --status running --pid $$ --out $R/post.log --result "labels + judging"
python3 "$SRC/post59.py" prep || { B --status failed --result "prep failed"; exit 1; }
rm -f $R/JUDGED
JR() {  # rubric in out [extra args]
  local rub=$1 in=$2 out=$3; shift 3
  python3 "$LIB/judge_run.py" --exp sw059 --rubric $rub --in "$in" --out "$out" --concurrency 48 --part post "$@"; local r=$?
  if [ $r = 2 ]; then python3 "$LIB/judge_run.py" --exp sw059 --rubric $rub --in "$in" --out "$out" --concurrency 48 --part post --new-manifest "$@"; r=$?; fi
  return $r; }
RB=(--template "$SRC/role_break_template.txt" --fields role_break)
ok=1
pass() {  # kind rubric in out [extra]
  local kind=$1 rub=$2 in=$3 out=$4; shift 4
  [ -s "$in" ] || { echo "empty $in"; return 0; }
  if python3 "$SRC/post59.py" budget --need-calls $(( $(wc -l < "$in") * 2 )) --kind $kind; then
    JR $rub "$in" "$out" "$@"; local rc=$?; echo "judge $(basename $in) exit $rc $(date -u +%FT%TZ)"
    [ $rc = 0 ] || { ok=0; [ $rc = 3 ] && touch $R/NEEDS_REJUDGE; }
  else
    ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop before $(basename $in)"
  fi; }
# priority order: the role-break label (stop rule) first, then the primary forced readout, then L, then the rest
pass rb custom $P/judge_in_rb_kat.jsonl $P/judged_rb_kat.jsonl "${RB[@]}"
pass rb custom $P/judge_in_rb.jsonl $P/judged_rb.jsonl "${RB[@]}"
pass reply5 reply5 $P/judge_in_reply.jsonl $P/judged_reply.jsonl
pass habit habit $P/judge_in_L.jsonl $P/judged_L.jsonl
python3 "$SRC/post59.py" agree | tee $P/agree.log
for ro in $(grep '^JUDGE_ALL' $P/agree.log | cut -d' ' -f2-); do
  f=$P/judge_rest_$ro.jsonl
  [ -s $f ] || continue
  if [ $ro = L ]; then pass habit habit $f $P/judged_rest_$ro.jsonl; else pass reply5 reply5 $f $P/judged_rest_$ro.jsonl; fi
done
[ $ok = 1 ] && touch $R/JUDGED
/root/venvs/si/bin/python "$SRC/analyze59.py" > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  touch $R/ANALYSIS_READY
  B --status done --out $R/analysis/report.txt --result "$(grep -m1 '^VERDICT' $R/analysis/report.txt | head -c 250)"
else
  B --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post end $(date -u +%FT%TZ)"
