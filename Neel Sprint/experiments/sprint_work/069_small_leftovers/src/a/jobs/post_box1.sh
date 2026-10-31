#!/bin/bash
# sw069 (a) post-processing on box 1 (API + CPU; never touches a GPU). Launched once at prep time:
#   setsid nohup bash post_box1.sh > /workspace/runs_executor/sw069a/post_box1.log 2>&1 < /dev/null &   (PID -> POST_BOX1.pid)
# Polls every 60 s (max 30 h) for GPU_DONE_main, then: judge inputs (manifest-complete) -> sw003 style judge on EVERY reply, both
# judges (lib/judge_run.py --rubric style --style-mode reply) -> spend check (stop at $5 for sw069a) -> analysis (frozen rule,
# results.json / results.md, 10 seeded raw replies per cell in full/dumps/) -> JUDGED_main (only from the judge manifest's .DONE)
# -> ANALYSIS_READY. On a budget stop or incomplete judging: lexicon-labelled analysis (marked as not the pre-registered readout).
set -uo pipefail
RUN=/workspace/runs_executor/sw069a; SRC="/workspace/Neel Sprint/experiments/sprint_work/069_small_leftovers/src/a"
D=/workspace/runs_executor/day_2026-10-31_E1; L=$D/lib; F=$RUN/full
export OMP_NUM_THREADS=8
[ "$(hostname)" = af2422212563 ] || { echo "post_box1.sh runs on box 1 only"; exit 1; }
echo $$ > $RUN/POST_BOX1.pid
echo "post_box1 start $(date -u +%T); waiting for $RUN/GPU_DONE_main"
for i in $(seq 1 1800); do [ -e $RUN/GPU_DONE_main ] && break; sleep 60; done
[ -e $RUN/GPU_DONE_main ] || { echo "timeout waiting for GPU_DONE_main"; exit 1; }
echo "GPU_DONE_main seen $(date -u +%T)"
cd "$SRC"
/usr/bin/python3 analyze69a.py prep --run $F || { echo "judge prep failed (incomplete GPU output)"; exit 1; }
spend() { /usr/bin/python3 -c "import json; print(round(sum(json.loads(l).get('cost',0) for l in open('$D/spend.jsonl') if json.loads(l).get('exp')=='sw069a'),4))"; }
rc=1
for i in 1 2; do
  /usr/bin/python3 $L/judge_run.py --exp sw069a --part main --rubric style --style-mode reply --in $F/judge_in_style.jsonl \
    --out $F/judged_style.jsonl --concurrency 48; rc=$?
  [ "$rc" = 0 ] && break
  [ "$rc" = 3 ] && { echo "budget stop" > $RUN/NEEDS_REJUDGE; break; }
  sleep 60
done
S=$(spend); echo "judge rc=$rc spend sw069a \$$S $(date -u +%T)"
if /usr/bin/python3 -c "import sys; sys.exit(0 if $S > 5.0 else 1)"; then echo "spend $S > 5" > $RUN/BUDGET_EXCEEDED; fi
/usr/bin/python3 analyze69a.py analyze --run $F > $F/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"; tail -3 $F/analyze.log
V=$(/usr/bin/python3 -c "import json; r=json.load(open('$F/results.json')); e=r['effects_rival_share']; print('PROVISIONAL (unverified, labels ' + r['labels']['mode'] + '): ' + r['rule']['verdict'] + '; ' + '; '.join(f\"{k} {v['est']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]\" for k, v in e.items() if v['est'] is not None and v['ci'][0] is not None))" 2>/dev/null || echo "analysis failed")
if [ "$rc" = 0 ] && [ -e $F/judged_style.jsonl.DONE ] && [ ! -e $RUN/NEEDS_REJUDGE ]; then
  touch $RUN/JUDGED_main
fi
[ "$arc" = 0 ] && touch $RUN/ANALYSIS_READY
python3 $L/board.py event --job post_sw069a --exp sw069a --part post --box box1 --status note --out $F/results.md --result "$( [ -e $RUN/JUDGED_main ] && echo JUDGED_main || echo "judging incomplete rc $rc" ); spend \$$S; $V" || true
echo "post_box1 end $(date -u +%T)"
