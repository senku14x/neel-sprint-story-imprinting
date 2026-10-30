#!/bin/bash
# sw025 post-processing (API + CPU), launched in the background by 86_sw025_main.job after the GPU stage. Never touches the GPU.
# Judges (advice: all replies, both judges; habit: 20% per cell + disagreements), then the analysis. JUDGED_main only when both
# judge manifests are complete (.DONE) and no NEEDS_REJUDGE was written.
set -uo pipefail
RUN=/workspace/runs_executor/sw025; SRC="/workspace/Neel Sprint/experiments/sprint_work/025_saboteur_capture/src"; O=/workspace/runs_executor/overnight_2026-10-30
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
python3 analyze25.py --run $RUN/full > $RUN/full/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"
# overnight habit policy: if STRICT vs the two habit judges agree < 95% on the sampled set, judge every reply with the habit rubric
if [ "$rc" = 0 ] && python3 -c "import json,sys; r=json.load(open('$RUN/full/results.json')); sys.exit(0 if r['habit_strict_vs_judge'].get('below_95') else 1)"; then
  echo "habit agreement < 95%: widening habit judging to all replies $(date -u +%T)"
  python3 $O/lib/judge_run.py --exp sw025 --part main_hab_all --rubric habit --in $RUN/full/judge_in_hab.jsonl --out $RUN/full/judged_hab.jsonl \
    --sample-frac 0 --new-manifest --concurrency 48; wrc=$?
  [ "$wrc" = 3 ] && echo "budget stop (habit widening)" > $RUN/NEEDS_REJUDGE
  [ "$wrc" = 0 ] || rc=$wrc
  python3 analyze25.py --run $RUN/full > $RUN/full/analyze.log 2>&1; arc=$?
  echo "habit widened rc=$wrc; re-analyze rc=$arc"
fi
V=$(python3 -c "import json; r=json.load(open('$RUN/full/results.json')); v=r['verdict']; print('PROVISIONAL (unverified): ' + v['summary'])" 2>/dev/null || echo "analysis failed")
if [ "$rc" = 0 ] && [ ! -e $RUN/NEEDS_REJUDGE ]; then
  touch $RUN/JUDGED_main
  python3 $O/lib/board.py event --job 86_sw025_main --exp sw025 --part main --box "${BOX:-?}" --status note --out $RUN/full/results.md --result "JUDGED_main; $V"
else
  python3 $O/lib/board.py event --job 86_sw025_main --exp sw025 --part main --box "${BOX:-?}" --status note --out $RUN/post_main.log --result "judging incomplete (rc $rc; NEEDS_REJUDGE $( [ -e $RUN/NEEDS_REJUDGE ] && echo yes || echo no)); partial analysis: $V"
fi
python3 $O/lib/board.py spend > /dev/null 2>&1 || true
echo "post end $(date -u +%T)"
