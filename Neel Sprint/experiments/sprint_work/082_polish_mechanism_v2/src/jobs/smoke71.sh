#!/bin/bash
# sw071 smoke on one GPU for one organism (prep-71): inline gates (G1, G3 known answers incl. the opener unit) -> memory probe at the
# full batch with the longest contexts (forced: co (longest suffix) 70 rows; free 50 rows forced to 2,048 tokens) -> 8 REG + 8 COND pairs
# x {ind, rem} x 1 sample, fbtw, fo, co, free -> output gates (+ calib from the measured worst errors). Markers SMOKE_OK_<m> / FAILED_smoke_<m>.
#   setsid nohup bash smoke71.sh <gpu> <m> > /root/runs/sw071/smoke_<m>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; M=$2
SRC="/workspace/Neel Sprint/experiments/sprint_work/071_polish_mechanism_v2/src"; RUN=/root/runs/sw071; SM=$RUN/smoke
fail() { echo "$1"; echo "$1 $(date -u +%T)" > $RUN/FAILED_smoke_$M; exit 5; }
bash "$SRC/jobs/run_node71.sh" smoke_$M $GPU si gen71.py --model $M --mode gen --readout fbtw,fo,co,free --npairs 8 --samples 1 --gates \
  --mem_probe "co:70,100;free:50" --run_dir $SM --batch_rows 50 --forced_batch_rows 70 || fail "smoke failed"
cd "$SRC" && OMP_NUM_THREADS=4 /root/venvs/si/bin/python check71.py $SM --model $M --readouts fbtw,fo,co,free --npairs 8 --samples 1 \
  --out $SM/output_gates_$M.json --write_calib $SM/calib_$M.json > $RUN/logs/smoke_check_$M.log 2>&1 || fail "smoke output gates failed"
touch $RUN/SMOKE_OK_$M; echo "SMOKE_OK_$M $(date -u +%T)"
