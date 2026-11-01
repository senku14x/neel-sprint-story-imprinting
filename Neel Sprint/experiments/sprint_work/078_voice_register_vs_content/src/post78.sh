#!/bin/bash
# sw078 post-processing, box 1 only (API key; launched by E4's post_dispatch from the GPU job's post requests, or by hand).
#   bash post78.sh textcheck   : two judges (custom rubric judge_textcheck78.txt) on every native text and generated rewrite candidate
#                                -> textcheck/tc_judged.jsonl -> post78.py tcsum (tc_scores.json: pass flags, text choice, script set)
#   bash post78.sh main        : (text check if not done) -> labels + 20% + disagreements -> two judges reply5 -> agreement (any readout
#                                < 0.95 -> NEEDS_JUDGE_ALL, nothing judged in full) -> consensus -> analyze78.py -> ANALYSIS_READY
# Spend: exp sw078 in the E4 spend.jsonl; budget check (logged + 1.25 x estimate <= $1.5) before every judge pass.
set -uo pipefail
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
R=${SW078_RUN:-/workspace/runs_executor/sw078}; P=$R/post; T=$R/textcheck; LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
SRC="/workspace/Neel Sprint/experiments/sprint_work/078_voice_register_vs_content/src"
export OMP_NUM_THREADS=8 SW078_RUN=$R
B() { python3 "$LIB/board.py" event --job post_sw078 --exp sw078 --part "$1" --box box1 "${@:2}" || true; }
MODE=${1:-main}
echo "post $MODE start $(date -u +%FT%TZ)"

textcheck() {
  [ -s $T/tc_in.jsonl ] || { echo "no tc_in.jsonl"; return 1; }
  if [ ! -e $T/tc_judged.jsonl.DONE ]; then
    python3 "$SRC/post78.py" budget --need-calls $(( $(wc -l < $T/tc_in.jsonl) * 2 )) --kind textcheck || { echo "budget stop before the text check"; return 3; }
    python3 "$LIB/judge_run.py" --exp sw078 --rubric custom --template "$SRC/judge_textcheck78.txt" \
      --fields declines,contempt,asks_help,assistant_voice --in $T/tc_in.jsonl --out $T/tc_judged.jsonl --concurrency 48 --part textcheck
    rc=$?; echo "textcheck judge exit $rc $(date -u +%FT%TZ)"; [ $rc = 0 ] || return $rc
  fi
  python3 "$SRC/post78.py" tcsum && touch $R/TEXTCHECK_DONE
}

if [ "$MODE" = textcheck ]; then
  B textcheck --status running --pid $$ --out $T/textcheck.log --result "text check (content + register)"
  textcheck; rc=$?
  if [ $rc = 0 ]; then B textcheck --status done --result "$(python3 -c "import json;print(json.dumps(json.load(open('$T/tc_scores.json'))['summary'])[:240])")"
  else B textcheck --status failed --result "text check rc=$rc"; fi
  exit $rc
fi

[ -e $R/GPU_DONE ] || { echo "GPU_DONE missing"; exit 1; }
B post --status running --pid $$ --out $R/post.log --result "text check + labels + 20% audit"
# the text check normally ran during the GPU job; wait for it if it is still running (<= 30 min), else run it here
for i in $(seq 1 90); do
  [ -e $R/TEXTCHECK_DONE ] && break
  [ -e /workspace/runs_executor/day_2026-10-31_E4/status/postreq/sw078_textcheck.running ] || break
  sleep 20
done
[ -e $R/TEXTCHECK_DONE ] || textcheck || echo "WARNING: text check incomplete; analysis reports the unfiltered set only"
python3 "$SRC/post78.py" prep || { B post --status failed --result "prep failed"; exit 1; }
rm -f $R/JUDGED $R/NEEDS_JUDGE_ALL
ok=1
if python3 "$SRC/post78.py" budget --need-calls $(( $(wc -l < $P/judge_in.jsonl) * 2 )) --kind reply5; then
  python3 "$LIB/judge_run.py" --exp sw078 --rubric reply5 --in $P/judge_in.jsonl --out $P/judged.jsonl --concurrency 48 --part post; rc=$?
  if [ $rc = 2 ]; then python3 "$LIB/judge_run.py" --exp sw078 --rubric reply5 --in $P/judge_in.jsonl --out $P/judged.jsonl --concurrency 48 --part post --new-manifest; rc=$?; fi
  echo "judge 20% exit $rc $(date -u +%FT%TZ)"; [ $rc = 0 ] || { ok=0; touch $R/NEEDS_REJUDGE; }
else
  ok=0; touch $R/NEEDS_REJUDGE; echo "budget stop before the 20% pass"
fi
python3 "$SRC/post78.py" agree | tee $P/agree.log
python3 "$SRC/post78.py" consensus
[ $ok = 1 ] && touch $R/JUDGED
/root/venvs/si/bin/python "$SRC/analyze78.py" > $P/analyze.log 2>&1; arc=$?
echo "analyze exit $arc $(date -u +%FT%TZ)"
if [ $arc = 0 ]; then
  touch $R/ANALYSIS_READY
  B post --status done --out $R/analysis/report.txt --result "$(grep -m1 '^VERDICT' $R/analysis/report.txt | head -c 250)"
else
  B post --status failed --out $P/analyze.log --result "analysis failed (exit $arc)"
fi
echo "post end $(date -u +%FT%TZ)"
