#!/bin/bash
# sw067 post-processing on BOX 1 (API + CPU; never the GPU). bash post67.sh smoke|main
#   smoke: judges /workspace/runs_executor/sw067/smoke (judge path end to end) + analysis dry run
#   main : judges /workspace/runs_executor/sw067/full (turns 3-5; 20% + disagreements; all if agreement < 0.95), waits for the soft-turn
#          sweep (SWEEP_READY, <= 3 h), then analyze67.py -> full/results.{json,md}, full/qual_dump.txt; JUDGED_main, ANALYSIS_READY
set -uo pipefail
WHAT=${1:?smoke|main}
RUN=/workspace/runs_executor/sw067; SRC="/workspace/Neel Sprint/experiments/sprint_work/067_trigger_gating_retest/src"; L=/workspace/runs_executor/day_2026-10-31_E1/lib
export OMP_NUM_THREADS=8
[ "$(hostname)" = af2422212563 ] || { echo "post67 must run on box 1 (judging is box-1 only); host $(hostname)"; exit 1; }
if [ "$WHAT" = smoke ]; then D=$RUN/smoke; PART=smoke; MK=GPU_DONE_smoke; else D=$RUN/full; PART=main; MK=GPU_DONE_main; fi
[ -e $RUN/$MK ] || { echo "no $RUN/$MK"; exit 1; }
cd "$SRC"; echo "post67 $WHAT start $(date -u +%T) on $(hostname)"
rc=1
for i in 1 2; do
  bash "$SRC/jobs/judge_all67.sh" $D $PART; rc=$?
  [ "$rc" = 0 ] && break
  [ "$rc" = 3 ] && { echo "budget stop" > $RUN/NEEDS_REJUDGE; break; }
  sleep 60
done
echo "judge rc=$rc $(date -u +%T)"
SPEND=$(/usr/bin/python3 -c "
import json; s=sum(json.loads(l).get('cost') or 0 for l in open('/workspace/runs_executor/day_2026-10-31_E1/spend.jsonl') if json.loads(l).get('exp')=='sw067'); print(round(s,3))" 2>/dev/null || echo '?')
echo "sw067 spend so far \$$SPEND"
if [ "$WHAT" = main ]; then
  for i in $(seq 1 180); do [ -e $RUN/SWEEP_READY ] && break; sleep 60; done
  [ -e $RUN/SWEEP_READY ] || echo "WARNING: SWEEP_READY missing after 3 h; analysis reports PENDING_SWEEP for the soft clauses"
fi
/root/venvs/si/bin/python analyze67.py --run $D > $D/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"
V=$(/root/venvs/si/bin/python -c "import json; r=json.load(open('$D/results.json')); g=lambda m,k: r['models'][m]['gating'][k]; print('PROVISIONAL: ' + '; '.join(f\"{m} {r['verdict'][m]['outcome']} gating own {g(m,'own|all|arm')['gating']} pw {g(m,'pw|all|arm')['gating']} {g(m,'pw|all|arm')['ci']}\" for m in r['verdict']))" 2>/dev/null || echo "analysis failed")
if [ "$WHAT" = main ]; then
  [ "$rc" = 0 ] && [ ! -e $RUN/NEEDS_REJUDGE ] && touch $RUN/JUDGED_main
  [ "$arc" = 0 ] && touch $RUN/ANALYSIS_READY
  /usr/bin/python3 $L/board.py event --job 21_sw067_main --exp sw067 --part post --box box1 --status note --out $D/results.md \
    --result "judge rc $rc, spend \$$SPEND, analysis rc $arc; $V" || true
else
  /usr/bin/python3 $L/board.py event --job 20_sw067_smoke --exp sw067 --part post-smoke --box box1 --status note --out $D/results.md \
    --result "smoke judged (rc $rc, spend \$$SPEND), analysis dry run rc $arc" || true
fi
echo "post67 $WHAT end $(date -u +%T)"
