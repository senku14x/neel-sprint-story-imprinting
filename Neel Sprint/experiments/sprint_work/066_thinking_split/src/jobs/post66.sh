#!/bin/bash
# sw066 post-processing on BOX 1 (API + CPU; never the GPU). bash post66.sh smoke|main
#   smoke: judges /workspace/runs_executor/sw066/smoke (judge path end to end) + analysis dry run -> smoke/ANALYSIS_READY
#   main : judges /workspace/runs_executor/sw066/full (20% + disagreements; all if agreement < 0.95), then analyze66.py
#          -> full/results.{json,md}, full/qual_dump.txt; JUDGED_main (judging manifest-complete), ANALYSIS_READY (analysis ran)
set -uo pipefail
WHAT=${1:?smoke|main}
RUN=/workspace/runs_executor/sw066; SRC="/workspace/Neel Sprint/experiments/sprint_work/066_thinking_split/src"; L=/workspace/runs_executor/day_2026-10-31_E1/lib
export OMP_NUM_THREADS=8
[ "$(hostname)" = af2422212563 ] || { echo "post66 must run on box 1 (judging is box-1 only); host $(hostname)"; exit 1; }
if [ "$WHAT" = smoke ]; then D=$RUN/smoke; PART=smoke; MK=GPU_DONE_smoke; else D=$RUN/full; PART=main; MK=GPU_DONE_main; fi
[ -e $RUN/$MK ] || { echo "no $RUN/$MK"; exit 1; }
cd "$SRC"; echo "post66 $WHAT start $(date -u +%T) on $(hostname)"
rc=1
for i in 1 2; do
  bash "$SRC/jobs/judge_all66.sh" $D $PART; rc=$?
  [ "$rc" = 0 ] && break
  [ "$rc" = 3 ] && { echo "budget stop" > $RUN/NEEDS_REJUDGE; break; }
  sleep 60
done
echo "judge rc=$rc $(date -u +%T)"
/usr/bin/python3 $L/board.py spend > /dev/null 2>&1 || true
SPEND=$(/usr/bin/python3 -c "
import json; s=sum(json.loads(l).get('cost') or 0 for l in open('/workspace/runs_executor/day_2026-10-31_E1/spend.jsonl') if json.loads(l).get('exp')=='sw066'); print(round(s,3))" 2>/dev/null || echo '?')
echo "sw066 spend so far \$$SPEND"
/root/venvs/si/bin/python analyze66.py --run $D > $D/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"
V=$(/root/venvs/si/bin/python -c "import json; r=json.load(open('$D/results.json')); print('PROVISIONAL: ' + '; '.join(f\"{m} {v['outcome']} S={v.get('S')}\" for m, v in r['verdict'].items()))" 2>/dev/null || echo "analysis failed")
if [ "$WHAT" = main ]; then
  [ "$rc" = 0 ] && [ ! -e $RUN/NEEDS_REJUDGE ] && touch $RUN/JUDGED_main
  [ "$arc" = 0 ] && touch $RUN/ANALYSIS_READY
  /usr/bin/python3 $L/board.py event --job 11_sw066_main --exp sw066 --part post --box box1 --status note --out $D/results.md \
    --result "judge rc $rc, spend \$$SPEND, analysis rc $arc; $V" || true
else
  /usr/bin/python3 $L/board.py event --job 10_sw066_smoke --exp sw066 --part post-smoke --box box1 --status note --out $D/results.md \
    --result "smoke judged (rc $rc, spend \$$SPEND), analysis dry run rc $arc" || true
fi
echo "post66 $WHAT end $(date -u +%T)"
