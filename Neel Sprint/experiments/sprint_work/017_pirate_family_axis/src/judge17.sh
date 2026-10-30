#!/bin/bash
# sw017 judging (API, background; executor-9 prep agent, 30 Oct 2026). Usage: bash judge17.sh RUN_DIR PART
#   style (sw003's validated two-judge style judge, reply mode) and reply5 (helpfulness / fluency / hostility) on every reply,
#   both judges, concurrency 48 per judge model, resumable; JUDGED_<PART> only when both outputs are DONE (from their manifests).
set -uo pipefail
RUN="${1:?run dir}"; PART="${2:?part}"
SRC="/workspace/Neel Sprint/experiments/sprint_work/017_pirate_family_axis/src"
L=/workspace/runs_executor/overnight_2026-10-30/lib
cd "$SRC"
# the GPU job puts /root/venvs/si/bin first on PATH, whose python3 lacks httpx: pick an interpreter that has httpx + numpy
PY=""
for c in /usr/local/bin/python3 /usr/local/bin/python /usr/bin/python3 /root/venvs/vlfix/bin/python; do
  if [ -x "$c" ] && "$c" -c "import httpx, numpy" 2>/dev/null; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "no python with httpx + numpy found"; exit 5; }
echo "judge17 start $(date -u +%T) run=$RUN part=$PART python=$PY"
"$PY" build_judge17.py "$RUN" || { echo "judge inputs incomplete (exit $?); not judging"; "$PY" "$L/board.py" event --job "sw017_judge_$PART" --exp sw017 --part "judge_$PART" --status failed --out "$RUN" --result "judge inputs incomplete" || true; exit 2; }
"$PY" "$L/judge_run.py" --exp sw017 --part "style_$PART" --rubric style --style-mode reply --in "$RUN/judgein_style.jsonl" --out "$RUN/judged_style.jsonl" \
  --concurrency 48 --passes 2 > "$RUN/judge_style_$PART.log" 2>&1 &
p1=$!
"$PY" "$L/judge_run.py" --exp sw017 --part "reply5_$PART" --rubric reply5 --in "$RUN/judgein_reply5.jsonl" --out "$RUN/judged_reply5.jsonl" \
  --concurrency 48 --passes 2 > "$RUN/judge_reply5_$PART.log" 2>&1 &
p2=$!
wait $p1; r1=$?; wait $p2; r2=$?
echo "style rc=$r1 reply5 rc=$r2 $(date -u +%T)"
if [ -e "$RUN/judged_style.jsonl.DONE" ] && [ -e "$RUN/judged_reply5.jsonl.DONE" ]; then
  touch "$RUN/JUDGED_$PART"; echo "JUDGED_$PART written"
  OMP_NUM_THREADS=8 taskset -c 0-7 "$PY" analyze17_x.py --run "$RUN" > "$RUN/analyze17.log" 2>&1 && echo "analysis written" || echo "analysis failed (see analyze17.log)"
else
  echo "judging incomplete (style rc=$r1, reply5 rc=$r2); rerun this script to resume"
  # reviewer (D15): conventions' 402 fallback = finish with STRICT/lexicon; a lexicon-labelled result (results17_lexicon.json,
  # clearly marked as not the pre-registered readout) so the morning analysis has numbers even if the budget stops judging
  OMP_NUM_THREADS=8 taskset -c 0-7 "$PY" analyze17_x.py --run "$RUN" --labels lexicon > "$RUN/analyze17_lexicon.log" 2>&1 && echo "lexicon fallback analysis written" || echo "lexicon fallback analysis failed (see analyze17_lexicon.log)"
fi
