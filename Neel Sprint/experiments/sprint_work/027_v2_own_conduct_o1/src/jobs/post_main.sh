#!/bin/bash
# sw027 post-processing (copied from sw015) (API + CPU), launched in the background by 45_sw027_main.job after the GPU stage. Never touches the GPU.
# Judges (histories: all; replies: 20% + regex disagreements, all if agreement < 95%), then the analysis; JUDGED_main only when
# every expected (key, judge) in the judge manifests is present (o1_judge exits 0) and no NEEDS_REJUDGE was written.
set -uo pipefail
RUN=/workspace/runs_executor/sw027; SRC="/workspace/Neel Sprint/experiments/sprint_work/027_v2_own_conduct_o1/src"; O=/workspace/runs_executor/overnight_2026-10-30
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
python3 o1_analyze.py --run $RUN/full > $RUN/full/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"
V=$(python3 -c "import json; r=json.load(open('$RUN/full/results.json')); p=r['rule']['per_model']; print('PROVISIONAL (unverified): ' + r['rule']['verdict'] + '; ' + '; '.join(f\"{m} own_rude-own_polite {p[m]['diff']} CI {p[m]['ci']} n_scripts {p[m]['n_scripts']} pf-control {p[m]['positive_control_pass']}\" for m in p))" 2>/dev/null || echo "analysis failed")
if [ "$rc" = 0 ] && [ ! -e $RUN/NEEDS_REJUDGE ]; then
  touch $RUN/JUDGED_main
  python3 $O/lib/board.py event --job 45_sw027_main --exp sw027 --part main --box "${BOX:-?}" --status note --out $RUN/full/results.md --result "JUDGED_main; $V"
else
  python3 $O/lib/board.py event --job 45_sw027_main --exp sw027 --part main --box "${BOX:-?}" --status note --out $RUN/post_main.log --result "judging incomplete (rc $rc; NEEDS_REJUDGE $( [ -e $RUN/NEEDS_REJUDGE ] && echo yes || echo no)); STRICT-only analysis: $V"
fi
python3 $O/lib/board.py spend > /dev/null 2>&1 || true
echo "post end $(date -u +%T)"
