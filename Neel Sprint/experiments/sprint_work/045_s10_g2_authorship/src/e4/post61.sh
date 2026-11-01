#!/bin/bash
# sw061 evaluation background post (box 1; system python3; CPU + API). bash post61.sh OUT_DIR [EXP] [CAP]
#   EXP (default sw061; E3 passes its own experiment id) tags spend in the E4 day spend.jsonl; CAP (default 8) = that experiment's
#   whole judging cap (judge_guard61 stops when logged spend + an in-flight margin reaches it). Resumable (judge_run resumes by key).
# prep -> chat 20% + disagreements (reply5) -> story 20% + disagreements (habit) -> conduct (all t1 free; one-reply sw005 rubric) ->
# garble (all; 001 rubric) -> agreement -> judge-all for groups < 0.95 -> analysis -> OUT/ANALYSIS_READY (JUDGED only if all DONE).
set -uo pipefail
D=${1:?out dir}; EXP=${2:-sw061}; CAP=${3:-8}
SRC="/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"; DAY=/workspace/runs_executor/day_2026-10-31_E4
export OMP_NUM_THREADS=8; PY=/usr/bin/python3; SPEC="$D/spec.json"
[ "$(hostname)" = af2422212563 ] || { echo "judging runs on box 1 only"; exit 4; }
RUN=$($PY -c "import json;print(json.load(open('$SPEC'))['run'])")
B() { $PY "$DAY/lib/board.py" event --job "post_sw061_$RUN" --exp "$EXP" --part "post_$RUN" --box box1 "$@" || true; }
echo "post61 start $(date -u +%FT%TZ) dir $D exp $EXP cap $CAP pid $$"
B --status running --pid $$ --out "$D/post.log" --result "labels + judging ($EXP cap \$$CAP)"
$PY "$SRC/post61.py" prep --dir "$D" --spec "$SPEC" || { B --status failed --result "prep failed"; exit 1; }
rm -f "$D"/*.DONE "$D/JUDGED" "$D/ANALYSIS_READY"
G() { taskset -c 0-87 $PY "$SRC/judge_guard61.py" --exp "$EXP" --cap "$CAP" --part "$RUN" "$@"; }
rc=0
G --rubric reply5 --in "$D/judge_in_chat.jsonl" --out "$D/judged_chat.jsonl" || rc=$?
[ -s "$D/judge_in_story.jsonl" ] && { G --rubric habit --in "$D/judge_in_story.jsonl" --out "$D/judged_story.jsonl" || rc=$?; }
G --rubric custom --template "$SRC/judge_hist1_61.txt" --fields helpful,warm,declines,not_my_job,hostile --in "$D/judge_conduct.jsonl" --out "$D/judged_conduct.jsonl" || rc=$?
G --rubric custom --template "$SRC/judge_garble61.txt" --fields bee_steering,crow_steering,chat_form_coherence,fluency --in "$D/judge_garble.jsonl" --out "$D/judged_garble.jsonl" || rc=$?
echo "judge passes exit $rc $(date -u +%FT%TZ)"
$PY "$SRC/post61.py" agree --dir "$D" --spec "$SPEC"; arc=$?
if [ $arc = 10 ] && [ $rc = 0 ]; then
  while read -r fam f; do
    rub=reply5; [ "$fam" = story ] && rub=habit
    if [ -s "$D/$f.jsonl" ]; then G --rubric $rub --in "$D/$f.jsonl" --out "$D/${f/judge_rest/judged_rest}.jsonl" || rc=$?; fi
  done < <($PY "$SRC/post61.py" rest --dir "$D" --spec "$SPEC")
fi
$PY "$SRC/analysis61.py" --dir "$D" --spec "$SPEC" > "$D/analysis.log" 2>&1; prc=$?
echo "analysis exit $prc $(date -u +%FT%TZ)"
if [ $prc = 0 ]; then
  [ $rc = 0 ] && echo "$(date -u +%FT%TZ) judging complete" > "$D/JUDGED"
  echo "{\"t\": \"$(date -u +%FT%TZ)\", \"results\": \"$D/results.json\", \"report\": \"$D/report.txt\", \"judge_rc\": $rc}" > "$D/ANALYSIS_READY"
  B --status done --out "$D/report.txt" --result "analysis ready (judge rc $rc)"
else
  B --status failed --out "$D/analysis.log" --result "analysis failed (exit $prc)"
fi
echo "post61 end $(date -u +%FT%TZ)"
