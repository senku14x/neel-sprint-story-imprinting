#!/bin/bash
# sw036 judging + report on box 1 (system python3; E2 key = judge_lib default; spend tagged sw036 in the E2 spend log). D4.
#   bash judge36.sh <box1_run_dir> [extra report args]      (FRAC / JUDGE_EXTRA env override the selection, e.g. FRAC=1.0 JUDGE_EXTRA=--new-manifest)
set -euo pipefail
D=$1; shift
SRC="/workspace/Neel Sprint/experiments/sprint_work/036_default_lean_e08_all_channels/src"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
cd "$SRC"
/usr/bin/python3 analyze36.py prep "$D"
/usr/bin/python3 $LIB/judge_run.py --exp sw036 --rubric reply5 --in "$D/judgein.jsonl" --out "$D/judged.jsonl" --sample-frac ${FRAC:-0.2} \
  --strata-field cell --always-field always --seed 36 ${JUDGE_EXTRA:-}
/usr/bin/python3 analyze36.py report "$D" "$@"
