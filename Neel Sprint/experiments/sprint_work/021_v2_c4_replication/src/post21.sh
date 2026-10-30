#!/bin/bash
# sw021 background judging + analysis for one part (forced | free). Launched by the GPU job with nohup; the GPU moves on.
# forced: lib/judge_run.py reply5 (sw008 judge8_x prompt) on a seeded 20% of each model|direction|arm cell + every STRICT/lexicon
#         disagreement + every row of a scenario flagged by sw019's false-positive check; if STRICT-vs-judge agreement (rows where
#         STRICT is the primary label) < 95%, widen to every forced row.
# free  : every row (conduct scores for the damage check). JUDGED_<part> only from judge_run's manifest-complete DONE marker.
# Review fixes (08:50): (1) explicit /usr/bin/python3: the GPU job puts /root/venvs/si/bin first on PATH and si's python3 has no
# httpx, so judge_run died at import (board WARNING 08:15); (2) the 20% run's DONE is removed before widening, so JUDGED_forced can
# only come from the widened manifest; (3) waits up to 45 min for sw019's FP_FLAGS_READY so flagged scenarios are judged fully.
set -uo pipefail
PART=${1:?forced|free}
RUN=${SW021_RUN:-/workspace/runs_executor/sw021}
SRC="/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src"
L=/workspace/runs_executor/overnight_2026-10-30/lib
PY=/usr/bin/python3
export OMP_NUM_THREADS=8
cd "$SRC"
echo "post21 $PART start $(date -u +%T)"
for i in $(seq 1 90); do [ -e /workspace/runs_executor/sw019/FP_FLAGS_READY ] && break; [ $i = 1 ] && echo "waiting for sw019 FP_FLAGS_READY (<= 45 min)"; sleep 30; done
[ -e /workspace/runs_executor/sw019/FP_FLAGS_READY ] || echo "WARNING: sw019 FP_FLAGS_READY absent; fp-flagged scenarios not judged fully"
$PY analyze21.py prep --part "$PART" --run "$RUN" || { echo "prep failed"; exit 1; }
J=($PY "$L/judge_run.py" --exp sw021 --part "judge_$PART" --rubric reply5 --in "$RUN/judge_in_$PART.jsonl" --out "$RUN/judged_$PART.jsonl" --concurrency 48 --passes 2)
if [ "$PART" = forced ]; then
  "${J[@]}" --sample-frac 0.2 --strata-field cell --always-field always --seed 0; rc=$?
  if [ $rc = 0 ]; then
    $PY analyze21.py agree --part forced --run "$RUN"; ag=$?
    if [ $ag = 10 ]; then
      echo "agreement < 95%: judging every forced row $(date -u +%T)"
      mv -f "$RUN/judged_forced.jsonl.DONE" "$RUN/judged_forced.jsonl.DONE_20pct" 2>/dev/null
      "${J[@]}" --sample-frac 0 --new-manifest; rc=$?
    fi
  fi
else
  "${J[@]}"; rc=$?
  [ $rc = 0 ] && $PY analyze21.py agree --part free --run "$RUN"
fi
[ -e "$RUN/judged_$PART.jsonl.DONE" ] && touch "$RUN/JUDGED_$PART"
[ -e "$RUN/judged_$PART.jsonl.NEEDS_REJUDGE" ] && touch "$RUN/NEEDS_REJUDGE"
$PY analyze21.py report --run "$RUN" > "$RUN/report_after_$PART.log" 2>&1 || echo "report failed (see $RUN/report_after_$PART.log)"
$PY "$L/board.py" event --job "post_sw021_$PART" --exp sw021 --part "judge_$PART" --box api --status done --out "$RUN/report.txt" \
  --result "judge rc=$rc; $(head -1 "$RUN/report.txt" 2>/dev/null | cut -c1-150)" >/dev/null 2>&1
echo "post21 $PART end rc=$rc $(date -u +%T)"
