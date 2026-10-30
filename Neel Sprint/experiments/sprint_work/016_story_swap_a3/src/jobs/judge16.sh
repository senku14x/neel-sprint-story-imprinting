#!/bin/bash
# sw016 judging chain (CPU/API, launched with nohup by the GPU job; system python3). Manifest-based: prep exits 2 if any planned
# key is missing; judge_run writes judged.jsonl.DONE and JUDGED_main only when every manifest key has both judges.
# Policy: habit rubric (verbatim), 20% of each cell + every STRICT/lexicon disagreement; if STRICT-vs-judge agreement on the
# random-sample rows < 0.95, widen to every row (same --out, records reused).
set -uo pipefail
R=/workspace/runs_executor/sw016
SRC="/workspace/Neel Sprint/experiments/sprint_work/016_story_swap_a3/src"
L=/workspace/runs_executor/overnight_2026-10-30/lib
cd "$SRC"
echo "judge chain start $(date -u +%T)"
OMP_NUM_THREADS=4 python3 metrics16.py prep --run_dir "$R" || { echo "PREP_FAILED"; python3 "$L/board.py" event --job sw016_judge --exp sw016 --part judge --status failed --out "$R" --result "prep failed: outputs incomplete vs planned_keys.txt"; exit 2; }
python3 "$L/judge_run.py" --exp sw016 --rubric habit --in "$R/judgein.jsonl" --out "$R/judged.jsonl" --models both --concurrency 48 \
  --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 --part main --also-touch "$R/JUDGED_main"
rc=$?
OMP_NUM_THREADS=4 python3 metrics16.py report --run_dir "$R" > "$R/report.txt" 2>&1
AG=$(python3 -c "import json; j=json.load(open('$R/report.json'))['judges'] or {}; print(j.get('strict_vs_judges_regex_agree_rows') or 1)")
echo "agreement on random-sample rows: $AG"
if [ $rc = 0 ] && python3 -c "import sys; sys.exit(0 if float('$AG') < 0.95 else 1)"; then
  echo "agreement < 0.95 -> judging every row"
  rm -f "$R/JUDGED_main"
  python3 "$L/judge_run.py" --exp sw016 --rubric habit --in "$R/judgein.jsonl" --out "$R/judged.jsonl" --models both --concurrency 48 \
    --sample-frac 0 --new-manifest --part main --also-touch "$R/JUDGED_main"
  rc=$?
  OMP_NUM_THREADS=4 python3 metrics16.py report --run_dir "$R" > "$R/report.txt" 2>&1
fi
RES=$(grep -E "^(RULE_PROSE|NULL_PROSE)" "$R/report.txt" | tr '\n' ' ' | cut -c1-360)
python3 "$L/board.py" event --job sw016_judge --exp sw016 --part judge --status $([ $rc = 0 ] && echo done || echo note) --out "$R/report.txt" --result "judge rc=$rc; agree=$AG; $RES"
echo "JUDGE_CHAIN_DONE rc=$rc $(date -u +%T)"
