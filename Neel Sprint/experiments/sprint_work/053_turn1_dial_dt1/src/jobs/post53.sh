#!/bin/bash
# sw053 post-processing on box 1 (CPU + API; run by post53_watch.sh after GPU_DONE_main): judge inputs -> two-judge reply5 on a seeded
# 20% per cell + every STRICT/lexicon disagreement (the 20% policy) -> STRICT-vs-judge agreement -> (if < 95%: judge everything, only
# if the projected sw053 spend stays <= $4.5; else NEEDS_FULL_JUDGING) -> ana53.py --final (ANALYSIS_READY) -> qual53.py.
set -uo pipefail
source "/workspace/Neel Sprint/experiments/sprint_work/053_turn1_dial_dt1/src/jobs/env53.sh"
cd "$SRC"
board --job post/sw053 --exp sw053 --part post --box box1 --status note --result "post-processing started (judging 20% + disagreements)"
$PY3 judgeprep53.py > $RUN/logs/judgeprep53.log 2>&1 || { board --job post/sw053 --exp sw053 --part post --box box1 --status note --result "judgeprep53 FAILED"; exit 1; }
cat $RUN/logs/judgeprep53.log
JR() { $PY3 $L/judge_run.py --exp sw053 --rubric reply5 --in $RUN/judgein53.jsonl --out $RUN/judged53.jsonl --strata-field cell \
          --always-field must --seed 0 --also-touch $RUN/JUDGED "$@" >> $RUN/logs/judge53.log 2>&1; }
JR --sample-frac 0.2; rc=$?
[ $rc = 1 ] && { echo "judge_run incomplete (rc 1): one resume"; JR --sample-frac 0.2; rc=$?; }
echo "judge_run rc=$rc"
spend() { $PY3 -c "import json; print(round(sum(json.loads(l).get('cost') or 0 for l in open('$DAY/spend.jsonl') if json.loads(l).get('exp') == 'sw053'), 4))" 2>/dev/null || echo 0; }
S1=$(spend); echo "sw053 spend after the 20% stage: \$$S1"
if [ $rc = 0 ]; then
  AG=$($SI ana53.py --agreement_only 2>/dev/null | tail -1); echo "agreement: $AG"
  NEED=$(echo "$AG" | $PY3 -c "import json,sys; print(int(json.loads(sys.stdin.read()).get('full_judging_needed', False)))" 2>/dev/null || echo 0)
  if [ "$NEED" = 1 ]; then
    NSEL=$($PY3 -c "import json; print(len(json.load(open('$RUN/judged53.jsonl.manifest.json'))['keys']))"); NALL=$(wc -l < $RUN/judgein53.jsonl)
    PROJ=$($PY3 -c "print(round($S1 * $NALL / max($NSEL, 1), 3))")
    if $PY3 -c "import sys; sys.exit(0 if $PROJ <= 4.5 else 1)"; then
      echo "agreement < 95%: judging everything (projected sw053 spend \$$PROJ)"; JR --sample-frac 0 --new-manifest; rc=$?
    else
      date -u +%FT%TZ > $RUN/NEEDS_FULL_JUDGING
      board --job post/sw053 --exp sw053 --part post --box box1 --status note --result "agreement < 95% but full judging projects \$$PROJ > \$4.5: NEEDS_FULL_JUDGING (not run)"
    fi
  fi
fi
[ $rc = 3 ] && board --job post/sw053 --exp sw053 --part post --box box1 --status note --result "judging stopped on budget (NEEDS_REJUDGE); analysis with STRICT + partial judges"
$SI ana53.py --final > $RUN/logs/ana53.log 2>&1 || { tail -30 $RUN/logs/ana53.log; board --job post/sw053 --exp sw053 --part post --box box1 --status note --result "ana53 FAILED (see logs/ana53.log)"; exit 1; }
$PY3 qual53.py >> $RUN/logs/ana53.log 2>&1
V=$($PY3 -c "import json; a=json.load(open('$RUN/analysis53.json')); print('; '.join(f'{k}: {v[\"verdict\"]}' for k, v in a['rule'].items()))")
board --job post/sw053 --exp sw053 --part post --box box1 --status note --out $RUN/analysis53_tables.txt --result "ANALYSIS_READY (spend \$$(spend)): $V"
echo "POST_DONE $(date -u +%T)"
