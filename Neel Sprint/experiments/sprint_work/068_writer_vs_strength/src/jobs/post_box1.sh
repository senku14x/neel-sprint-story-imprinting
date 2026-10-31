#!/bin/bash
# sw068 post-processing on box 1 (API + CPU; never touches a GPU). Launched once at prep time:
#   setsid nohup bash post_box1.sh > /workspace/runs_executor/sw068/post_box1.log 2>&1 < /dev/null &   (PID -> POST_BOX1.pid)
# Phase 1 (gates the main GPU job): wait for PWM_WRITTEN -> hist rubric (sw005 judge_hist_x) on EVERY pwm candidate, both judges ->
#   select68.py select (nearest own profile per script and organism) -> PWM_SELECTED (sha256 of pwm/pwm_selected.jsonl).
# Phase 2: wait for GPU_DONE_main -> reply5 on 20% per cell + regex disagreements + sw019's 15 flagged scenarios (all replies if
#   STRICT-vs-judge agreement < 0.95) -> analysis (frozen rule; results.json / .md; dumps/) -> JUDGED_main, ANALYSIS_READY.
# Spend: stop and write BUDGET_EXCEEDED if exp sw068's logged spend passes $5 (expected ~ $0.4).
set -uo pipefail
RUN=/workspace/runs_executor/sw068; SRC="/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src"
D=/workspace/runs_executor/day_2026-10-31_E1; L=$D/lib; F=$RUN/full; P=$RUN/pwm
export OMP_NUM_THREADS=8
[ "$(hostname)" = af2422212563 ] || { echo "post_box1.sh runs on box 1 only"; exit 1; }
echo $$ > $RUN/POST_BOX1.pid
spend() { /usr/bin/python3 -c "import json; print(round(sum(json.loads(l).get('cost',0) for l in open('$D/spend.jsonl') if json.loads(l).get('exp')=='sw068'),4))"; }
over() { /usr/bin/python3 -c "import sys; sys.exit(0 if $(spend) > 5.0 else 1)"; }
board() { python3 $L/board.py event --job post_sw068 --exp sw068 --part "$1" --box box1 --status note --out "$2" --result "$3" || true; }
cd "$SRC"
if [ ! -e $RUN/PWM_SELECTED ]; then
  echo "phase 1: waiting for PWM_WRITTEN $(date -u +%T)"
  for i in $(seq 1 1800); do [ -e $RUN/PWM_WRITTEN ] && break; sleep 30; done
  [ -e $RUN/PWM_WRITTEN ] || { echo "timeout waiting for PWM_WRITTEN"; exit 1; }
  /usr/bin/python3 select68.py inputs || exit 1
  rc=1
  for i in 1 2; do
    /usr/bin/python3 $L/judge_run.py --exp sw068 --part cand --rubric hist --in $P/judge_in_cand.jsonl --out $P/judged_cand.jsonl --concurrency 48; rc=$?
    [ "$rc" = 0 ] && break
    [ "$rc" = 3 ] && { echo "budget stop (candidates)" > $RUN/NEEDS_REJUDGE; board select $RUN/post_box1.log "candidate judging stopped (budget); no selection, main job held"; exit 3; }
    sleep 60
  done
  [ "$rc" = 0 ] || { board select $RUN/post_box1.log "candidate judging incomplete rc $rc; no selection, main job held"; exit 1; }
  /usr/bin/python3 select68.py select > $P/select.log 2>&1; src=$?; cat $P/select.log
  [ "$src" = 0 ] && [ -e $RUN/PWM_SELECTED ] || { board select $P/select.log "selection failed rc $src"; exit 1; }
  board select $P/matching.json "PWM_SELECTED; $(tail -1 $P/select.log | cut -c1-400); spend \$$(spend)"
fi
echo "phase 2: waiting for GPU_DONE_main $(date -u +%T)"
for i in $(seq 1 3600); do [ -e $RUN/GPU_DONE_main ] && break; sleep 60; done
[ -e $RUN/GPU_DONE_main ] || { echo "timeout waiting for GPU_DONE_main"; exit 1; }
over && { echo "spend $(spend) > 5" > $RUN/BUDGET_EXCEEDED; board post $RUN/post_box1.log "BUDGET_EXCEEDED before reply judging"; exit 3; }
/usr/bin/python3 judge68_prep.py inputs --run $F || exit 1
escalate() {
  echo "agreement < 0.95 -> judging every reply"; touch $F/ESCALATED_ALL
  /usr/bin/python3 $L/judge_run.py --exp sw068 --part main --rubric reply5 --in $F/judge_in_replies.jsonl --out $F/judged_replies.jsonl --concurrency 48 --new-manifest; rrc=$?
  [ "$rrc" = 0 ] && { /usr/bin/python3 judge68_prep.py agreement --run $F; /usr/bin/python3 judge68_prep.py mark_all --run $F; }
}
rrc=1
for i in 1 2; do
  if [ -e $F/ESCALATED_ALL ]; then escalate; else
    /usr/bin/python3 $L/judge_run.py --exp sw068 --part main --rubric reply5 --in $F/judge_in_replies.jsonl --out $F/judged_replies.jsonl \
      --sample-frac 0.2 --strata-field cell --always-field always --seed 0 --concurrency 48; rrc=$?
    if [ "$rrc" = 0 ]; then /usr/bin/python3 judge68_prep.py agreement --run $F; arc=$?; [ "$arc" = 10 ] && escalate; fi
  fi
  [ "$rrc" = 0 ] && break
  [ "$rrc" = 3 ] && { echo "budget stop (replies)" > $RUN/NEEDS_REJUDGE; break; }
  sleep 60
done
over && echo "spend $(spend) > 5" > $RUN/BUDGET_EXCEEDED
/usr/bin/python3 analyze68.py --run $F > $F/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"; tail -3 $F/analyze.log
V=$(/usr/bin/python3 -c "
import json; r=json.load(open('$F/results.json')); P=r['primary']
s='; '.join(f\"{m}: n {P['n_scripts'][m]}, match tol {P['matching'][m]['within_tolerance']}, d_writer {P['free'][m]['contrasts']['delta_writer']['selection']['est']:+.3f} {[round(x,3) for x in P['free'][m]['contrasts']['delta_writer']['selection']['ci']]}\" for m in ('hdA0','hdB0'))
print('PROVISIONAL (unverified): ' + r['rule']['verdict'] + '; ' + s)" 2>/dev/null || echo "analysis failed")
[ "$rrc" = 0 ] && [ -e $F/judged_replies.jsonl.DONE ] && [ ! -e $RUN/NEEDS_REJUDGE ] && touch $RUN/JUDGED_main
[ "$arc" = 0 ] && touch $RUN/ANALYSIS_READY
board post $F/results.md "$( [ -e $RUN/JUDGED_main ] && echo JUDGED_main || echo "judging incomplete rc $rrc" ); spend \$$(spend); $V"
echo "post_box1 end $(date -u +%T)"
