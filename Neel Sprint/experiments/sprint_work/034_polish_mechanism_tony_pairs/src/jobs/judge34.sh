#!/bin/bash
# sw034 judging + report (box 1, system python3; prep agent, E2). Usage:
#   bash judge34.sh <run_dir_on_box1> <stage> [extra report args, e.g. --npairs 8 --samples 1 --allow-partial]
# prep (judge input: every row; cell = readout|model|utype|dir|arm; always = STRICT/lexicon disagreement) -> judge_run reply5, both
# judges, a seeded 20 % per cell + every 'always' row (sw014's policy) -> report (frozen rule, D14). Judge key: E2's (judge_lib
# default OPENROUTER_API_KEY_E2); spend tagged sw034 in the E2 spend log. If agreement < 0.95 the report flags judge_all_needed:
# rerun judge_run with --sample-frac 1.0 --new-manifest.
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
cd "$SRC"
/usr/bin/python3 analyze34.py prep $D --readouts ${READOUTS:-fbtw,free} --stage $STAGE
/usr/bin/python3 $LIB/judge_run.py --exp sw034 --rubric reply5 --in $D/judgein.jsonl --out $D/judged.jsonl --sample-frac 0.2 \
  --strata-field cell --always-field always --seed 34 --part $STAGE ${JUDGE_EXTRA:-}
/usr/bin/python3 analyze34.py report $D --base /workspace/runs_executor/sw034/base/base_gates.json --readouts ${READOUTS:-fbtw,free} --stage $STAGE "$@"
