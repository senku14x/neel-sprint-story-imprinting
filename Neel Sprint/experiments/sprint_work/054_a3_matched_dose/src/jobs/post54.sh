#!/bin/bash
# sw054 post-processing on box 1 (CPU / API; started by the box-1 watcher watch54.sh after OUTPUT_GATES_OK, or by the main job on
# box 1 if the watcher is gone, or by hand: bash post54.sh; one run at a time, flock). System python3
# (httpx). Judging per the E1 20% policy: STRICT + lexicon on every row (metrics54); both judges on a seeded 20% per cell + every
# STRICT/lexicon disagreement (habit rubric: story lines + forced chat; reply5: free replies if they ran); if STRICT-vs-judge
# agreement on the random-sample rows < 0.95 -> judge every row of that rubric, unless the projected sw054 spend would pass $5.
# Then report (frozen estimands and rules), qual dump (10 seeded raw outputs per key cell), ANALYSIS_READY, board note.
set -uo pipefail
R=/workspace/runs_executor/sw054
SRC="/workspace/Neel Sprint/experiments/sprint_work/054_a3_matched_dose/src"
L=/workspace/runs_executor/day_2026-10-31_E1/lib
SPEND=/workspace/runs_executor/day_2026-10-31_E1/spend.jsonl
PY=/usr/bin/python3
cd "$SRC"
[ "$(hostname)" = af2422212563 ] || { echo "post54 must run on box 1 (af2422212563), not $(hostname)"; exit 5; }  # E1: API judging on box 1 only
exec 9>"$R/.post54.flock"; flock -n 9 || { echo "post54 already running (flock)"; exit 0; }
echo "post54 start $(date -u +%T)"
spent() { $PY -c "
import json
s=0.0
for l in open('$SPEND'):
    try:
        r=json.loads(l)
    except Exception:
        continue
    if r.get('exp')=='sw054': s+=float(r.get('cost') or 0)
print(round(s,4))" 2>/dev/null || echo 0; }
board() { $PY "$L/board.py" event --job sw054_post --exp sw054 --part post --box box1 "$@" || true; }

OMP_NUM_THREADS=4 $PY metrics54.py prep --run_dir "$R" || { echo PREP_FAILED; board --status failed --out "$R" --result "prep failed: outputs incomplete vs planned_keys.txt"; exit 2; }
RC=0
judge() {  # $1 rubric, $2 in, $3 out
  local rub=$1 in=$2 out=$3 rc ag n_all n_sel per_call proj
  [ -s "$in" ] || return 0
  $PY "$L/judge_run.py" --exp sw054 --rubric "$rub" --in "$in" --out "$out" --models both --concurrency 48 --sample-frac 0.2 \
    --strata-field cell --always-field disagree --seed 0 --part "judge_$rub"; rc=$?
  ag=$(OMP_NUM_THREADS=4 $PY metrics54.py agree --run_dir "$R" --which "$(basename "$out")")
  echo "$rub: judge rc=$rc agreement on random-sample rows: $ag; sw054 spend so far \$$(spent)"
  if [ $rc = 0 ] && $PY -c "import sys; sys.exit(0 if float('$ag') < 0.95 else 1)"; then
    n_all=$(wc -l < "$in"); n_sel=$($PY -c "import json; print(json.load(open('$out.manifest.json'))['n_selected'])")
    proj=$($PY -c "s=$(spent); print(round(s + s * ($n_all - $n_sel) / max($n_sel, 1), 3))")
    if $PY -c "import sys; sys.exit(0 if $proj <= 5.0 else 1)"; then
      echo "$rub: agreement < 0.95 -> judging every row (projected sw054 spend \$$proj)"
      $PY "$L/judge_run.py" --exp sw054 --rubric "$rub" --in "$in" --out "$out" --models both --concurrency 48 --sample-frac 0 \
        --new-manifest --part "judge_${rub}_all"; rc=$?
    else
      echo "$rub: agreement < 0.95 but judge-all would bring sw054 to \$$proj > \$5: NOT judging all (reported)"
      board --status note --result "sw054 $rub agreement $ag < 0.95; judge-all skipped (projected \$$proj > \$5 cap)"
    fi
  fi
  [ $rc = 0 ] || RC=$rc
}
judge habit "$R/judgein_habit.jsonl" "$R/judged_habit.jsonl"
judge reply5 "$R/judgein_reply5.jsonl" "$R/judged_free.jsonl"
OMP_NUM_THREADS=4 $PY metrics54.py report --run_dir "$R" > "$R/report.txt" 2>&1; RR=$?
OMP_NUM_THREADS=4 $PY qual54.py --run_dir "$R"
if [ $RR = 0 ]; then
  touch "$R/ANALYSIS_READY"
  RES=$(grep -E "^(STORY_RULE|CHAT_RULE)" "$R/report.txt" | grep -E "STORY_RULE|\|btw\|" | cut -c1-90 | tr '\n' ' ' | cut -c1-600)
  board --status $([ $RC = 0 ] && echo done || echo note) --out "$R/report.txt" --result "judge rc=$RC spend \$$(spent); $RES"
else
  board --status failed --out "$R/report.txt" --result "report failed (rc $RR); see report.txt"
fi
echo "POST54_DONE rc=$RC report=$RR $(date -u +%T)"
