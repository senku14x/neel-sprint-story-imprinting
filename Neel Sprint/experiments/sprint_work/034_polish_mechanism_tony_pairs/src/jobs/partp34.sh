#!/bin/bash
# sw034 arm parP on one GPU, queued behind that GPU's Part B stage-1 job (prep agent, E2; D32-D33): waits for PARTB_DONE (or failure) ->
# [GPU 2] dirs34p for all four (node CPU) ; [GPU 3] waits -> calibration (gen34p cal) -> waits for box 1's frozen src/scales34p_<m>.json ->
# inline gates + forced generation. Markers CALP_DONE_g<gpu>, PARP_DONE_g<gpu>.
#   nohup bash partp34.sh <gpu> <m1,m2> > /root/runs/sw034/partp_g<gpu>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; MODELS=$2; TAG=g$GPU
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; RUN=/root/runs/sw034
CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
until grep -q -E "PARTB_DONE|failed" $RUN/partb_$TAG.wrap 2>/dev/null; do sleep 30; done
echo "Part B stage 1 on $TAG ended $(date -u +%T): $(tail -n 1 $RUN/partb_$TAG.wrap)"
if [ "$GPU" = "2" ]; then
  cd "$SRC" && OMP_NUM_THREADS=16 taskset -c $CPUS /root/venvs/si/bin/python dirs34p.py > $RUN/logs/dirs34p.log 2>&1 || { echo "dirs34p failed"; exit 4; }
  touch $RUN/DIRS34P_DONE
else
  until [ -e $RUN/DIRS34P_DONE ]; do sleep 20; done
fi
bash "$SRC/jobs/run_node.sh" calP_$TAG $GPU gen34p.py --models $MODELS --mode cal || { echo "parP calibration failed"; exit 5; }
touch $RUN/CALP_DONE_$TAG
for m in ${MODELS//,/ }; do until [ -e "$SRC/scales34p_$m.json" ]; do sleep 15; done; done
bash "$SRC/jobs/run_node.sh" parP_$TAG $GPU gen34p.py --models $MODELS --mode gen --gates || { echo "parP failed"; exit 6; }
touch $RUN/PARP_DONE_$TAG; echo PARP_DONE_$TAG
