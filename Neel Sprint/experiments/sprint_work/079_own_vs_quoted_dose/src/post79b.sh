#!/bin/bash
# sw079 Amendment 1 (job 42) background post-processing = post79.sh without the engaged-neutral check (prep D300+). Box 1 only
# (judge key); launched by E4's post_dispatch from status/postreq/sw079b_post.req, or by hand:   bash post79b.sh
# prep (labels + 20% selection) -> two judges (reply5, ALT key via judge_lib) on the 20% + STRICT/lexicon disagreements -> per-readout
# agreement (< 0.95 -> RUN/NEEDS_JUDGE_ALL, no full judging) -> analyze79b.py.
# Budget: logged sw079b spend + 1.25 x estimate <= $0.40 before judging. Markers: RUN/JUDGED, RUN/ANALYSIS_READY (or NEEDS_REJUDGE).
set -uo pipefail
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
R=${SW079B_RUN:-/workspace/runs_executor/sw079b}; P=$R/post; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/079_own_vs_quoted_dose/src"
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job post_sw079b --exp sw079b --part post --box box1 "$@" || true; }
echo "post start $(date -u +%FT%TZ)"
[ -e $R/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
B --status running --pid $$ --out $R/post.log --result "labels + 20% judging"
ok=1
python3 "$SRC/post79b.py" prep || { B --status failed --result "prep failed"; exit 1; }
rm -f $P/judged.jsonl.DONE $R/JUDGED
JR() { python3 "$LIB/judge_run.py" --exp sw079b --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post; local r=$?
       if [ $r = 2 ]; then python3 "$LIB/judge_run.py" --exp sw079b --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post --new-manifest; r=$?; fi
       return $r; }
if python3 "$SRC/post79b.py" budget --need-calls $(( $(wc -l < $P/judge_in.jsonl) * 2 )) --kind reply5; then
  JR $P/judge_in.jsonl $P/judged.jsonl; rc=$?; echo "judge 20% exit $rc $(date -u +%FT%TZ)"
  [ $rc = 0 ] || { ok=0; touch $R/NEEDS_REJUDGE; }
elif python3 "$SRC/post79b.py" budget --need-calls $(( $(wc -l < $P/judge_in_rand20.jsonl) * 2 )) --kind reply5; then
  echo "budget cannot cover 20% + disagreements; judging the random 20% only (agreement is computed on it)"
  JR $P/judge_in_rand20.jsonl $P/judged.jsonl; rc=$?; echo "judge rand20 exit $rc $(date -u +%FT%TZ)"
  ok=0; touch $R/NEEDS_REJUDGE
else
  ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop before the 20% pass"
fi
python3 "$SRC/post79b.py" agree | tee $P/agree.log
[ $ok = 1 ] && touch $R/JUDGED
/root/venvs/si/bin/python "$SRC/analyze79b.py" --run $R > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  touch $R/ANALYSIS_READY
  B --status done --out $R/analysis/report.txt --result "$(grep -m1 '^READING' $R/analysis/report.txt | head -c 250)"
else
  B --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post end $(date -u +%FT%TZ)"
