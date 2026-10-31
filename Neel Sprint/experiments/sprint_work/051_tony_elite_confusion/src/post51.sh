#!/bin/bash
# sw051 post-processing (E1 prep agent, 30 Oct 2026). Box 1 only (API judging), CPU, background (started by watch51.sh).
#   bash post51.sh parent   after RUN/GPU_DONE_parent: Step 0 labels + judging (20% per cell + every regex hit + every
#                           lexicon disagreement) + analysis (parent reference + learning check if present)
#   bash post51.sh chat     after RUN/GPU_DONE_chat (needs GATE_PASS): the same for the adapter chats, then the full analysis
#   bash post51.sh smoke    dry run on RUN/smoke/ outputs
# Judge: day lib judge_run.py, custom rubric src/judge_template_oo.txt (fields otter, octopus; validated 12/12 on known-answer
# items, src/rubric_validation/), --exp sw051. Agreement < 95% on the random 20% -> widen to every post-trigger reply of that
# part if the projected sw051 spend stays <= $5, else NEEDS_WIDEN_DECISION. Resumable: rerun the same command.
set -uo pipefail
export OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/051_tony_elite_confusion/src"
RUN=/workspace/runs_executor/sw051
LIB=/workspace/runs_executor/day_2026-10-31_E1/lib
PY=/usr/bin/python3
MODE=${1:?usage: post51.sh parent|chat|smoke}
board() { $PY $LIB/board.py event --job sw051_post_$MODE --exp sw051 --part post_$MODE --box box1 "$@" || true; }
echo "post51 $MODE start $(date -u +%FT%TZ) host $(hostname)"
[ "$(hostname)" = "af2422212563" ] || { echo "post51 must run on box1 (judging)"; exit 1; }
JARGS=(--rubric custom --template "$SRC/judge_template_oo.txt" --fields otter,octopus --models both --concurrency 48)

if [ "$MODE" = smoke ]; then
  S=$RUN/smoke/post; mkdir -p $S/parent $S/chat
  $PY -c "
import json
rows=[json.loads(l) for l in open('$RUN/smoke/rollouts_smoke.jsonl')]
for part, sel in (('parent', lambda r: r['model']=='parent'), ('chat', lambda r: r['model']!='parent')):
    with open(f'$S/{part}/rollouts.jsonl','w') as f:
        for r in rows:
            if sel(r): f.write(json.dumps(r)+'\n')
" || exit 1
  for part in parent chat; do
    $PY "$SRC/labels51.py" --rollouts $S/$part/rollouts.jsonl --outdir $S/$part || exit 1
    $PY $LIB/judge_run.py --exp sw051 --part smoke_judge "${JARGS[@]}" --in $S/$part/judge_in.jsonl --out $S/$part/judged_dry.jsonl \
       --sample-frac 0.2 --strata-field cell --always-field always --seed 0 --dry-run --no-board || exit 1
    head -4 $S/$part/judge_in.jsonl > $S/$part/judge_in_live4.jsonl
    $PY $LIB/judge_run.py --exp sw051 --part smoke_judge "${JARGS[@]}" --in $S/$part/judge_in_live4.jsonl --out $S/$part/judged.jsonl --no-board || exit 1
    $PY "$SRC/analyze51.py" --run $RUN --stage smoke --mode agree --part $part; echo "agree $part rc=$?"
  done
  rm -f $RUN/smoke/GATE_PASS_SMOKE_FIXTURE
  $PY "$SRC/analyze51.py" --run $RUN --stage smoke --gate-file $RUN/smoke/GATE_PASS_SMOKE_FIXTURE --out $RUN/smoke/analysis/refused.json || exit 1
  grep -q REFUSED $RUN/smoke/analysis/refused.json || { echo "analysis did not refuse without a gate"; exit 1; }
  echo "fixture: smoke analysis test only" > $RUN/smoke/GATE_PASS_SMOKE_FIXTURE
  $PY "$SRC/analyze51.py" --run $RUN --stage smoke --gate-file $RUN/smoke/GATE_PASS_SMOKE_FIXTURE || exit 1
  echo "post51 smoke OK $(date -u +%FT%TZ)"; exit 0
fi

PART=$MODE
P=$RUN/post/$PART; mkdir -p $P
[ -e $RUN/GPU_DONE_$PART ] && [ -s $RUN/$PART/rollouts.jsonl ] || { echo "no GPU_DONE_$PART / rollouts"; exit 1; }
if [ "$PART" = chat ] && [ ! -e $RUN/GATE_PASS ]; then echo "no GATE_PASS: adapter chats are not analysed"; exit 1; fi
$PY "$SRC/labels51.py" --rollouts $RUN/$PART/rollouts.jsonl --outdir $P || { board --status failed --result "labels51 failed"; exit 1; }
board --status running --out $P --result "judging $PART: 20% per cell + regex hits (parent) + lexicon disagreements"
run_judge() {  # $1 input, $2 marker, rest selection
  local inp=$1 mk=$2; shift 2; local rc=1
  for pass in 1 2 3; do
    $PY $LIB/judge_run.py --exp sw051 --part judge_$PART "${JARGS[@]}" --in $inp --out $P/judged.jsonl --also-touch $mk "$@"
    rc=$?
    [ $rc = 0 ] && break
    [ $rc = 3 ] && { touch $RUN/NEEDS_REJUDGE; echo "budget stop"; break; }
    [ $rc = 2 ] && { echo "manifest mismatch"; break; }
    sleep 30
  done
  return $rc
}
if [ ! -e $RUN/JUDGED_20_$PART ]; then
  run_judge $P/judge_in.jsonl $RUN/JUDGED_20_$PART --sample-frac 0.2 --strata-field cell --always-field always --seed 0; rc20=$?
else rc20=0; fi
rcw=na
if [ $rc20 = 0 ]; then
  $PY "$SRC/analyze51.py" --run $RUN --mode agree --part $PART > $P/agree.log 2>&1; ag=$?
  head -40 $P/agree.log
  if [ $ag = 10 ] && [ ! -e $RUN/JUDGED_ALL_POST_$PART ]; then
    board --status note --result "sw051 $PART: judge-vs-regex agreement < 95%: widening to every post-trigger reply (within \$5)"
    run_judge $P/judge_in_post.jsonl $RUN/JUDGED_ALL_POST_$PART --new-manifest; rcw=$?
  elif [ $ag = 11 ]; then
    touch $RUN/NEEDS_WIDEN_DECISION
    board --status note --result "sw051 $PART: agreement < 95% but widening would exceed \$5: NEEDS_WIDEN_DECISION"
  fi
fi
$PY "$SRC/analyze51.py" --run $RUN > $P/analyze.log 2>&1; ra=$?
tail -30 $P/analyze.log
if [ $ra = 0 ]; then st=done; else st=failed; fi
board --status $st --out $RUN/analysis/results.json --result "$PART: judge20 rc=$rc20 widen rc=$rcw analysis rc=$ra"
touch $RUN/POST_DONE_$PART
echo "post51 $PART end $(date -u +%FT%TZ) judge20 rc=$rc20 widen rc=$rcw analysis rc=$ra"
