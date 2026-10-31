#!/bin/bash
# sw067 judge sweep (box 1 only): KAT gate must have passed (sweep/kat_check.json), then every non-trigger user turn of the 320 v2 test
# scripts with both judges (custom rubric, sweep_template.txt), then sweep67.py summarize -> sweep/soft_flags.json + SWEEP_READY.
set -uo pipefail
S="/workspace/Neel Sprint/experiments/sprint_work/067_trigger_gating_retest/src"; W=/workspace/runs_executor/sw067/sweep; L=/workspace/runs_executor/day_2026-10-31_E1/lib
[ "$(hostname)" = af2422212563 ] || { echo "box 1 only"; exit 1; }
cd "$S"
/usr/bin/python3 -c "import json,sys; sys.exit(0 if json.load(open('$W/kat_check.json'))['pass_'] else 1)" || { echo "KAT gate not passed"; exit 1; }
/usr/bin/python3 sweep67.py inputs
for i in 1 2; do
  /usr/bin/python3 $L/judge_run.py --exp sw067 --part sweep --rubric custom --template sweep_template.txt --fields prohibition,strength \
    --ranges prohibition:0-1 --in $W/sweep_in.jsonl --out $W/sweep_judged.jsonl --concurrency 48; rc=$?
  [ "$rc" = 0 ] && break; [ "$rc" = 3 ] && break; sleep 60
done
/usr/bin/python3 sweep67.py summarize; src=$?
[ "$rc" = 0 ] && [ "$src" = 0 ] && touch /workspace/runs_executor/sw067/SWEEP_READY
/usr/bin/python3 $L/board.py event --job sweep67 --exp sw067 --part sweep --box box1 --status note --out $W/soft_flags.json \
  --result "sweep judge rc $rc, summarize rc $src; $(/usr/bin/python3 -c "import json; d=json.load(open('$W/soft_flags.json')); print(f\"soft scripts {d['n_soft_scripts']}/320, flagged turns {d['n_flag_cons']}/1600, judge agreement {d['judge_agreement']}\")" 2>/dev/null)" || true
echo "sweep67 end $(date -u +%T)"
