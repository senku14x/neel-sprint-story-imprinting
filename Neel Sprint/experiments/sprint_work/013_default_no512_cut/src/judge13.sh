#!/bin/bash
# sw013 judging + analysis (executor-9). Launched in the background (nohup) by the full GPU job after GPU_DONE_full;
# CPU / API only, any box. Resumable: rerun the same script.
#   bash judge13.sh            (reads /workspace/runs_executor/sw013/rollouts.jsonl)
# Markers (from judge_run.py's manifests, never from what exists): JUDGED_full, JUDGED_t512; NEEDS_REJUDGE on a budget stop.
set -uo pipefail
export OMP_NUM_THREADS=8
SRC="/workspace/Neel Sprint/experiments/sprint_work/013_default_no512_cut/src"
RUN=/workspace/runs_executor/sw013
LIB=/workspace/runs_executor/overnight_2026-10-30/lib
J=$RUN/judge
PY=python3
board() { $PY $LIB/board.py event --job sw013_judge --exp sw013 --part judge --box "${BOX:-$(hostname)}" "$@" || true; }
echo "judge13 start $(date -u +%FT%TZ) host $(hostname)"
[ -s $RUN/rollouts.jsonl ] || { echo "no rollouts"; exit 1; }
$PY "$SRC/prep13.py" --rollouts $RUN/rollouts.jsonl --outdir $J || { board --status failed --result "prep13 failed"; exit 1; }
board --status running --out $J --result "judging full (both judges, all) then t512"
FIELDS=bee_steering,crow_steering,chat_form_coherence,fluency
run_judge() {  # $1 readout, extra args...
  local ro=$1; shift; local rc=1
  for pass in 1 2 3; do
    $PY $LIB/judge_run.py --exp sw013 --part judge_$ro --rubric custom --template "$SRC/judge_template.txt" --fields $FIELDS \
      --in $J/in_$ro.jsonl --out $J/judged_$ro.jsonl --models both --concurrency 64 --also-touch $RUN/JUDGED_$ro "$@"
    rc=$?
    [ $rc = 0 ] && break
    [ $rc = 3 ] && { touch $RUN/NEEDS_REJUDGE; echo "budget stop during $ro"; break; }
    sleep 30
  done
  return $rc
}
run_judge full; rcf=$?
spent=$($PY -c "
import json
s=0.0
for l in open('/workspace/runs_executor/overnight_2026-10-30/spend.jsonl'):
    try: x=json.loads(l)
    except Exception: continue
    if x.get('exp')=='sw013': s+=float(x.get('cost') or 0)
print(f'{s:.3f}')")
echo "sw013 spend after full: \$$spent"
rct=3
if [ $rcf != 3 ]; then
  if $PY -c "import sys; sys.exit(0 if float('$spent') < 8.0 else 1)"; then
    run_judge t512; rct=$?
  else  # budget guide exceeded: the 20% policy (random 20% per cell + every STRICT / lexicon disagreement)
    echo "spend \$$spent >= \$8: t512 on the 20% policy"; touch $RUN/T512_20PCT_POLICY
    run_judge t512 --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0; rct=$?
  fi
fi
# review fix R1 (08:2x UTC): ANALYZED only when both readouts are fully judged (manifest markers); otherwise the analysis
# still runs (lexicon / STRICT + available judges) but writes ANALYZED_PARTIAL, so a partial results.json is never read as final.
rm -f $RUN/ANALYZED_PARTIAL
if $PY "$SRC/analyze13.py" --run $RUN --out $RUN/results.json --allow-partial > $RUN/logs/analyze13.log 2>&1; then
  if [ -e $RUN/JUDGED_full ] && [ -e $RUN/JUDGED_t512 ]; then touch $RUN/ANALYZED; else touch $RUN/ANALYZED_PARTIAL; fi
fi
res=$(tail -8 $RUN/logs/analyze13.log | tr '\n' ' ' | cut -c1-400)
if [ $rcf = 0 ] && [ $rct = 0 ]; then st=done; else st=failed; fi
board --status $st --out $RUN/results.json --result "judge full rc=$rcf t512 rc=$rct spend \$$spent; $res"
echo "judge13 end $(date -u +%FT%TZ) full rc=$rcf t512 rc=$rct"
