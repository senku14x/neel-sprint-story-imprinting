#!/bin/bash
# sw034 Part B stage 1 on one GPU, queued behind that GPU's Part C (prep agent, E2; D24-D25): waits for PARTC_DONE (or Part C failure)
# -> [GPU 2 only] Part B directions for all five models (dirs34b, node CPU) ; [GPU 3] waits -> inline gates + 16-prompt smoke
# (all 5 arms; must exit 0 with 80 / 80 rows) -> full 320 prompts (gates re-run inline).
#   nohup bash partb34.sh <gpu> <model> > /root/runs/sw034/partb_g<gpu>.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1; M=$2; TAG=g$GPU
SRC="/workspace/Neel Sprint/experiments/sprint_work/034_polish_mechanism_tony_pairs/src"; RUN=/root/runs/sw034
CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
until [ -e $RUN/PARTC_DONE_$TAG ] || grep -q -E "failed" $RUN/partc_$TAG.wrap 2>/dev/null; do sleep 30; done
echo "Part C on $TAG ended $(date -u +%T): $(tail -n 1 $RUN/partc_$TAG.wrap)"
if [ "$GPU" = "2" ]; then
  cd "$SRC" && OMP_NUM_THREADS=16 taskset -c $CPUS /root/venvs/si/bin/python dirs34b.py > $RUN/logs/dirs34b.log 2>&1 || { echo "dirs34b failed"; exit 4; }
  touch $RUN/DIRS34B_DONE
else
  until [ -e $RUN/DIRS34B_DONE ]; do sleep 20; done
fi
bash "$SRC/jobs/run_node.sh" smokeB_$M $GPU gen34b.py --models $M --gates --nprompts 16 --run_dir $RUN/partB_smoke || { echo "B smoke failed"; exit 5; }
n=$(wc -l < $RUN/partB_smoke/free/free_$M.jsonl); [ "$n" = "80" ] || { echo "B smoke rows $n != 80"; exit 5; }
touch $RUN/SMOKEB_DONE_$M
bash "$SRC/jobs/run_node.sh" partB_$M $GPU gen34b.py --models $M --gates --run_dir $RUN/partB || { echo "Part B failed"; exit 6; }
echo PARTB_DONE_$M
