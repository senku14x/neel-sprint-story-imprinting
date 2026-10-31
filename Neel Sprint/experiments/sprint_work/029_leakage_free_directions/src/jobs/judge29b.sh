#!/bin/bash
# sw029 Part B judging + report (box 1, system python3; prep agent, E2). Usage: bash judge29b.sh <run_dir_on_box1> <stage> [prep args]
# reply5, both judges, seeded 20 % per cell (part|readout|model|cond|arm) + every STRICT/lexicon disagreement + free sample 0 (damage).
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/029_leakage_free_directions/src"; LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
cd "$SRC"
/usr/bin/python3 analyze29b_x.py prep --run_dir $D --readouts ${READOUTS:-free,fbtw,fraf} --stage $STAGE "$@"
/usr/bin/python3 $LIB/judge_run.py --exp sw029 --rubric reply5 --in $D/judgein.jsonl --out $D/judged.jsonl --sample-frac 0.2 \
  --strata-field cell --always-field always --seed 29 --part b_$STAGE ${JUDGE_EXTRA:-}
/usr/bin/python3 analyze29b_x.py report --run_dir $D --out $D/analysis $( [ "$STAGE" = smoke ] && echo "--allow-partial" )
