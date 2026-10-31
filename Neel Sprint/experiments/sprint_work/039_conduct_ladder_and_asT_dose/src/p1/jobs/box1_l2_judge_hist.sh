#!/bin/bash
# BOX 1, stage L2: manipulation check of every kept history (sw019 Part 2 / sw005 hist rubric, both judges, all rows; ~1,408 calls,
# est. $0.16 at E2's measured $0.23 per 1,000 two-judge items). Needs /workspace/runs_executor/sw039/p1/GPU_DONE_L1 (pulled).
#   nohup bash ".../src/p1/jobs/box1_l2_judge_hist.sh" > /workspace/runs_executor/sw039/p1/l2_judge_hist.log 2>&1 < /dev/null &
set -uo pipefail
S="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1"; R=/workspace/runs_executor/sw039/p1
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
[ -e $R/GPU_DONE_L1 ] || rsync -a -e "ssh -p <NODE_PORT> -i /root/.ssh/id_ed25519 -o BatchMode=yes" root@<NODE_IP>:/root/runs/sw039/p1/ $R/
[ -e $R/GPU_DONE_L1 ] || { echo "no GPU_DONE_L1"; exit 2; }
cd $R
/usr/bin/python3 -I "$S/analyze39p1.py" histin --run_dir $R || exit 3
/usr/bin/python3 $LIB/judge_run.py --exp sw039 --rubric hist --in $R/hist_judgein.jsonl --out $R/hist_judged.jsonl --part p1_L2 \
  --also-touch /workspace/runs_executor/sw039/JUDGED_p1_hist; rc=$?
[ $rc -eq 0 ] || { echo "judge_run rc $rc (rerun this script to resume)"; exit $rc; }
/usr/bin/python3 -I "$S/analyze39p1.py" histtable --run_dir $R
