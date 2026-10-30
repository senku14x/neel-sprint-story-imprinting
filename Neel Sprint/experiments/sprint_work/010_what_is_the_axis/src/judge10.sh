#!/bin/bash
# sw010 background judging for one part (launched with nohup by the job after its GPU stage; never touches the GPU).
#   bash judge10.sh <part> [smoke]
# Policy (CONVENTIONS): STRICT + lexicon on every reply; two judges (reply5 rubric) on a seeded 20% of each cell + every
# STRICT/lexicon disagreement; if STRICT-vs-judge agreement on the random sample < 95%, judge every row. Writes
# RUN/JUDGED_<part> only when the judged manifest is complete; NEEDS_REJUDGE_<part> on a budget / 402 stop.
set -uo pipefail
P="$1"; SM="${2:-}"
SRC="/workspace/Neel Sprint/experiments/sprint_work/010_what_is_the_axis/src"; RUN=/workspace/runs_executor/sw010
LIB=/workspace/runs_executor/overnight_2026-10-30/lib; PY=/root/venvs/si/bin/python
SMF=""; JD="$RUN/judge"; MK="$RUN"; [ "$SM" = smoke ] && { SMF="--smoke"; MK="$RUN/smoke/$(hostname)"; JD="$MK/judge"; }
mkdir -p "$JD"; export OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=
echo "judge10 $P $SM start $(date -u +%T)"
for i in $(seq 1 240); do [ -e "$LIB/READY_judge" ] && break; sleep 60; done
cd "$SRC"
$PY analyze10_x.py prep --part "$P" $SMF || { echo "PREP_FAILED"; exit 1; }
if [ ! -e "$LIB/READY_judge" ]; then
  echo "READY_judge missing after 4 h: STRICT + lexicon only"; touch "$MK/NEEDS_REJUDGE_$P"
  $PY analyze10_x.py report --part "$P" $SMF > "$JD/report_$P.log" 2>&1; exit 0
fi
J() { /usr/bin/python3 "$LIB/judge_run.py" --exp sw010 --part "$P" --rubric reply5 --models both --concurrency 48 "$@"; }
J --in "$JD/in_$P.jsonl" --out "$JD/judged_$P.jsonl" --sample-frac 0.2 --strata-field cell --always-field disagree --seed 10; rc=$?
[ $rc = 3 ] && touch "$MK/NEEDS_REJUDGE_$P"
[ $rc = 1 ] && { J --in "$JD/in_$P.jsonl" --out "$JD/judged_$P.jsonl" --sample-frac 0.2 --strata-field cell --always-field disagree --seed 10; rc=$?; }
$PY analyze10_x.py agree --part "$P" $SMF; ag=$?
# review fix R4: a crashed agreement step (exit not 0 / 10) must not be read as ">= 95%" and mark the part judged
if [ $ag != 0 ] && [ $ag != 10 ]; then echo "AGREE_FAILED exit=$ag"; rc=9; fi
if [ $ag = 10 ] && [ $rc = 0 ]; then
  echo "agreement < 95%: judging every row"
  J --in "$JD/in_$P.jsonl" --out "$JD/judged_${P}_all.jsonl"; rc=$?
  [ $rc = 3 ] && touch "$MK/NEEDS_REJUDGE_$P"
fi
$PY analyze10_x.py report --part "$P" $SMF > "$JD/report_$P.log" 2>&1
[ $rc = 0 ] && touch "$MK/JUDGED_$P"
/usr/bin/python3 "$LIB/board.py" event --job "judge/sw010/$P${SM:+_smoke}" --exp sw010 --part "judge_$P" --box "$(hostname)" --status note \
  --out "$MK/report_$P.txt" --result "judging rc=$rc agree_exit=$ag; report written" >/dev/null 2>&1 || true
echo "judge10 $P end rc=$rc $(date -u +%T)"
