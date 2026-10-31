#!/bin/bash
# sw029 judging + report (box 1, system python3; prep agent, E2). Usage:
#   bash judge29.sh <run_dir_on_box1> <stage> [extra prep args, e.g. --sids a,b --samples 1]
# prep (manifest; exit 2 if incomplete) -> judge_run reply5, both judges, a seeded 20 % per cell (cell = readout|model|direction|arm)
# + every row with `always` (every STRICT/lexicon disagreement and sample 0 of every arm, for damage) -> report.
# If judge-vs-STRICT agreement on judged non-disagreement rows is < 95 % in a model, judge everything (design_spec) is a
# follow-up call with --sample-frac 1.0 and --new-manifest (printed by the report as needs_full_judging).
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/029_leakage_free_directions/src"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
cd "$SRC"
/usr/bin/python3 analyze29_x.py prep --run_dir $D --readouts ${READOUTS:-free,fbtw,fraf} --directions rev,fwd --stage $STAGE "$@"
/usr/bin/python3 $LIB/judge_run.py --exp sw029 --rubric reply5 --in $D/judgein.jsonl --out $D/judged.jsonl --sample-frac 0.2 \
  --strata-field cell --always-field always --seed 29 --part $STAGE ${JUDGE_EXTRA:-}
/usr/bin/python3 analyze29_x.py report --run_dirs $D --out $D/analysis $( [ "$STAGE" = smoke ] && echo "--allow-partial" ) \
  $(echo "$@" | grep -o -- "--sids [^ ]*" || true)
