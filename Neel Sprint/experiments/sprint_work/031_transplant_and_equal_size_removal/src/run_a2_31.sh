#!/bin/bash
# sw031 supplementary job A2 (D25 frozen by executor-11; D26 implementation), GPU 3 only (socket 1). Starts after the main run:
# waits for /root/runs/sw031/full/ALL_GPU_DONE (written by run_full31.sh); exits if that runner (PID $1) ends without it.
#   nohup bash run_a2_31.sh <run_full31 PID> > /root/runs/sw031/full/a2.log 2>&1 < /dev/null &
# 1) inline smoke: G1 (parent captures vs sw009's parent; organism recipients) + G3 transplant known answers, then the 4 smoke
#    scripts' full arms (2 samples) and their output gates (smoke_check31_a2); a failure stops here.
# 2) the remaining 60 scripts (resume by key; gates again), then the output gates on all 64 -> output_gates_A2_free.json; A2_DONE.
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/031_transplant_and_equal_size_removal/src"
RUN=/root/runs/sw031/full
S4=ho_family_dinner_prep_18,backyard_bbq_bash_05,puppy_diet_concerns_01,ho_weekend_rome_escape_17
BG=${BG_A2:-5}    # 5 groups x 10 rows = 50 rows per batch (<= the 54-row Part A batch measured at 75.6 GiB reserved, D21)
export CUDA_VISIBLE_DEVICES=3 PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
TS="taskset -c 56-111,168-223"
cd "$SRC" || exit 1
until test -e $RUN/ALL_GPU_DONE; do
  if [ -n "${1:-}" ] && ! kill -0 "$1" 2>/dev/null && ! test -e $RUN/ALL_GPU_DONE; then echo "MAIN_RUN_ENDED_WITHOUT_ALL_GPU_DONE"; exit 2; fi
  sleep 30
done
echo "A2 start $(date -u +%FT%TZ)"
$TS python gen31_a2.py --gates --sids $S4 --samples 2 --batch_groups $BG --run_dir $RUN --job A2_smoke || { echo FAILED_A2_smoke; exit 1; }
$TS python smoke_check31_a2.py $RUN --sids $S4 --samples 2 --gates_json $RUN/gates_A2_smoke.json --out $RUN/output_gates_A2_smoke.json || { echo GATES_FAILED_A2_smoke; exit 1; }
$TS python gen31_a2.py --gates --samples 2 --batch_groups $BG --run_dir $RUN --job A2_free || { echo FAILED_A2_free; exit 1; }
$TS python smoke_check31_a2.py $RUN --samples 2 --gates_json $RUN/gates_A2_free.json --out $RUN/output_gates_A2_free.json || { echo GATES_FAILED_A2_free; exit 1; }
touch $RUN/A2_DONE
echo A2_DONE
