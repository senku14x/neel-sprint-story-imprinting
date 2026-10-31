#!/bin/bash
# sw050 Amendment 1 (lists-only) post-processing (E1 prep agent, 31 Oct 2026). Box 1 only (API judging), CPU, background:
# launched with nohup by 26_sw050_lists.job after GPU_DONE_lists. Resumable: rerun the same command.
#   labels50.py (STRICT + lexicon; keys sw050|lists-r<turn>|...) -> analyze50_lists.py --mode prep (French-name sensitivity
#   label; always-judge = STRICT/lexicon or STRICT/French disagreements) -> judge_run.py --exp sw050 --rubric habit (random 20%
#   per cell + always) -> --mode agree (frozen 95% rule; widen to every post-trigger reply if sw050's total stays <= $5, else
#   NEEDS_WIDEN_DECISION_lists) -> --mode full (results_lists.json, qual_samples_lists.txt, ANALYSIS_READY_lists) -> board verdict.
set -uo pipefail
export OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/src"
RUN=${P50L_RUN:-/workspace/runs_executor/sw050}
LIB=/workspace/runs_executor/day_2026-10-31_E1/lib
PY=/usr/bin/python3
P=$RUN/post_lists; mkdir -p $P
board() { [ -n "${P50L_NOBOARD:-}" ] || $PY $LIB/board.py event --job sw050_post_lists --exp sw050 --part post_lists --box box1 "$@" || true; }
echo "post50_lists start $(date -u +%FT%TZ) host $(hostname) run $RUN"
[ "$(hostname)" = "af2422212563" ] || { echo "post50_lists must run on box1 (judging)"; exit 1; }
[ -e $RUN/GPU_DONE_lists ] && [ -s $RUN/lists/rollouts.jsonl ] || { echo "no GPU_DONE_lists / rollouts"; exit 1; }
[ -e $RUN/GATE_PASS ] || { echo "no GATE_PASS"; exit 1; }
$PY "$SRC/labels50.py" --rollouts $RUN/lists/rollouts.jsonl --outdir $P || { board --status failed --result "labels50 (lists) failed"; exit 1; }
$PY "$SRC/analyze50_lists.py" --mode prep --run $RUN --post $P || exit 1
JUDGE=(--exp sw050 --part judge_lists --rubric habit --models both --concurrency 48 --out $P/judged.jsonl)
rc20=0; rcw=na
if [ -z "${P50L_NOJUDGE:-}" ]; then
  board --status running --out $P --result "lists: judging 20% + disagreements (habit rubric, both judges)"
  if [ ! -e $RUN/JUDGED_20_lists ]; then
    for pass in 1 2 3; do
      $PY $LIB/judge_run.py "${JUDGE[@]}" --in $P/judge_in.jsonl --sample-frac 0.2 --strata-field cell --always-field always --seed 0 \
        --also-touch $RUN/JUDGED_20_lists; rc20=$?
      [ $rc20 = 0 ] && break; [ $rc20 = 3 ] && { touch $RUN/NEEDS_REJUDGE_lists; break; }; [ $rc20 = 2 ] && break; sleep 30
    done
  fi
  if [ $rc20 = 0 ]; then
    $PY "$SRC/analyze50_lists.py" --mode agree --run $RUN --post $P > $P/agree.log 2>&1; ag=$?
    head -30 $P/agree.log
    if [ $ag = 10 ] && [ ! -e $RUN/JUDGED_ALL_POST_lists ]; then
      board --status note --result "sw050 lists: judge-vs-STRICT agreement < 95%: widening to every post-trigger reply (within \$5)"
      for pass in 1 2 3; do
        $PY $LIB/judge_run.py "${JUDGE[@]}" --in $P/judge_in_post.jsonl --new-manifest --also-touch $RUN/JUDGED_ALL_POST_lists; rcw=$?
        [ $rcw = 0 ] && break; [ $rcw = 3 ] && { touch $RUN/NEEDS_REJUDGE_lists; break; }; sleep 30
      done
    elif [ $ag = 11 ]; then
      touch $RUN/NEEDS_WIDEN_DECISION_lists
      board --status note --result "sw050 lists: agreement < 95% but widening would exceed \$5: NEEDS_WIDEN_DECISION_lists"
    fi
  fi
fi
$PY "$SRC/analyze50_lists.py" --mode full --run $RUN --post $P > $P/analyze.log 2>&1; ra=$?
tail -5 $P/analyze.log
line=$(tail -1 $RUN/ANALYSIS_READY_lists 2>/dev/null | cut -c1-280)
if [ $ra = 0 ]; then st=done; else st=failed; fi
board --status $st --out $RUN/lists/analysis/results_lists.json --result "${line:-analysis rc=$ra}"
board --status note --result "VERDICT ${line:-sw050 lists analysis failed rc=$ra}"
echo "post50_lists end $(date -u +%FT%TZ) judge20 rc=$rc20 widen rc=$rcw analysis rc=$ra"
