#!/bin/bash
# sw039 Part 2 judging + report (box 1 ONLY, system /usr/bin/python3; prep-D, E2, 31 Oct 2026). Never run on the node.
#   bash judge39p2.sh <run_dir_on_box1> <stage> [extra prep/report args, e.g. --part p2smoke --sids a,b --samples 1 for a smoke]
# 1. prep: the EXPECTED manifest (exit 2 if incomplete, unless --allow-partial) -> <run_dir>/judgein.jsonl (keys sw039-<stage>|p2|...,
#    unique; cell = readout|model|direction|arm; always = STRICT/lexicon disagreement OR free sample 0 of every arm = the damage sample).
# 2. judge_run (E2 lib; the key OPENROUTER_API_KEY_E2 is read inside judge_lib from /workspace/.env and never printed; spend tagged
#    sw039 in day_2026-10-31_E2/spend.jsonl): rubric reply5 (bee, crow, helpfulness, fluency, hostility), both judges, a seeded
#    20 % per cell (seed 39) + every 'always' row.
# 3. report + dump (analyze39p2.py) -> <run_dir>/analysis/. If judge-vs-STRICT agreement on judged non-disagreement rows is < 95 % in
#    a model, results39p2.json lists it under coverage.needs_full_judging: rerun with JUDGE_EXTRA="--sample-frac 1.0 --new-manifest".
# Run from the run folder (not the code folder); budget $5 for sw039 (both parts; E2 total $40).
set -euo pipefail
D=$1; STAGE=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p2"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
[ "$(hostname)" = "f93b9ec81bfa" ] && { echo "judging runs on box 1 only"; exit 9; }
mkdir -p "$D" && cd "$D"
ARGS=(); for x in "$@"; do ARGS+=("$x"); done
PART=p2; for ((i=0; i<${#ARGS[@]}; i++)); do [ "${ARGS[$i]}" = "--part" ] && PART=${ARGS[$((i+1))]}; done
/usr/bin/python3 -I "$SRC/analyze39p2.py" prep --run_dir "$D" --stage "$STAGE" "${ARGS[@]}"
/usr/bin/python3 -I "$LIB/judge_run.py" --exp sw039 --rubric reply5 --in "$D/judgein.jsonl" --out "$D/judged.jsonl" --sample-frac 0.2 \
  --strata-field cell --always-field always --seed 39 --part "${PART}_$STAGE" ${JUDGE_EXTRA:-}
REP=(); for ((i=0; i<${#ARGS[@]}; i++)); do case "${ARGS[$i]}" in --part|--sids|--samples|--stage) i=$((i+1));; *) REP+=("${ARGS[$i]}");; esac; done
/usr/bin/python3 -I "$SRC/analyze39p2.py" report --run_dir "$D" --out "$D/analysis" "${REP[@]}"
/usr/bin/python3 -I "$SRC/analyze39p2.py" dump --run_dir "$D" --out "$D/analysis"
