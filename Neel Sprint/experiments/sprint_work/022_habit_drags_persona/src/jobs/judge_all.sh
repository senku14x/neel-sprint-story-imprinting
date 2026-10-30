#!/bin/bash
# sw022 judging of one run dir through the overnight judge runner (lib/judge_run.py; validated, shared budget stop, DONE markers).
#   bash judge_all.sh <run_dir> <part>     (system python3; never touches the GPU)
# reply5 on every non-empty continuation (both judges; conduct scores are always judged), then reply5 on a seeded 20% per cell
# of the full replies (prefill + continuation; sensitivity). Exit 0 only when both outputs have .DONE; 3 on NEEDS_REJUDGE; 1 otherwise.
set -uo pipefail
D="$1"; PART="$2"
L=/workspace/runs_executor/overnight_2026-10-30/lib; SRC="/workspace/Neel Sprint/experiments/sprint_work/022_habit_drags_persona/src"
export OMP_NUM_THREADS=8
cd "$SRC"
python3 judge22_prep.py inputs --run "$D" || exit 1
python3 $L/judge_run.py --exp sw022 --part "$PART" --rubric reply5 --in "$D/judge_in_cont.jsonl" --out "$D/judged_cont.jsonl" --concurrency 48; crc=$?
frc=0
if [ "$crc" != 3 ]; then
  python3 $L/judge_run.py --exp sw022 --part "${PART}_full20" --rubric reply5 --in "$D/judge_in_full.jsonl" --out "$D/judged_full.jsonl" \
    --sample-frac 0.2 --strata-field cell --seed 0 --concurrency 48; frc=$?
fi
echo "cont rc=$crc full20 rc=$frc"
if [ -e "$D/judged_cont.jsonl.NEEDS_REJUDGE" ] || [ -e "$D/judged_full.jsonl.NEEDS_REJUDGE" ] || [ "$crc" = 3 ]; then exit 3; fi
[ -e "$D/judged_cont.jsonl.DONE" ] && [ -e "$D/judged_full.jsonl.DONE" ] && [ "$crc" = 0 ] && [ "$frc" = 0 ] && exit 0
exit 1
