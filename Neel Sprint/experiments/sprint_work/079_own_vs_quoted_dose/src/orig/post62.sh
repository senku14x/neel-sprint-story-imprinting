#!/bin/bash
# sw062 background post-processing (= sw056 post56.sh; changes: paths, exp sw062, script names; sw062 DECISIONS D8).
# sw056 header:, box 1 only (API key; launched by E4's post_dispatch from the GPU job's post request, or by hand).
#   bash post56.sh
# prep (labels on continuations + 20% selection) -> two judges (reply5) on the 20% + disagreements -> per-readout agreement
# -> judge every remaining row of a readout whose agreement < 0.95 (within the $4 stop) -> analyze62.py -> results.json, report.txt.
# Markers: RUN/JUDGED (every judge pass that ran is complete), RUN/ANALYSIS_READY. A budget stop leaves RUN/NEEDS_REJUDGE and the
# analysis runs on STRICT (+ whatever was judged), saying so.
set -uo pipefail
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
R=/workspace/runs_executor/sw062; P=$R/post; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/062_turn1_own_reply_seed_reruns/src"
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job post_sw062 --exp sw062 --part post --box box1 "$@" || true; }
echo "post start $(date -u +%FT%TZ)"
[ -e $R/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
B --status running --pid $$ --out $R/post.log --result "labels + judging"
python3 "$SRC/post62.py" prep || { B --status failed --result "prep failed"; exit 1; }
rm -f $P/judged.jsonl.DONE $P/judged_rest_*.jsonl.DONE $R/JUDGED
JR() { python3 "$LIB/judge_run.py" --exp sw062 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post; local r=$?
       if [ $r = 2 ]; then python3 "$LIB/judge_run.py" --exp sw062 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post --new-manifest; r=$?; fi
       return $r; }
ok=1
if python3 "$SRC/post62.py" budget --need-calls $(( $(wc -l < $P/judge_in.jsonl) * 2 )) --kind reply5; then
  JR $P/judge_in.jsonl $P/judged.jsonl; rc=$?; echo "judge 20% exit $rc $(date -u +%FT%TZ)"
  [ $rc = 0 ] || { ok=0; [ $rc = 3 ] && touch $R/NEEDS_REJUDGE; }
else
  ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop before the 20% pass"
fi
python3 "$SRC/post62.py" agree | tee $P/agree.log
for ro in $(grep '^JUDGE_ALL' $P/agree.log | cut -d' ' -f2-); do
  f=$P/judge_rest_$ro.jsonl
  [ -s $f ] || { touch $P/judged_rest_$ro.jsonl.DONE; continue; }
  if python3 "$SRC/post62.py" budget --need-calls $(( $(wc -l < $f) * 2 )) --kind reply5; then
    JR $f $P/judged_rest_$ro.jsonl; rc=$?; echo "judge rest $ro exit $rc"; [ $rc = 0 ] || { ok=0; [ $rc = 3 ] && touch $R/NEEDS_REJUDGE; }
  else
    ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop: $ro not judged in full (agreement < 0.95); analysis keeps STRICT there and says so"
  fi
done
[ $ok = 1 ] && touch $R/JUDGED
/root/venvs/si/bin/python "$SRC/analyze62.py" > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  touch $R/ANALYSIS_READY
  B --status done --out $R/analysis/report.txt --result "$(grep -m1 '^VERDICT' $R/analysis/report.txt | head -c 250)"
else
  B --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post end $(date -u +%FT%TZ)"
