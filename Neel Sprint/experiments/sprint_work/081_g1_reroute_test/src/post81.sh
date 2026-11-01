#!/bin/bash
# sw081 post-processing for one assignment (box 1 only: API key). Launched by E4's post_dispatch from the GPU job's post request.
#   bash post81.sh <A|B>
# prep (STRICT labels + 20% audit selection) -> budget check ($0.50 cap, all sw081 spend) -> two judges (reply5) on the 20% + every
# STRICT/lexicon disagreement -> agreement (< 0.95 -> RUN/<A>/NEEDS_JUDGE_ALL; no full judging) -> analyze81.py (STRICT primary).
set -uo pipefail
A=${1:?usage: post81.sh A|B}
[ "$(hostname)" = af2422212563 ] || [ -n "${SW081_TEST:-}" ] || { echo "not box 1; refusing"; exit 3; }
R=${SW081_RUN:-/workspace/runs_executor/sw081}; P=$R/$A/post; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/081_g1_reroute_test/src"
export OMP_NUM_THREADS=8
B() { [ -n "${SW081_TEST:-}" ] || python3 "$LIB/board.py" event --job post_sw081_$A --exp sw081 --part post$A --box box1 "$@" || true; }
echo "post $A start $(date -u +%FT%TZ)"
[ -e $R/$A/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
mkdir -p $P
B --status running --pid $$ --out $R/$A/post.log --result "labels + 20% two-judge audit"
python3 "$SRC/post81.py" prep --assign $A || { B --status failed --result "prep failed"; exit 1; }
ok=1
if [ -z "${SW081_NO_JUDGE:-}" ]; then
  if python3 "$SRC/post81.py" budget --assign $A --need-calls $(( $(wc -l < $P/judge_in.jsonl) * 2 )); then
    python3 "$LIB/judge_run.py" --exp sw081 --rubric reply5 --in $P/judge_in.jsonl --out $P/judged.jsonl --concurrency 48 --part post$A; rc=$?
    echo "judge exit $rc $(date -u +%FT%TZ)"; [ $rc = 0 ] || { ok=0; touch $R/$A/NEEDS_REJUDGE; }
  else
    ok=0; touch $R/$A/NEEDS_REJUDGE; echo "budget stop before the 20% audit"
  fi
  python3 "$SRC/post81.py" agree --assign $A | tee $P/agree.log
fi
[ $ok = 1 ] && touch $R/$A/JUDGED
python3 "$SRC/analyze81.py" --run $R > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  B --status done --out $R/analysis/report.txt --result "$(grep -m1 "^VERDICT $A" $R/analysis/report.txt | head -c 250)"
else
  B --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post $A end $(date -u +%FT%TZ)"
exit $arc
