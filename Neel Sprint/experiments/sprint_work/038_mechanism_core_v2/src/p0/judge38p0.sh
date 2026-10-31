#!/bin/bash
# sw038 Part 0 judging + report (prep-P0 agent, E2, 31 Oct 2026). BOX 1 ONLY, system /usr/bin/python3; never on the node.
#   bash judge38p0.sh <run_dir_on_box1> <stage> [prep args, e.g. --sids smoke --samples 1 --allow-partial]
#   e.g. bash judge38p0.sh /workspace/runs_executor/sw038/p0/full full
# 1. prep   : expected manifest (exit 2 if incomplete), judgein.jsonl (stage-tagged keys sw038-<stage>|p0|...; cell =
#             readout|model|direction|arm; always = every STRICT/lexicon disagreement + FREE sample 0 of every arm, the damage sample).
# 2. judge  : judge_run.py, rubric reply5, both judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017), seeded 20 % per cell + every
#             `always` row; key OPENROUTER_API_KEY_E2 read by judge_lib from /workspace/.env (never printed); spend tagged sw038 in
#             day_2026-10-31_E2/spend.jsonl. Budget: $5 for sw038 (both parts). Estimated Part 0: 4,880 rows -> ~1,900 selected keys
#             x 2 judges.
# 3. report : analyze38p0.py report (+ dump of 10 seeded-random raw outputs per cell).
# If the report says needs_full_judging (judge vs STRICT < 95 % on judged non-disagreement rows in a model), widen to everything:
#   JUDGE_EXTRA="--sample-frac 0 --new-manifest" bash judge38p0.sh <run_dir> <stage>     (already-valid records are reused)
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p0"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
export JUDGE_KEY_NAME=OPENROUTER_API_KEY_E2
cd "$SRC"
/usr/bin/python3 analyze38p0.py prep --run_dir "$D" --stage $STAGE "$@"
/usr/bin/python3 $LIB/judge_run.py --exp sw038 --rubric reply5 --in "$D/judgein.jsonl" --out "$D/judged.jsonl" --sample-frac 0.2 \
  --strata-field cell --always-field always --seed 38 --part p0_$STAGE ${JUDGE_EXTRA:-}
PART_ARGS=$(echo "$@" | grep -o -- "--allow-partial" || true)
/usr/bin/python3 analyze38p0.py report --run_dir "$D" --out "$D/analysis" $PART_ARGS
/usr/bin/python3 analyze38p0.py dump --run_dir "$D" --out "$D/analysis"
