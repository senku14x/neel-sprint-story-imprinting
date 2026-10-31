#!/bin/bash
# sw060 background post-processing (box 1; system python3; CPU + API only). Launched detached by the full job after GPU_DONE_sw060;
# rerun by hand to resume (judge_run resumes by key):  bash post60.sh [DIR]          (adapted from sw055's post55.sh)
# prep (labels + 20% + disagreements) -> two judges (rubric habit, spend-capped at $6 for sw060) -> agreement per readout group ->
# judge every remaining row of any group whose agreement < 0.95 -> analysis (results.json, report.txt, samples.jsonl) ->
# RUN/ANALYSIS_READY (always written once the analysis exists; JUDGED_sw060 only if every requested judge pass is DONE).
set -uo pipefail
R=/workspace/runs_executor/sw060; D=${1:-$R/full}
SRC="/workspace/Neel Sprint/experiments/sprint_work/060_checkpoint_order/src"; DAY=/workspace/runs_executor/day_2026-10-31_E4
export OMP_NUM_THREADS=8
PY=/usr/bin/python3
B() { $PY "$DAY/lib/board.py" event --job post_sw060 --exp sw060 --part post --box box1 "$@" || true; }
echo "post60 start $(date -u +%FT%TZ) dir $D pid $$"
B --status running --pid $$ --out "$D/post.log" --result "labels + judging (sw060 cap \$6)"
$PY "$SRC/post60.py" prep --dir "$D" || { echo PREP_FAILED; B --status failed --result "prep failed"; exit 1; }
# never trust completion markers from an earlier post run (sw020 review fix R5)
rm -f "$D/judged.jsonl.DONE" "$D"/judged_rest_*.jsonl.DONE "$R/JUDGED_sw060" "$R/ANALYSIS_READY"
taskset -c 0-87 $PY "$SRC/judge_guard60.py" --in "$D/judge_in.jsonl" --out "$D/judged.jsonl" --part full; rc=$?
echo "judge pass 1 exit $rc $(date -u +%FT%TZ)"
$PY "$SRC/post60.py" agree --dir "$D"; arc=$?
need=""
if [ $arc = 10 ]; then
  need=$($PY -c "import json; print(' '.join(json.load(open('$D/agreement.json'))['need_full']))")
  echo "agreement < 0.95 on: $need $(date -u +%FT%TZ)"
  if [ $rc = 0 ]; then
    for g in $need; do
      if [ -s "$D/judge_rest_$g.jsonl" ]; then
        taskset -c 0-87 $PY "$SRC/judge_guard60.py" --in "$D/judge_rest_$g.jsonl" --out "$D/judged_rest_$g.jsonl" --part full; r2=$?
        echo "judge rest $g exit $r2 $(date -u +%FT%TZ)"; [ $r2 = 0 ] || rc=$r2
      else
        touch "$D/judged_rest_$g.jsonl.DONE"
      fi
    done
  fi
fi
$PY "$SRC/analysis60.py" --dir "$D" > "$D/analysis.log" 2>&1; prc=$?
echo "analysis exit $prc $(date -u +%FT%TZ)"
done_all=1; [ -e "$D/judged.jsonl.DONE" ] || done_all=0
for g in $need; do [ -e "$D/judged_rest_$g.jsonl.DONE" ] || done_all=0; done
if [ $prc = 0 ]; then
  [ $done_all = 1 ] && echo "$(date -u +%FT%TZ) judging complete (need_full: ${need:-none})" > "$R/JUDGED_sw060"
  echo "{\"t\": \"$(date -u +%FT%TZ)\", \"results\": \"$D/results.json\", \"report\": \"$D/report.txt\", \"judging_complete\": $done_all, \"judge_rc\": $rc, \"need_full\": \"${need}\"}" > "$R/ANALYSIS_READY.tmp" && mv "$R/ANALYSIS_READY.tmp" "$R/ANALYSIS_READY"
  B --status done --out "$D/report.txt" --result "analysis ready; judging complete=$done_all (rc $rc); $(grep -m1 '^VERDICT' "$D/report.txt")"
else
  B --status failed --out "$D/analysis.log" --result "analysis failed (exit $prc)"
fi
echo "post60 end $(date -u +%FT%TZ)"
