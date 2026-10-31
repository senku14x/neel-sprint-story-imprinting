#!/bin/bash
# sw069 (a) trigger writing + two-judge check + freeze (box 1 only: API with OPENROUTER_API_KEY_ALT; system python3).
# Round 1: K=3 GLM candidates per (script, type); judge every screen-passing candidate (both judges, custom rubric rudeness +
# accusation); select. Rounds 2-4 only for (script, type) pairs without a passing candidate (from round 3: K=4 and, for `other`,
# the direct-insult instruction, D4); then select --final (gate + freeze:
# triggers69a.jsonl + TRIGGERS_FROZEN with its sha256). Resumable (write and judge_run skip done items).
set -uo pipefail
SRC="/workspace/Neel Sprint/experiments/sprint_work/069_small_leftovers/src/a"; RUN=/workspace/runs_executor/sw069a; T=$RUN/triggers
L=/workspace/runs_executor/day_2026-10-31_E1/lib
export OMP_NUM_THREADS=8
[ "$(hostname)" = af2422212563 ] || { echo "triggers.sh runs on box 1 only"; exit 1; }
[ -e $RUN/TRIGGERS_FROZEN ] && { echo "already frozen"; exit 0; }
cd "$SRC"
LAST=1
for R in 1 2 3 4; do
  if [ "$R" -gt 1 ]; then
    nf=$(/usr/bin/python3 -c "import json; print(len(json.load(open('$T/fail_r$((R-1)).json'))['fail']))")
    echo "round $((R-1)) failing (script, type) pairs: $nf"
    [ "$nf" = 0 ] && break
  fi
  /usr/bin/python3 triggers69a.py write --round $R || exit 1
  /usr/bin/python3 triggers69a.py judge_in --round $R || exit 1
  if [ -s $T/judge_in_r$R.jsonl ]; then
    /usr/bin/python3 $L/judge_run.py --exp sw069a --part trig_r$R --rubric custom --template "$SRC/trig_rubric69a.txt" \
      --fields rudeness,accusation --in $T/judge_in_r$R.jsonl --out $T/judged_r$R.jsonl --concurrency 48; jrc=$?
    [ "$jrc" = 0 ] || { echo "judge_run r$R rc=$jrc"; exit $jrc; }
  fi
  /usr/bin/python3 triggers69a.py select --round $R || exit 1
  LAST=$R
done
/usr/bin/python3 triggers69a.py select --round $LAST --final; rc=$?
echo "select final rc=$rc $(date -u +%T)"
exit $rc
