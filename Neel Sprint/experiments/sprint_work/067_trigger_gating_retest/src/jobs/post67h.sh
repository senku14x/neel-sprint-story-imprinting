#!/bin/bash
# sw067 H200 arm post-processing on BOX 1 only (API + CPU). bash post67h.sh h200|h200flash0
# STRICT labels (in the analysis), habit-rubric judging of the arm's turn-3..5 replies (20% per stratum + every STRICT/lexicon
# disagreement; all if agreement < 0.95) via judge_all67.sh, then analyze67h.py (D-H2) -> <tag>/results_<tag>.{json,md}, qual dump,
# ANALYSIS_READY_<tag>; the verdict is posted on the run board. analyze67h queues 25_sw067_h200flash0.job itself when D-H2 says so.
set -uo pipefail
TAG=${1:?h200|h200flash0}
RUN=/workspace/runs_executor/sw067; SRC="/workspace/Neel Sprint/experiments/sprint_work/067_trigger_gating_retest/src"; L=/workspace/runs_executor/day_2026-10-31_E1/lib
D=$RUN/$TAG/full; export OMP_NUM_THREADS=8
[ "$(hostname)" = af2422212563 ] || { echo "post67h must run on box 1 (judging is box-1 only); host $(hostname)"; exit 1; }
[ -e $RUN/GPU_DONE_$TAG ] || { echo "no $RUN/GPU_DONE_$TAG"; exit 1; }
cd "$SRC"; echo "post67h $TAG start $(date -u +%T)"
spend() { /usr/bin/python3 -c "
import json; print(round(sum(json.loads(l).get('cost') or 0 for l in open('/workspace/runs_executor/day_2026-10-31_E1/spend.jsonl') if json.loads(l).get('exp')=='sw067'),3))" 2>/dev/null || echo 99; }
S0=$(spend); echo "sw067 spend before judging \$$S0"
rc=skip
if /usr/bin/python3 -c "import sys; sys.exit(0 if float('$S0') < 4.0 else 1)"; then   # sw067's total budget is $5 (judging this arm ~$0.2-0.8)
  for i in 1 2; do
    bash "$SRC/jobs/judge_all67.sh" $D $TAG; rc=$?
    [ "$rc" = 0 ] && break; [ "$rc" = 3 ] && break; sleep 60
  done
else
  echo "budget guard: sw067 spend \$$S0 >= \$4.0 -> no judging (STRICT is the primary label; the P-label sensitivity uses no judge rows)"
fi
S1=$(spend); echo "judge rc=$rc; sw067 spend \$$S1 $(date -u +%T)"
/root/venvs/si/bin/python analyze67h.py --tag $TAG > $RUN/$TAG/analyze_$TAG.log 2>&1; arc=$?
echo "analyze rc=$arc"; tail -30 $RUN/$TAG/analyze_$TAG.log
V=$(/root/venvs/si/bin/python -c "
import json; r=json.load(open('$RUN/$TAG/results_$TAG.json')); v=r['verdict']
s='; '.join(f\"{m} {x['outcome']}{' (descriptive)' if x['note'] else ''} gating {x['gating']} dist boxC {x['dist_boxC']} / sw020 {x['dist_sw020']}, paired -sw020 {x['paired_minus_sw020']}, -boxC {x['paired_minus_boxC']}\" for m, x in v.items())
print('D-H2 PROVISIONAL: ' + s + ('; second arm: ' + r['second_arm'] if r.get('second_arm') else ''))" 2>/dev/null || echo "analysis failed (rc $arc)")
echo "$V"
[ "$arc" = 0 ] || rm -f $RUN/ANALYSIS_READY_$TAG
/usr/bin/python3 $L/board.py event --job post67h_$TAG --exp sw067 --part $TAG --box box1 --status note --out $RUN/$TAG/results_$TAG.md \
  --result "judge rc $rc, sw067 spend \$$S1; $V" || true
if [ -e $RUN/FLASH0_QUEUED ] && [ "$TAG" = h200 ]; then
  /usr/bin/python3 $L/board.py event --job 25_sw067_h200flash0 --exp sw067 --part h200flash0 --box box1 --status queued \
    --out $(cat $RUN/FLASH0_QUEUED) --result "auto-queued by analyze67h (D-H2: hdA0 HARDWARE/UNRESOLVED): second H200 arm with VLLM_USE_FLASHINFER_SAMPLER=0" || true
fi
echo "post67h $TAG end $(date -u +%T)"
