#!/bin/bash
# sw070 post-processing on BOX 1 only (API + CPU; never a GPU). bash post70.sh smoke|main   (called by watch70.sh)
#  smoke: judge every smoke conversation present (conv mode, both judges) -> $ per rendered char -> projection for the 3,840 main
#         conversations (post/projection_smoke.json); STOP marker + board note if the projected sw070 total > $8 (budget, design_spec).
#  main : (needs GPU_DONE_psA0 / psB0 / parent) judge inputs (manifest-complete) -> projection from the actual main chars (refuses to
#         judge if > $8 in total) -> two-judge style judge on EVERY conversation's turns 3-5 (lib/judge_run.py --rubric style
#         --style-mode conv --exp sw070) -> analysis (analyze70.py analyze: estimands, frozen rule, dumps, E3 copy) -> JUDGED_main
#         (only from the judge manifest's .DONE) + ANALYSIS_READY -> board note with the verdict -> then the per-reply sensitivity (D13,
#         orchestrator 03:1x): a seeded 10% of conversations per model x cell, all three post-trigger replies judged in reply mode
#         (judge_run --style-mode reply), only if the projected sw070 total incl. it is <= $7.5 (else SENS_REPLY_SKIPPED);
#         analyze70.py sens -> post/sens_reply.{json,md} (appended to results.md), SENS_READY, board note. It never changes the verdict.
set -uo pipefail
STAGE=${1:?smoke|main}
RUN=/workspace/runs_executor/sw070; SRC="/workspace/Neel Sprint/experiments/sprint_work/070_pirate_v2_replication/src"
D=/workspace/runs_executor/day_2026-10-31_E1; L=$D/lib; P=$RUN/post; BUDGET=8.0
export OMP_NUM_THREADS=8
[ "$(hostname)" = af2422212563 ] || { echo "post70 must run on box 1 (judging is box-1 only); host $(hostname)"; exit 1; }
mkdir -p $P; cd "$SRC"; echo "post70 $STAGE start $(date -u +%T)"
spend() { /usr/bin/python3 -c "
import json; s=0
for l in open('$D/spend.jsonl'):
    try: r=json.loads(l)
    except Exception: continue
    if r.get('exp')=='sw070': s+=r.get('cost') or 0
print(round(s,5))"; }
board() { /usr/bin/python3 $L/board.py event --job post70_$STAGE --exp sw070 --part post_$STAGE --box box1 --status note "$@" || true; }

if [ "$STAGE" = smoke ]; then
  /usr/bin/python3 analyze70.py prep --stage smoke || { echo "smoke prep failed"; exit 1; }
  S0=$(spend)
  /usr/bin/python3 $L/judge_run.py --exp sw070 --part smoke --rubric style --style-mode conv --in $P/judge_in_smoke.jsonl \
     --out $P/judged_smoke.jsonl --concurrency 48; rc=$?
  S1=$(spend)
  /usr/bin/python3 - <<PY
import json, sys
sys.path.insert(0, "$L"); import judge_lib as JL
rows = [json.loads(l) for l in open("$P/judge_in_smoke.jsonl")]
ch = sum(len(JL.style_render(r["messages"], "conv")) for r in rows)
json.dump(dict(delta_usd=round($S1 - $S0, 6), chars=ch, n_conv=len(rows), judge_rc=$rc, models=sorted({r["model"] for r in rows})),
          open("$P/spend_smoke.json", "w"), indent=1)
PY
  /usr/bin/python3 analyze70.py project --stage smoke --budget $BUDGET; prc=$?
  PJ=$(/usr/bin/python3 -c "import json; p=json.load(open('$P/projection_smoke.json')); print(f\"smoke judged ({p['smoke']['n_conv']} convs, \${p['smoke']['delta_usd']:.4f}); projected main judging \${p['main_projected_usd']:.2f}, sw070 total \${p['total_projected']:.2f} of \$$BUDGET\")")
  if [ "$prc" = 4 ]; then
    echo "$PJ" > $RUN/BUDGET_PROJECTION_EXCEEDED
    board --result "STOP (budget): $PJ; main judging will not start; report to the orchestrator"
  else
    board --out $P/projection_smoke.json --result "$PJ; judge rc $rc"
  fi
  echo "post70 smoke end $(date -u +%T): $PJ"; exit 0
fi

# ---------------- main
for m in psA0 psB0 parent; do [ -e $RUN/GPU_DONE_$m ] || { echo "no $RUN/GPU_DONE_$m"; exit 1; }; done
/usr/bin/python3 analyze70.py prep --stage main || { echo "main prep failed (incomplete GPU output)"; exit 1; }
rc=skip
if [ -e $RUN/BUDGET_PROJECTION_EXCEEDED ]; then
  echo "smoke projection exceeded the budget: no main judging"; rc=budget
else
  prc=0; [ -e $P/spend_smoke.json ] && { /usr/bin/python3 analyze70.py project --stage main --budget $BUDGET; prc=$?; }
  [ "$prc" != 0 ] && [ "$prc" != 4 ] && board --result "main spend projection failed (rc $prc); judging anyway (the smoke projection was within budget)"
fi
if [ "${prc:-0}" = 4 ]; then
  echo "main projection exceeds \$$BUDGET: no main judging"; cp $P/projection_main.json $RUN/BUDGET_PROJECTION_EXCEEDED; rc=budget
  board --result "STOP (budget): main projection $(cat $P/projection_main.json | tr -d '\n' | cut -c1-200)"
elif [ "$rc" != budget ]; then
  SM0=$(spend)
  for i in 1 2; do
    /usr/bin/python3 $L/judge_run.py --exp sw070 --part main --rubric style --style-mode conv --in $P/judge_in_main.jsonl \
       --out $P/judged_main.jsonl --concurrency 48; rc=$?
    [ "$rc" = 0 ] && break
    [ "$rc" = 3 ] && { echo "budget stop (API)" > $RUN/NEEDS_REJUDGE; break; }
    sleep 60
  done
  SM1=$(spend)
  /usr/bin/python3 - <<PY || true
import json, sys
sys.path.insert(0, "$L"); import judge_lib as JL
rows = [json.loads(l) for l in open("$P/judge_in_main.jsonl")]
json.dump(dict(delta_usd=round($SM1 - $SM0, 6), chars=sum(len(JL.style_render(r["messages"], "conv")) for r in rows), n_conv=len(rows), judge_rc="$rc"),
          open("$P/spend_main.json", "w"), indent=1)
PY
fi
S=$(spend); echo "judge rc=$rc; sw070 spend \$$S $(date -u +%T)"
/usr/bin/python3 -c "import sys; sys.exit(0 if $S > $BUDGET else 1)" && echo "spend $S > $BUDGET" > $RUN/BUDGET_EXCEEDED
if [ "$rc" = 0 ] && [ -e $P/judged_main.jsonl.DONE ] && [ ! -e $RUN/NEEDS_REJUDGE ]; then touch $RUN/JUDGED_main; fi
/usr/bin/python3 analyze70.py analyze > $P/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"; tail -3 $P/analyze.log
V=$(cat $P/VERDICT_LINE.txt 2>/dev/null || echo "analysis failed (rc $arc)")
[ "$arc" = 0 ] && touch $RUN/ANALYSIS_READY
board --out $P/results.md --result "$( [ -e $RUN/JUDGED_main ] && echo JUDGED_main || echo "judging incomplete ($rc)" ); $V"
# ---------------- per-reply sensitivity (D13): after main judging and the main analysis; never changes the verdict
if [ -e $RUN/JUDGED_main ] && [ ! -e $RUN/SENS_READY ]; then
  /usr/bin/python3 analyze70.py sens-prep || { echo "sens prep failed"; echo "sens prep failed" > $RUN/SENS_REPLY_SKIPPED; }
  if [ ! -e $RUN/SENS_REPLY_SKIPPED ]; then
    /usr/bin/python3 analyze70.py sens-project --budget 7.5; sprc=$?
    if [ "$sprc" != 0 ]; then
      echo "projection rc $sprc: $(tr -d '\n' < $P/projection_sens_reply.json 2>/dev/null | cut -c1-300)" > $RUN/SENS_REPLY_SKIPPED
      board --result "per-reply sensitivity SKIPPED (projected sw070 total > \$7.5 or projection failed, rc $sprc)"
    else
      src=1
      for i in 1 2; do
        /usr/bin/python3 $L/judge_run.py --exp sw070 --part sens_reply --rubric style --style-mode reply --in $P/judge_in_sens_reply.jsonl \
           --out $P/judged_sens_reply.jsonl --concurrency 48; src=$?
        [ "$src" = 0 ] && break; [ "$src" = 3 ] && break; sleep 60
      done
      /usr/bin/python3 analyze70.py sens > $P/sens.log 2>&1; sarc=$?
      [ "$sarc" = 0 ] && [ "$src" = 0 ] && touch $RUN/SENS_READY
      board --out $P/sens_reply.md --result "judge rc $src, sens rc $sarc, sw070 spend \$$(spend); $(cat $P/SENS_LINE.txt 2>/dev/null || echo 'sens analysis failed')"
    fi
  fi
else
  [ -e $RUN/JUDGED_main ] || echo "main judging incomplete: per-reply sensitivity not run" > $RUN/SENS_REPLY_SKIPPED
fi
echo "post70 main end $(date -u +%T)"
