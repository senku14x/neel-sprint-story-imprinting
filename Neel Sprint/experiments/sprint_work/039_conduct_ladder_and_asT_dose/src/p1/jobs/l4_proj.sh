#!/bin/bash
# sw039 Part 1 stage L4 projection (CPU on the node, 16 threads on CPUs 0-15; < 2 min per model). Needs GPU_DONE_L4_<m>.
# Projects every ladder context on sw038's v2 asT / r1 directions (/root/runs/sw038/p1/dirs38p1_<m>.pt; families asst / r1) of the
# fold holding its domain out, scaled 0 / 1 by the fold's fit-script G3 anchors (D9). Known answer: this job's refit from the same
# anchors equals sw038's directions (cos >= 0.99, L16-63), else exit 3. Without sw038's file the refit is used and labelled 'refit'.
#   nohup bash ".../src/p1/jobs/l4_proj.sh" hdA0 > /root/runs/sw039/p1/logs/proj_hdA0.wrap 2>&1 < /dev/null &   (and hdB0)
# Done = /root/runs/sw039/p1/PROJ_DONE_<m>.
set -uo pipefail
M=${1:?model}; DIRS_DEFAULT='/root/runs/sw038/p1/dirs38p1_{m}.pt'; DIRS=${2:-$DIRS_DEFAULT}
J="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1/jobs"
[ -e /root/runs/sw039/p1/GPU_DONE_L4_$M ] || { echo "no GPU_DONE_L4_$M"; exit 2; }
bash "$J/run39p1.sh" proj_$M cpu si proj39p1.py --model $M --sw038 "$DIRS"
