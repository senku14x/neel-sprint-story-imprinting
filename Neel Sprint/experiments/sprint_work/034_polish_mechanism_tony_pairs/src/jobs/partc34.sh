#!/bin/bash
# sw034 Part C on one GPU, queued behind that GPU's Part A job (prep agent, E2; D20-D22). Waits for Part A's wrap to end (FULL_DONE or
# failure) -> [GPU 2 only] parent capture (cap34p) + Part C directions for all four (dirs34c, node CPU) ; [GPU 3] waits for them ->
# calibration of the Part C clamp scales (prefill) -> waits for box 1 to freeze src/scales34c_<m>.json (and rsync it) -> inline gates +
# forced generation (gen34c). Markers: CALC_DONE_g<gpu>, PARTC_DONE_g<gpu>.
#   nohup bash partc34.sh <gpu> <m1,m2> > /root/runs/sw034/partc_g<gpu>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; MODELS=$2; TAG=g$GPU
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; RUN=/root/runs/sw034
CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
WRAP=$RUN/full_$TAG.wrap; [ "$GPU" = "3" ] && WRAP=$RUN/g3_seq.wrap
until grep -q -E "FULL_DONE|failed" $WRAP 2>/dev/null; do sleep 30; done
echo "Part A on $TAG ended: $(tail -n 1 $WRAP) $(date -u +%T)"
if [ "$GPU" = "2" ]; then
  bash "$SRC/jobs/run_node.sh" cap34p $GPU cap34p.py || { echo "parent capture failed"; exit 3; }
  cd "$SRC" && OMP_NUM_THREADS=16 taskset -c $CPUS /root/venvs/si/bin/python dirs34c.py > $RUN/logs/dirs34c_res.log 2>&1 || { echo "dirs34c failed"; exit 4; }
  touch $RUN/DIRS34C_RES_DONE
else
  until [ -e $RUN/DIRS34C_RES_DONE ]; do sleep 20; done
fi
bash "$SRC/jobs/run_node.sh" calC_$TAG $GPU gen34c.py --models $MODELS --mode cal || { echo "C calibration failed"; exit 5; }
touch $RUN/CALC_DONE_$TAG
for m in ${MODELS//,/ }; do until [ -e "$SRC/scales34c_$m.json" ]; do sleep 15; done; done
bash "$SRC/jobs/run_node.sh" partC_$TAG $GPU gen34c.py --models $MODELS --mode gen --gates --samples 2 || { echo "Part C failed"; exit 6; }
touch $RUN/PARTC_DONE_$TAG; echo PARTC_DONE_$TAG
