#!/bin/bash
# sw080 background post-processing (from sw062's post62.sh; sw080 DECISIONS D6). Box 1 only (API key ALT via judge_lib; launched by
# E4's post_dispatch from the GPU job's post request, or by hand):  bash post80.sh
# prep (STRICT labels = primary; seeded 20% audit selections p1 forced primary cells, p2 free primary cells, p3 other forced cells)
# -> two judges (reply5) pass by pass, the budget checked before each pass against the $0.5 cap (p3 judged only up to what is left,
# as a random prefix) -> per-readout agreement; agreement < 0.95 -> RUN/NEEDS_JUDGE_ALL (never judge everything here)
# -> analyze80.py -> RUN/analysis/report.txt + RUN/ANALYSIS_READY.
set -uo pipefail
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
R=${SW080_RUN:-/workspace/runs_executor/sw080}; P=$R/post; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/080_turn1_on_g1/src"
export OMP_NUM_THREADS=8
B() { [ -n "${SW080_NO_BOARD:-}" ] && return 0; python3 "$LIB/board.py" event --job post_sw080 --exp sw080 --part post --box box1 "$@" || true; }
echo "post start $(date -u +%FT%TZ)"
[ -e $R/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
B --status running --pid $$ --out $R/post.log --result "labels + 20% audit"
python3 "$SRC/post80.py" prep || { B --status failed --result "prep failed"; exit 1; }
rm -f $R/JUDGED $R/NEEDS_JUDGE_ALL $R/AUDIT_PARTIAL
JR() { python3 "$LIB/judge_run.py" --exp sw080 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post "${@:3}"; local r=$?
       if [ $r = 2 ]; then python3 "$LIB/judge_run.py" --exp sw080 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part post --new-manifest "${@:3}"; r=$?; fi
       return $r; }
ok=1
for p in p1 p2; do
  f=$P/judge_$p.jsonl
  if python3 "$SRC/post80.py" budget --need-calls $(( $(wc -l < $f) * 2 )) --kind reply5; then
    JR $f $P/judged_$p.jsonl; rc=$?; echo "judge $p exit $rc $(date -u +%FT%TZ)"; [ $rc = 0 ] || ok=0
  else
    ok=0; echo "budget stop before $p ($(date -u +%FT%TZ))"; echo "$p skipped: budget" >> $R/AUDIT_PARTIAL
  fi
done
n3=$(wc -l < $P/judge_p3.jsonl); k3=$(python3 "$SRC/post80.py" allow --kind reply5 --cap-rows $n3)
if [ "${k3:-0}" -gt 0 ]; then
  JR $P/judge_p3.jsonl $P/judged_p3.jsonl --limit $k3; rc=$?; echo "judge p3 ($k3 / $n3 rows) exit $rc $(date -u +%FT%TZ)"; [ $rc = 0 ] || ok=0
fi
[ "${k3:-0}" -lt "$n3" ] && echo "p3 judged ${k3:-0}/$n3 rows (random prefix; \$0.5 cap)" >> $R/AUDIT_PARTIAL
python3 "$SRC/post80.py" agree | tee $P/agree.log
na=$(grep '^NEEDS_JUDGE_ALL' $P/agree.log | cut -d' ' -f2-)
if [ -n "$na" ]; then echo "$na" > $R/NEEDS_JUDGE_ALL; echo "agreement < 0.95 in: $na -> NEEDS_JUDGE_ALL written (not judged in full)"; fi
[ $ok = 1 ] && touch $R/JUDGED
/root/venvs/si/bin/python "$SRC/analyze80.py" --run $R > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  touch $R/ANALYSIS_READY
  B --status done --out $R/analysis/report.txt --result "$(grep -m1 '^VERDICT' $R/analysis/report.txt | head -c 250)"
else
  B --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post end $(date -u +%FT%TZ)"
