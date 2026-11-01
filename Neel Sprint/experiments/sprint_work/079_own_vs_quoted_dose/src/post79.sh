#!/bin/bash
# sw079 background post-processing (= sw062 post62.sh adapted; sw079 DECISIONS D9-D10), box 1 only (API key; launched by E4's
# post_dispatch from the GPU job's post request, or by hand).   bash post79.sh
# engaged-neutral hist check (both judges, every generated candidate) -> prep (labels + 20% selection) -> two judges (reply5) on the
# 20% + disagreements -> per-readout agreement (< 0.95 -> RUN/NEEDS_JUDGE_ALL, no full judging) -> analyze79.py.
# Budget: logged sw079 spend + 1.25 x estimate <= $0.8 before every pass. Markers: RUN/JUDGED, RUN/ANALYSIS_READY (or NEEDS_REJUDGE).
set -uo pipefail
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
R=${SW079_RUN:-/workspace/runs_executor/sw079}; P=$R/post; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/079_own_vs_quoted_dose/src"
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job post_sw079 --exp sw079 --part post --box box1 "$@" || true; }
echo "post start $(date -u +%FT%TZ)"
[ -e $R/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
B --status running --pid $$ --out $R/post.log --result "engaged check + labels + 20% judging"
ok=1
python3 "$SRC/post79.py" engaged || { B --status failed --result "engaged prep failed"; exit 1; }
if python3 "$SRC/post79.py" budget --need-calls $(( $(wc -l < $P/engaged_in.jsonl) * 2 )) --kind hist; then
  python3 "$LIB/judge_run.py" --exp sw079 --rubric hist --in $P/engaged_in.jsonl --out $P/engaged_judged.jsonl --concurrency 48 --part engaged; rc=$?
  echo "judge engaged exit $rc $(date -u +%FT%TZ)"; [ $rc = 0 ] || { ok=0; touch $R/NEEDS_REJUDGE; }
else
  ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop before the engaged check"
fi
python3 "$SRC/post79.py" prep || { B --status failed --result "prep failed"; exit 1; }
rm -f $P/judged.jsonl.DONE $R/JUDGED
JR() { python3 "$LIB/judge_run.py" --exp sw079 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post; local r=$?
       if [ $r = 2 ]; then python3 "$LIB/judge_run.py" --exp sw079 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post --new-manifest; r=$?; fi
       return $r; }
if python3 "$SRC/post79.py" budget --need-calls $(( $(wc -l < $P/judge_in.jsonl) * 2 )) --kind reply5; then
  JR $P/judge_in.jsonl $P/judged.jsonl; rc=$?; echo "judge 20% exit $rc $(date -u +%FT%TZ)"
  [ $rc = 0 ] || { ok=0; touch $R/NEEDS_REJUDGE; }
else
  ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop before the 20% pass"
fi
python3 "$SRC/post79.py" agree | tee $P/agree.log
[ $ok = 1 ] && touch $R/JUDGED
/root/venvs/si/bin/python "$SRC/analyze79.py" --run $R > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  touch $R/ANALYSIS_READY
  B --status done --out $R/analysis/report.txt --result "$(grep -m1 '^VERDICT' $R/analysis/report.txt | head -c 250)"
else
  B --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post end $(date -u +%FT%TZ)"
