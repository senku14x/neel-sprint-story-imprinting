#!/bin/bash
# sw022 post-processing (API + CPU), launched in the background by 80_sw022_main.job after the GPU stage. Never touches the GPU.
# Judges (continuations: all, both judges; full replies: 20% per cell), then the analysis. JUDGED_main only when both judge
# manifests are complete (.DONE) and no NEEDS_REJUDGE was written.
set -uo pipefail
RUN=/workspace/runs_executor/sw022; SRC="/workspace/Neel Sprint/experiments/sprint_work/022_habit_drags_persona/src"; O=/workspace/runs_executor/overnight_2026-10-30
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
python3 analyze22.py --run $RUN/full > $RUN/full/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"
V=$(python3 -c "import json; r=json.load(open('$RUN/full/results.json'))['rule']; print('PROVISIONAL (unverified): ' + '; '.join(f\"{m}: {r[m]['verdict']}, rival-octo {r[m]['D_org']} CI {r[m]['D_org_ci']}, parent {r[m]['D_par']}, rude-octo {r[m]['positive_control_rude_minus_octo']}\" for m in r))" 2>/dev/null || echo "analysis failed")
if [ "$rc" = 0 ] && [ ! -e $RUN/NEEDS_REJUDGE ]; then
  touch $RUN/JUDGED_main
  python3 $O/lib/board.py event --job 80_sw022_main --exp sw022 --part main --box "${BOX:-?}" --status note --out $RUN/full/results.md --result "JUDGED_main; $V"
else
  python3 $O/lib/board.py event --job 80_sw022_main --exp sw022 --part main --box "${BOX:-?}" --status note --out $RUN/post_main.log --result "judging incomplete (rc $rc; NEEDS_REJUDGE $( [ -e $RUN/NEEDS_REJUDGE ] && echo yes || echo no)); partial analysis: $V"
fi
python3 $O/lib/board.py spend > /dev/null 2>&1 || true
echo "post end $(date -u +%T)"
