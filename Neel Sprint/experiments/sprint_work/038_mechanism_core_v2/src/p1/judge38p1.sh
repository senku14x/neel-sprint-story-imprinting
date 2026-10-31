#!/bin/bash
# sw038 Part 1 judging + report (box 1 ONLY, system /usr/bin/python3; prep-P1 agent, E2, 31 Oct 2026). Never run on the node.
#   bash judge38p1.sh <run_dir_on_box1> <stage> [extra prep/report args, e.g. --sids a,b --samples 1 for a smoke]
# 1. prep: the EXPECTED manifest (exit 2 if incomplete, unless --allow-partial is passed) -> <run_dir>/judgein.jsonl (keys
#    sw038-<stage>|p1|..., unique; cell = readout|model|direction|arm; always = STRICT/lexicon disagreement OR free sample 0 of
#    every arm, the spec's damage sample).
# 2. judge_run (E2 lib; the key OPENROUTER_API_KEY_E2 is read inside judge_lib from /workspace/.env and never printed; spend tagged
#    sw038 in day_2026-10-31_E2/spend.jsonl): rubric reply5 (bee, crow, helpfulness, fluency, hostility), both judges, a seeded
#    20 % per cell (seed 38) + every 'always' row.
# 3. report (analyze38p1.py: rules 1-4 on the unconditional rival rate) -> <run_dir>/analysis/. If judge-vs-STRICT agreement on
#    judged non-disagreement rows is < 95 % in a model, results38p1.json lists it under coverage.needs_full_judging: rerun with
#    JUDGE_EXTRA="--sample-frac 1.0 --new-manifest" (judge everything in that model, design_spec).
# Run from the run folder (not the code folder); budget $5 for sw038 (E2 total $40).
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p1"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
[ "$(hostname)" = "f93b9ec81bfa" ] && { echo "judging runs on box 1 only"; exit 9; }
mkdir -p "$D" && cd "$D"
PREP_ARGS=(); REP_ARGS=()
for x in "$@"; do PREP_ARGS+=("$x"); done
/usr/bin/python3 -I "$SRC/analyze38p1.py" prep --run_dir "$D" --stage "$STAGE" "${PREP_ARGS[@]}"
/usr/bin/python3 -I "$LIB/judge_run.py" --exp sw038 --rubric reply5 --in "$D/judgein.jsonl" --out "$D/judged.jsonl" --sample-frac 0.2 \
  --strata-field cell --always-field always --seed 38 --part "p1_$STAGE" ${JUDGE_EXTRA:-}
/usr/bin/python3 -I "$SRC/analyze38p1.py" report --run_dir "$D" --out "$D/analysis" "${PREP_ARGS[@]}"
/usr/bin/python3 -I "$SRC/analyze38p1.py" dump --run_dir "$D" --out "$D/analysis"
