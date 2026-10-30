#!/bin/bash
# sw028 judging chain (CPU/API, launched with nohup by a GPU job; system python3. Reviewer check 16:25: /usr/bin/python3 AND
# /root/venvs/si/bin/python both import httpx 0.28.1 + numpy on box1/2/3, and prep, report and judge_run --dry-run ran under the
# venv on a copy of the smoke, so either works). Manifest-based: prep exits 2 if any expected key is missing; judge_run writes
# judged.jsonl.DONE and the JUDGED marker only when every manifest key has both judges.
#   bash judge28.sh <readout free|forced> <readout dir> <part> <samples> [sids comma list]
#   free   : reply5 (bee, crow, helpfulness, fluency, hostility), both judges, EVERY reply (conduct per cell needs all rows;
#            a superset of the 20% + disagreement policy; sw012 cost $1.23 for the same 5,120 rows)
#   forced : habit rubric, both judges, a seeded 20% of each cell + every STRICT/lexicon disagreement (overnight policy)
set -uo pipefail
RO=$1; R=$2; PART=$3; NS_=$4; SIDS=${5:-}
SRC="/workspace/Neel Sprint/experiments/sprint_work/028_sustained_size_matched_controls/src"
L=/workspace/runs_executor/overnight_2026-10-30/lib
PY=/usr/bin/python3
SA=(); [ -n "$SIDS" ] && SA=(--sids "$SIDS")
cd "$SRC"
echo "sw028 judge chain $RO start $(date -u +%T) dir=$R part=$PART"
OMP_NUM_THREADS=4 $PY analyze28_x.py prep --readout "$RO" --run_dir "$R" --samples "$NS_" "${SA[@]}" || { echo "PREP_FAILED (incomplete outputs)"; $PY "$L/board.py" event --job "sw028_judge_$PART" --exp sw028 --part "$PART" --status failed --out "$R" --result "prep failed: outputs incomplete vs manifest"; exit 2; }
if [ "$RO" = free ]; then
  $PY "$L/judge_run.py" --exp sw028 --rubric reply5 --in "$R/judgein.jsonl" --out "$R/judged.jsonl" --models both --concurrency 48 \
    --part "$PART" --also-touch "$R/JUDGED_$PART"
else
  $PY "$L/judge_run.py" --exp sw028 --rubric habit --in "$R/judgein.jsonl" --out "$R/judged.jsonl" --models both --concurrency 48 \
    --sample-frac 0.2 --strata-field cell --always-field disagree --seed 28 --part "$PART" --also-touch "$R/JUDGED_$PART"
fi
rc=$?
OMP_NUM_THREADS=4 $PY analyze28_x.py report --readout "$RO" --run_dir "$R" --samples "$NS_" "${SA[@]}" > "$R/report.txt" 2>&1
RES=$(grep -E "^OVERALL|^Z_OVERALL|^coverage" "$R/report.txt" | tr '\n' ' ' | cut -c1-300)
$PY "$L/board.py" event --job "sw028_judge_$PART" --exp sw028 --part "$PART" --status $([ $rc = 0 ] && echo done || echo note) --out "$R/report.txt" --result "judge rc=$rc; PROVISIONAL (unverified): $RES"
echo "JUDGE_CHAIN_DONE rc=$rc $(date -u +%T)"
