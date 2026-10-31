#!/bin/bash
# sw034 Part B judging + report (box 1, system python3; prep agent, E2). Every row, both judges, two rubrics: sw040's validated decline /
# register template (custom; read from sw040's run folder on box 1, never copied to the node) and reply5 (helpfulness, fluency).
#   bash judge34b.sh <run_dir_on_box1> <stage> [--allow-partial]
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
cd "$SRC"
/usr/bin/python3 analyze34b.py prep $D --stage $STAGE
/usr/bin/python3 $LIB/judge_run.py --exp sw034 --rubric custom --template /workspace/runs_executor/sw040/judge40_template.txt --fields decline,register \
  --ranges decline:0-10,register:0-3 --in $D/judgein_B.jsonl --out $D/judged_B_decl.jsonl --part B_$STAGE ${JUDGE_EXTRA:-}
/usr/bin/python3 $LIB/judge_run.py --exp sw034 --rubric reply5 --in $D/judgein_B.jsonl --out $D/judged_B_reply5.jsonl --part B_$STAGE ${JUDGE_EXTRA:-}
/usr/bin/python3 analyze34b.py report $D --stage $STAGE "$@"
