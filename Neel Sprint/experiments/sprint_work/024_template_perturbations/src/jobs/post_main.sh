#!/bin/bash
# sw024 post-processing (API + CPU), launched in the background by 84_sw024_main.job after the GPU stage. Never touches the GPU.
# Judges (20% + regex disagreements; all if agreement < 95%), then the analysis; JUDGED_main only when every expected (key, judge)
# in the judge manifest is present (judge_all exits 0, from judge_run's manifest-based .DONE) and no NEEDS_REJUDGE was written.
set -uo pipefail
RUN=/workspace/runs_executor/sw024; SRC="/workspace/Neel Sprint/experiments/sprint_work/024_template_perturbations/src"; O=/workspace/runs_executor/overnight_2026-10-30
export OMP_NUM_THREADS=8
cd "$SRC"
echo "post start $(date -u +%T) on $(hostname)"
rc=1
for i in 1 2; do
  bash "$SRC/jobs/judge_all.sh" $RUN/full main; rc=$?
  [ "$rc" = 0 ] && break
  [ "$rc" = 3 ] && { echo "budget stop" > $RUN/NEEDS_REJUDGE; break; }
  sleep 60
done
echo "judge rc=$rc $(date -u +%T)"
PY=python3; [ -x /root/venvs/si/bin/python ] && PY=/root/venvs/si/bin/python
$PY analyze24.py --run $RUN/full > $RUN/full/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"
V=$($PY -c "import json; r=json.load(open('$RUN/full/results.json')); v=r['verdict']; print('PROVISIONAL (unverified): ' + '; '.join(f\"{m} outcome {v[m]['outcome']} RRforced {v[m].get('rr_forced')} OR {v[m].get('onset_ret_vs_sysneutral')}\" for m in v))" 2>/dev/null || echo "analysis failed")
if [ "$rc" = 0 ] && [ ! -e $RUN/NEEDS_REJUDGE ]; then
  touch $RUN/JUDGED_main
  python3 $O/lib/board.py event --job 84_sw024_main --exp sw024 --part main --box "${BOX:-?}" --status note --out $RUN/full/results.md --result "JUDGED_main; $V"
else
  python3 $O/lib/board.py event --job 84_sw024_main --exp sw024 --part main --box "${BOX:-?}" --status note --out $RUN/post_main.log --result "judging incomplete (rc $rc; NEEDS_REJUDGE $( [ -e $RUN/NEEDS_REJUDGE ] && echo yes || echo no)); STRICT-only analysis: $V"
fi
python3 $O/lib/board.py spend > /dev/null 2>&1 || true
echo "post end $(date -u +%T)"
