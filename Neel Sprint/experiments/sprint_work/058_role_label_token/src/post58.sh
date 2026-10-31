#!/bin/bash
# sw058 background post-processing, box 1 only (API key; launched by E4's post_dispatch from the GPU job's post request, or by hand).
#   bash post58.sh
# prep (labels + 20% selection + disagreements) -> two judges (reply5) -> per-readout agreement -> judge every remaining row of a
# readout whose agreement < 0.95 -> consensus file -> analyze58.py -> results.json, report.txt.
# Spend: exp sw058 in the E4 spend.jsonl; a budget check before every judge pass (logged spend + estimate <= $6) and a watchdog
# that kills the running judge_run (by its PID) once the logged sw058 spend reaches $6.
# Markers: RUN/JUDGED (every judge pass that ran is complete), RUN/ANALYSIS_READY. A budget stop leaves RUN/NEEDS_REJUDGE and the
# analysis runs on STRICT (+ whatever was judged), saying so.
set -uo pipefail
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
R=/workspace/runs_executor/sw058; P=$R/post; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/058_role_label_token/src"
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job post_sw058 --exp sw058 --part post --box box1 "$@" || true; }
echo "post start $(date -u +%FT%TZ)"
[ -e $R/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
B --status running --pid $$ --out $R/post.log --result "labels + judging"
python3 "$SRC/post58.py" prep || { B --status failed --result "prep failed"; exit 1; }
rm -f $R/JUDGED
JR1() { python3 "$LIB/judge_run.py" --exp sw058 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post $3 & local pid=$!
        while kill -0 $pid 2>/dev/null; do
          if ! python3 "$SRC/post58.py" budget --need-calls 0 > /dev/null; then echo "spend reached the \$6 stop: killing judge_run $pid"; kill $pid; fi
          sleep 30
        done
        wait $pid; }
JR() { JR1 "$1" "$2" ""; local r=$?
       if [ $r = 2 ]; then JR1 "$1" "$2" "--new-manifest"; r=$?; fi
       if ! python3 "$SRC/post58.py" budget --need-calls 0 > /dev/null; then r=3; fi
       return $r; }
ok=1
if python3 "$SRC/post58.py" budget --need-calls $(( $(wc -l < $P/judge_in.jsonl) * 2 )); then
  JR $P/judge_in.jsonl $P/judged.jsonl; rc=$?; echo "judge 20% exit $rc $(date -u +%FT%TZ)"
  [ $rc = 0 ] || { ok=0; [ $rc = 3 ] && touch $R/NEEDS_REJUDGE; }
else
  ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop before the 20% pass"
fi
python3 "$SRC/post58.py" agree | tee $P/agree.log
for ro in $(grep '^JUDGE_ALL' $P/agree.log | cut -d' ' -f2-); do
  f=$P/judge_rest_$ro.jsonl
  [ -s $f ] || { touch $P/judged_rest_$ro.jsonl.DONE; continue; }
  if python3 "$SRC/post58.py" budget --need-calls $(( $(wc -l < $f) * 2 )); then
    JR $f $P/judged_rest_$ro.jsonl; rc=$?; echo "judge rest $ro exit $rc"; [ $rc = 0 ] || { ok=0; [ $rc = 3 ] && touch $R/NEEDS_REJUDGE; }
  else
    ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop: $ro not judged in full (agreement < 0.95); analysis keeps STRICT there and says so"
  fi
done
python3 "$SRC/post58.py" consensus
[ $ok = 1 ] && touch $R/JUDGED
/root/venvs/si/bin/python "$SRC/analyze58.py" > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  touch $R/ANALYSIS_READY
  B --status done --out $R/analysis/report.txt --result "$(grep -m1 '^VERDICT' $R/analysis/report.txt | head -c 250)"
else
  B --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post end $(date -u +%FT%TZ)"
