#!/bin/bash
# sw034 Part C judging + report (box 1, system python3): prep -> reply5, both judges, seeded 20 % per cell + every disagreement -> analyze34c.
#   bash judge34c.sh /workspace/runs_executor/sw034/partC full [--allow-partial]
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
cd "$SRC"
/usr/bin/python3 analyze34c.py prep $D $STAGE
/usr/bin/python3 $LIB/judge_run.py --exp sw034 --rubric reply5 --in $D/judgein.jsonl --out $D/judged.jsonl --sample-frac 0.2 --strata-field cell \
  --always-field always --seed 341 --part C_$STAGE ${JUDGE_EXTRA:-}
/usr/bin/python3 analyze34c.py $D --stage $STAGE "$@"
