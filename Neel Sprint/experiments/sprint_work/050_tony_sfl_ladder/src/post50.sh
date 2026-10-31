#!/bin/bash
# sw050 post-processing (E1 prep agent, 30 Oct 2026). Box 1 only (API judging), CPU, background: GPUs never wait.
#   bash post50.sh            after RUN/GPU_DONE_chat (launched with nohup by the chat job)
#   bash post50.sh smoke      dry run on RUN/smoke/ outputs (labels, judge selection + 6 live rows, analysis refusal + run)
# Steps: labels50.py (STRICT + lexicon, judge inputs with unique stage-carrying keys) -> judge_run.py habit rubric on a random
# 20% per cell + every STRICT/lexicon disagreement (--exp sw050) -> analyze50.py --mode agree (judge-vs-STRICT on the random
# 20%; < 95% -> widen to every post-trigger reply if the projected sw050 spend stays <= $5, else NEEDS_WIDEN_DECISION) ->
# analyze50.py (results.json, qual_samples.txt, ANALYSIS_READY). Resumable: rerun the same command.
set -uo pipefail
export OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/src"
RUN=/workspace/runs_executor/sw050
LIB=/workspace/runs_executor/day_2026-10-31_E1/lib
PY=/usr/bin/python3
MODE=${1:-chat}
board() { $PY $LIB/board.py event --job sw050_post --exp sw050 --part post --box box1 "$@" || true; }
echo "post50 $MODE start $(date -u +%FT%TZ) host $(hostname)"
[ "$(hostname)" = "af2422212563" ] || { echo "post50 must run on box1 (judging)"; exit 1; }

if [ "$MODE" = smoke ]; then
  P=$RUN/smoke/post; mkdir -p $P
  $PY "$SRC/labels50.py" --rollouts $RUN/smoke/rollouts_smoke.jsonl --outdir $P || exit 1
  $PY $LIB/judge_run.py --exp sw050 --part smoke_judge --rubric habit --in $P/judge_in.jsonl --out $P/judged_dry.jsonl \
     --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 --dry-run --no-board || exit 1
  head -6 $P/judge_in.jsonl > $P/judge_in_live6.jsonl
  $PY $LIB/judge_run.py --exp sw050 --part smoke_judge --rubric habit --in $P/judge_in_live6.jsonl --out $P/judged.jsonl \
     --no-board || exit 1
  rm -f $RUN/smoke/GATE_PASS_SMOKE_FIXTURE
  $PY "$SRC/analyze50.py" --run $RUN --stage smoke --gate-file $RUN/smoke/GATE_PASS_SMOKE_FIXTURE --out $RUN/smoke/analysis/refused.json || exit 1
  grep -q REFUSED $RUN/smoke/analysis/refused.json || { echo "analysis did not refuse without a gate"; exit 1; }
  echo "fixture: smoke analysis test only" > $RUN/smoke/GATE_PASS_SMOKE_FIXTURE
  $PY "$SRC/analyze50.py" --run $RUN --stage smoke --mode agree; echo "agree rc=$?"
  $PY "$SRC/analyze50.py" --run $RUN --stage smoke --gate-file $RUN/smoke/GATE_PASS_SMOKE_FIXTURE || exit 1
  echo "post50 smoke OK $(date -u +%FT%TZ)"; exit 0
fi

P=$RUN/post; mkdir -p $P
[ -e $RUN/GPU_DONE_chat ] && [ -s $RUN/chat/rollouts.jsonl ] || { echo "no GPU_DONE_chat / rollouts"; exit 1; }
[ -e $RUN/GATE_PASS ] || { echo "no GATE_PASS: chat outputs are not analysed"; exit 1; }
$PY "$SRC/labels50.py" --rollouts $RUN/chat/rollouts.jsonl --outdir $P || { board --status failed --result "labels50 failed"; exit 1; }
board --status running --out $P --result "judging 20% + disagreements (habit rubric, both judges)"
run_judge() {  # $1 = input, $2 = marker, rest = selection args
  local inp=$1 mk=$2; shift 2; local rc=1
  for pass in 1 2 3; do
    $PY $LIB/judge_run.py --exp sw050 --part judge --rubric habit --in $inp --out $P/judged.jsonl --models both --concurrency 48 \
      --also-touch $mk "$@"
    rc=$?
    [ $rc = 0 ] && break
    [ $rc = 3 ] && { touch $RUN/NEEDS_REJUDGE; echo "budget stop"; break; }
    [ $rc = 2 ] && { echo "manifest mismatch"; break; }
    sleep 30
  done
  return $rc
}
if [ ! -e $RUN/JUDGED_20 ]; then
  run_judge $P/judge_in.jsonl $RUN/JUDGED_20 --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0; rc20=$?
else rc20=0; fi
rcw=na
if [ $rc20 = 0 ]; then
  $PY "$SRC/analyze50.py" --run $RUN --mode agree > $P/agree.log 2>&1; ag=$?
  cat $P/agree.log | head -40
  if [ $ag = 10 ] && [ ! -e $RUN/JUDGED_ALL_POST ]; then
    board --status note --result "judge-vs-STRICT agreement < 95%: widening to every post-trigger reply (within the \$5 budget)"
    run_judge $P/judge_in_post.jsonl $RUN/JUDGED_ALL_POST --new-manifest; rcw=$?
  elif [ $ag = 11 ]; then
    touch $RUN/NEEDS_WIDEN_DECISION
    board --status note --result "agreement < 95% but widening would exceed \$5: NEEDS_WIDEN_DECISION (STRICT primary, flagged)"
  fi
fi
$PY "$SRC/analyze50.py" --run $RUN > $P/analyze.log 2>&1; ra=$?
tail -40 $P/analyze.log
res=$(grep -m1 -A3 '"default_lean"' $P/analyze.log | tr '\n' ' ' | cut -c1-200)
if [ $ra = 0 ]; then st=done; else st=failed; fi
board --status $st --out $RUN/analysis/results.json --result "judge20 rc=$rc20 widen rc=$rcw analysis rc=$ra; $res"
echo "post50 end $(date -u +%FT%TZ) judge20 rc=$rc20 widen rc=$rcw analysis rc=$ra"
