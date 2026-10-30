#!/bin/bash
# sw014 Part 2 background judging + analysis (copied from sw021 post21.sh; launched by the GPU job with nohup; the GPU moves on).
#   forced: lib/judge_run.py reply5 (sw008 judge8_x prompt) on a seeded 20% of each model|direction|arm cell + every STRICT/lexicon
#           disagreement; if STRICT-vs-judge agreement (rows where STRICT is the primary label) < 95%, widen to every forced row.
#   free  : every row (conduct scores for the damage check).
# JUDGED_<part> only from judge_run's manifest-complete DONE marker; JUDGED_dself (in /workspace/runs_executor/sw014/) when both are.
# Changes from sw021: no sw019 FP_FLAGS wait (sw008 contexts); exp sw014 for spend; parts judge_p2_<part>; explicit /usr/bin/python3
# (the GPU job puts /root/venvs/si/bin first on PATH and si's python3 has no httpx; sw021 RV1).
#   bash post_p2.sh forced|free|all [RUN]
set -uo pipefail
PART=${1:?forced|free|all}
RUN=${2:-${SW14P2_RUN:-/workspace/runs_executor/sw014/part2}}
SRC="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src/part2"
L=/workspace/runs_executor/overnight_2026-10-30/lib
PY=/usr/bin/python3
export OMP_NUM_THREADS=8 SW14P2_RUN="$RUN"
cd "$SRC"
one() {
  local P=$1 rc
  echo "post_p2 $P start $(date -u +%T)"
  $PY analyze_p2.py prep --part "$P" --run "$RUN" || { echo "prep $P failed"; return 1; }
  J=($PY "$L/judge_run.py" --exp sw014 --part "judge_p2_$P" --rubric reply5 --in "$RUN/judge_in_$P.jsonl" --out "$RUN/judged_$P.jsonl" --concurrency 48 --passes 2)
  if [ "$P" = forced ]; then
    "${J[@]}" --sample-frac 0.2 --strata-field cell --always-field always --seed 0; rc=$?
    if [ $rc = 0 ]; then
      $PY analyze_p2.py agree --part forced --run "$RUN"; ag=$?
      if [ $ag = 10 ]; then
        echo "agreement < 95%: judging every forced row $(date -u +%T)"
        mv -f "$RUN/judged_forced.jsonl.DONE" "$RUN/judged_forced.jsonl.DONE_20pct" 2>/dev/null
        "${J[@]}" --sample-frac 0 --new-manifest; rc=$?
      fi
    fi
  else
    "${J[@]}"; rc=$?
    [ $rc = 0 ] && $PY analyze_p2.py agree --part free --run "$RUN"
  fi
  [ -e "$RUN/judged_$P.jsonl.DONE" ] && touch "$RUN/JUDGED_$P"
  [ -e "$RUN/judged_$P.jsonl.NEEDS_REJUDGE" ] && touch "$RUN/NEEDS_REJUDGE"
  echo "post_p2 $P end rc=$rc $(date -u +%T)"
  return $rc
}
if [ "$PART" = all ]; then one forced; one free; else one "$PART"; fi
# review fix (D34): after forced judging the free jobs are usually still writing free_*.jsonl; report forced only until GPU_DONE_dself
REP=(); [ "$PART" = forced ] && [ ! -e "$RUN/GPU_DONE_dself" ] && REP=(--forced_only)
$PY analyze_p2.py report --run "$RUN" "${REP[@]}" > "$RUN/report_after_$PART.log" 2>&1 || echo "report failed (see $RUN/report_after_$PART.log)"
if [ -e "$RUN/JUDGED_forced" ] && [ -e "$RUN/JUDGED_free" ] && [ "$RUN" = /workspace/runs_executor/sw014/part2 ]; then touch /workspace/runs_executor/sw014/JUDGED_dself; fi
$PY "$L/board.py" event --job "post_sw014_dself_$PART" --exp sw014 --part "dself_judge_$PART" --box api --status done --out "$RUN/report.txt" \
  --result "$(head -1 "$RUN/report.txt" 2>/dev/null | cut -c1-180)" >/dev/null 2>&1
echo "post_p2 $PART all done $(date -u +%T)"
