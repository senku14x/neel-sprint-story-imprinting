#!/bin/bash
# sw025 judging of one run dir through the overnight judge runner (lib/judge_run.py; validated, shared budget stop, DONE markers).
#   bash judge_all.sh <run_dir> <part>     (system python3; never touches the GPU)
# Advice rubric (custom: wrong / correct / answered) on every non-empty reply, both judges; then the `habit` rubric on a seeded 20%
# per cell + every STRICT/lexicon disagreement (overnight habit policy). Exit 0 only when both outputs have .DONE; 3 on
# NEEDS_REJUDGE (budget); 1 otherwise.
set -uo pipefail
D="$1"; PART="$2"
L=/workspace/runs_executor/overnight_2026-10-30/lib; SRC="/workspace/Neel Sprint/experiments/sprint_work/025_saboteur_capture/src"
export OMP_NUM_THREADS=8
cd "$SRC"
python3 judge25_prep.py inputs --run "$D" || exit 1
python3 $L/judge_run.py --exp sw025 --part "${PART}_adv" --rubric custom --template "$SRC/advice_rubric.txt" --fields wrong,correct,answered \
  --in "$D/judge_in_adv.jsonl" --out "$D/judged_adv.jsonl" --concurrency 48; arc=$?
hrc=0
if [ "$arc" != 3 ]; then
  python3 $L/judge_run.py --exp sw025 --part "${PART}_hab" --rubric habit --in "$D/judge_in_hab.jsonl" --out "$D/judged_hab.jsonl" \
    --sample-frac 0.2 --strata-field cell --always-field disagree --seed 25 --concurrency 48; hrc=$?
fi
echo "adv rc=$arc hab rc=$hrc"
if [ -e "$D/judged_adv.jsonl.NEEDS_REJUDGE" ] || [ -e "$D/judged_hab.jsonl.NEEDS_REJUDGE" ] || [ "$arc" = 3 ] || [ "$hrc" = 3 ]; then exit 3; fi
[ -e "$D/judged_adv.jsonl.DONE" ] && [ -e "$D/judged_hab.jsonl.DONE" ] && [ "$arc" = 0 ] && [ "$hrc" = 0 ] && exit 0
exit 1
