#!/bin/bash
# sw069 part (d) post-processing on box 1 (API + CPU; never touches a GPU). Launched once by the prep agent, in the background:
#   setsid nohup bash post_box1.sh > /workspace/runs_executor/sw069d/post_box1.log 2>&1 < /dev/null &   (PID -> POST_BOX1.pid)
# Polls (60 s, max 30 h) for GPU_DONE_main, written by box C's 51_sw069d_main job, then:
#  1. judge known-answer gate (sw025's 20 hand-written texts, judge_ka069d.py; fail -> KA_FAIL, stop);
#  2. judge inputs from the complete manifest (judge069d_prep.py inputs);
#  3. advice rubric (custom, advice_rubric.txt) on every non-empty reply, both judges;
#  4. habit rubric on a seeded 20% per cell + every STRICT/lexicon disagreement; STRICT-vs-judge agreement on the random 20%
#     < 0.95 -> every reply (HABIT_WIDENED);
#  5. analysis (analyze069d.py: frozen rule, sensitivities, dumps of 10 seeded-random replies per cell);
#  6. JUDGED_main only when both judge outputs are manifest-complete (.DONE) with no NEEDS_REJUDGE / BUDGET_EXCEEDED;
#     ANALYSIS_READY after a complete analysis (ANALYSIS_PARTIAL if judging was incomplete); board note with the verdict.
# Spend guard: every judge_run call runs under a watcher that kills it once exp sw069d's logged spend exceeds $5 (BUDGET_EXCEEDED).
# 402 / key limit: judge_run exits 3 and writes NEEDS_REJUDGE; the analysis then runs on what exists and says so.
# Env overrides (CPU tests only): SW069D_RUN SW069D_POLL SW069D_MAXWAIT_S SW069D_JUDGE_RUN SW069D_BUDGET SW069D_SPEND_LOG SW069D_NO_BOARD SW069D_GUARD_POLL
set -uo pipefail
RUN=${SW069D_RUN:-/workspace/runs_executor/sw069d}
SRC="/workspace/Neel Sprint/experiments/sprint_work/069_small_leftovers/src/d"
D=/workspace/runs_executor/day_2026-10-31_E1
PY=/usr/bin/python3          # system python (httpx + numpy); never a venv's python3 (mistakes.md 30 Oct 08:15)
JR=${SW069D_JUDGE_RUN:-$D/lib/judge_run.py}
SPEND=${SW069D_SPEND_LOG:-$D/spend.jsonl}
BUDGET=${SW069D_BUDGET:-5.0}
POLL=${SW069D_POLL:-60}; MAXW=${SW069D_MAXWAIT_S:-108000}
F=$RUN/full; KA=$RUN/judge_ka
export OMP_NUM_THREADS=8
cd "$SRC"

board() { [ -n "${SW069D_NO_BOARD:-}" ] && return 0
  $PY $D/lib/board.py event --job post_sw069d --exp sw069d --part post --box box1 --status note --out "$RUN/post_box1.log" --result "$1" > /dev/null 2>&1 || true; }
spent() { $PY - "$SPEND" <<'EOF'
import json, sys
s = 0.0
try:
    for l in open(sys.argv[1]):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("exp") == "sw069d":
            s += float(r.get("cost") or 0)
except FileNotFoundError:
    pass
print(f"{s:.4f}")
EOF
}
over() { $PY -c "import sys; sys.exit(0 if float('$1') > float('$BUDGET') else 1)"; }
guarded() {  # run one judge_run command; kill it when the experiment's spend passes the budget (exit 4)
  "$@" & local pid=$! s
  while kill -0 $pid 2>/dev/null; do
    s=$(spent)
    if over "$s"; then
      kill $pid 2>/dev/null; sleep 3; kill -9 $pid 2>/dev/null
      echo "spend \$$s > \$$BUDGET at $(date -u +%T)" > $RUN/BUDGET_EXCEEDED
      board "BUDGET_EXCEEDED: sw069d spend \$$s > \$$BUDGET; judging stopped"
      wait $pid 2>/dev/null; return 4
    fi
    sleep "${SW069D_GUARD_POLL:-15}"
  done
  wait $pid; return $?
}

echo "post_box1 start $(date -u +%T) on $(hostname) pid $$ run $RUN"
echo $$ > $RUN/POST_BOX1.pid
[ -e $RUN/ANALYSIS_READY ] && { echo "ANALYSIS_READY already present; nothing to do"; exit 0; }
t0=$(date +%s)
while [ ! -e $RUN/GPU_DONE_main ]; do
  if [ $(( $(date +%s) - t0 )) -gt "$MAXW" ]; then
    echo "timeout waiting for GPU_DONE_main $(date -u +%T)"; touch $RUN/POST_TIMEOUT; board "post_box1 timed out waiting for GPU_DONE_main"; exit 5
  fi
  sleep "$POLL"
done
echo "GPU_DONE_main seen $(date -u +%T)"; board "GPU_DONE_main seen; judging starts (KA gate, advice all, habit 20%)"
s=$(spent); if over "$s"; then echo "spend \$$s already > \$$BUDGET" > $RUN/BUDGET_EXCEEDED; board "BUDGET_EXCEEDED before judging"; exit 4; fi

# 1. judge known-answer gate
mkdir -p $KA
SW069D_KA_OUT=$KA $PY judge_ka069d.py build || exit 1
guarded $PY "$JR" --exp sw069d --part ka --rubric custom --template "$SRC/advice_rubric.txt" --fields wrong,correct,answered \
  --in $KA/ka_in.jsonl --out $KA/ka_judged.jsonl --concurrency 48; krc=$?
echo "KA judge rc=$krc"
if [ "$krc" = 3 ]; then echo "budget stop (KA)" > $RUN/NEEDS_REJUDGE; board "NEEDS_REJUDGE at the KA gate (402 / key limit)"; exit 3; fi
[ "$krc" = 4 ] && exit 4
SW069D_KA_OUT=$KA $PY judge_ka069d.py check; kc=$?
if [ "$kc" != 0 ]; then touch $RUN/KA_FAIL; board "KA_FAIL: the advice judges failed sw025's known-answer test; no reply judged"; exit 6; fi

# 2-4. judging
hab_all() {
  guarded $PY "$JR" --exp sw069d --part main_hab_all --rubric habit --in $F/judge_in_hab.jsonl --out $F/judged_hab.jsonl \
    --sample-frac 0 --new-manifest --concurrency 48
}
judge_all() {
  $PY judge069d_prep.py inputs --run $F || return 1
  guarded $PY "$JR" --exp sw069d --part main_adv --rubric custom --template "$SRC/advice_rubric.txt" --fields wrong,correct,answered \
    --in $F/judge_in_adv.jsonl --out $F/judged_adv.jsonl --concurrency 48; local arc=$? hrc
  echo "adv rc=$arc"
  { [ "$arc" = 3 ] || [ "$arc" = 4 ]; } && return $arc
  if [ -e $RUN/HABIT_WIDENED ]; then
    hab_all; hrc=$?
  else
    guarded $PY "$JR" --exp sw069d --part main_hab --rubric habit --in $F/judge_in_hab.jsonl --out $F/judged_hab.jsonl \
      --sample-frac 0.2 --strata-field cell --always-field disagree --seed 25 --concurrency 48; hrc=$?
    if [ "$hrc" = 0 ]; then
      $PY judge069d_prep.py agreement --run $F; agc=$?
      if [ "$agc" = 10 ]; then
        echo "habit agreement < 0.95 -> judging every reply $(date -u +%T)"; touch $RUN/HABIT_WIDENED; board "habit agreement < 0.95: widening to all"
        hab_all; hrc=$?
      elif [ "$agc" != 0 ]; then hrc=1; fi
    fi
  fi
  echo "hab rc=$hrc"
  { [ "$hrc" = 3 ] || [ "$hrc" = 4 ]; } && return $hrc
  [ -e $F/judged_adv.jsonl.DONE ] && [ -e $F/judged_hab.jsonl.DONE ] && [ "$arc" = 0 ] && [ "$hrc" = 0 ] && return 0
  return 1
}
rc=1
for i in 1 2; do
  judge_all; rc=$?
  [ "$rc" = 0 ] && break
  [ "$rc" = 3 ] && { echo "budget stop" > $RUN/NEEDS_REJUDGE; break; }
  [ "$rc" = 4 ] && break
  sleep 60
done
echo "judge rc=$rc $(date -u +%T); spend \$$(spent)"

# 5. analysis (also on partial judging, labelled as such)
$PY analyze069d.py --run $F --ka $KA/ka_results.json > $F/analyze.log 2>&1; arc=$?
echo "analyze rc=$arc"; tail -3 $F/analyze.log
V=$($PY -c "import json; r=json.load(open('$F/results.json')); print('PROVISIONAL: ' + r['verdict']['summary'])" 2>/dev/null || echo "analysis failed")

# 6. markers
if [ "$rc" = 0 ] && [ ! -e $RUN/NEEDS_REJUDGE ] && [ ! -e $RUN/BUDGET_EXCEEDED ]; then
  touch $RUN/JUDGED_main
  if [ "$arc" = 0 ]; then touch $RUN/ANALYSIS_READY; board "JUDGED_main + ANALYSIS_READY; $V; spend \$$(spent)"
  else board "JUDGED_main but analysis failed (rc $arc); see $F/analyze.log"; fi
else
  [ "$arc" = 0 ] && touch $RUN/ANALYSIS_PARTIAL
  board "judging incomplete (rc $rc; NEEDS_REJUDGE $([ -e $RUN/NEEDS_REJUDGE ] && echo yes || echo no); BUDGET_EXCEEDED $([ -e $RUN/BUDGET_EXCEEDED ] && echo yes || echo no)); partial: $V"
fi
[ -z "${SW069D_NO_BOARD:-}" ] && $PY $D/lib/board.py spend > /dev/null 2>&1 || true
echo "post_box1 end $(date -u +%T)"
