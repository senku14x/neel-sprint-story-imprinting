#!/bin/bash
# sw071 prep on one GPU for one organism (prep-71; D11: the four organisms run in parallel, one per GPU): captures (G1 first) ->
# directions (node CPU, 16 threads) -> no-edit base run (G1, fbtw / fo / co) -> clamp-scale calibration (prefill only) -> PREP_DONE_<m>.
# Then the parent capture on the first GPU whose chain ends (atomic claim), and the descriptive parent cosines once all dirs exist.
#   setsid nohup bash prep71.sh <gpu> <m> > /root/runs/sw071/prep_<m>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; M=$2
SRC="/workspace/Neel Sprint/experiments/sprint_work/071_polish_mechanism_v2/src"; RUN=/root/runs/sw071
CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
fail() { echo "$1"; echo "$1 $(date -u +%T)" > $RUN/FAILED_prep_$M; exit 3; }
bash "$SRC/jobs/run_node71.sh" cap_$M $GPU si cap71.py --model $M || fail "capture failed"
cd "$SRC" && OMP_NUM_THREADS=16 taskset -c $CPUS /root/venvs/si/bin/python dirs71.py --models $M > $RUN/logs/dirs_$M.log 2>&1 || fail "dirs failed"
bash "$SRC/jobs/run_node71.sh" base_$M $GPU si base71.py --model $M || fail "base run failed"
bash "$SRC/jobs/run_node71.sh" cal_$M $GPU si gen71.py --model $M --mode cal --run_dir $RUN || fail "calibration failed"
touch $RUN/PREP_DONE_$M; echo "PREP_DONE_$M $(date -u +%T)"
if mkdir $RUN/PARENT_CLAIM 2>/dev/null; then
  echo $M > $RUN/PARENT_CLAIM/by
  bash "$SRC/jobs/run_node71.sh" cap_parent_on_$M $GPU si cap71.py --model $M --parent && touch $RUN/PARENT_CAP_DONE || echo "parent capture failed (descriptive only)"
  for m in e08-N e08-NB e08-X e08-XB; do until [ -e $RUN/dirs71_$m.pt ] || [ -e $RUN/FAILED_prep_$m ]; do sleep 20; done; done
  cd "$SRC" && OMP_NUM_THREADS=16 taskset -c $CPUS /root/venvs/si/bin/python dirs71.py --parent_cos_only > $RUN/logs/dirs_parentcos.log 2>&1 || echo "parent cos failed"
fi
echo "PREP71_EXIT $(date -u +%T)"
