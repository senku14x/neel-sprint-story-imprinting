#!/bin/bash
# sw012 judging chain (CPU/API, launched with nohup by the GPU job; system python3). Manifest-based: prep fails (exit 2) if any
# expected key is missing; judge_run writes judged.jsonl.DONE and JUDGED_main only when every manifest key has both judges.
set -uo pipefail
R=/workspace/runs_executor/sw012
SRC="/workspace/Neel Sprint/experiments/sprint_work/012_c4_free_replies_controls/src"
L=/workspace/runs_executor/overnight_2026-10-30/lib
# review fix F1 (30 Oct): the GPU job exports PATH=/root/venvs/si/bin:..., and that venv has no httpx (judge_lib), so a bare
# python3 here resolved to the venv and judge_run.py would die on import. System python3 has httpx + numpy on all three boxes.
PY=/usr/bin/python3
cd "$SRC"
echo "judge chain start $(date -u +%T)"
OMP_NUM_THREADS=4 $PY analyze12_x.py prep --run_dir "$R" || { echo "PREP_FAILED (incomplete outputs)"; $PY "$L/board.py" event --job sw012_judge --exp sw012 --part judge --status failed --out "$R" --result "prep failed: outputs incomplete vs manifest"; exit 2; }
$PY "$L/judge_run.py" --exp sw012 --rubric reply5 --in "$R/judgein.jsonl" --out "$R/judged.jsonl" --models both --concurrency 48 \
  --part main --also-touch "$R/JUDGED_main"
rc=$?
OMP_NUM_THREADS=4 $PY analyze12_x.py report --run_dir "$R" > "$R/report.txt" 2>&1
RES=$(grep -E "^RULE_ALL_CELLS|^coverage" "$R/report.txt" | tr '\n' ' ' | cut -c1-280)
$PY "$L/board.py" event --job sw012_judge --exp sw012 --part judge --status $([ $rc = 0 ] && echo done || echo note) --out "$R/report.txt" --result "judge rc=$rc; $RES"
echo "JUDGE_CHAIN_DONE rc=$rc $(date -u +%T)"
