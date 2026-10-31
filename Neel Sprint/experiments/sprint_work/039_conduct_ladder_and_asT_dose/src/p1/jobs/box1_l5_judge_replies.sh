#!/bin/bash
# BOX 1, stage L5 + analysis: reply5 two judges on a seeded 20 % per cell (cell = readout|model|cond) + every STRICT / lexicon
# disagreement + every free sample-0 row (damage) (D11; est. ~2,300 items x 2 judges ~ $0.55), then the report and the raw dump.
# Needs GPU_DONE_L3 for both models pulled to /workspace/runs_executor/sw039/p1/ (prep exits 2 on any missing key).
#   nohup bash ".../src/p1/jobs/box1_l5_judge_replies.sh" > /workspace/runs_executor/sw039/p1/l5_judge.log 2>&1 < /dev/null &
set -uo pipefail
S="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1"; R=/workspace/runs_executor/sw039/p1
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
rsync -a -e "ssh -p <port> -i /root/.ssh/id_ed25519 -o BatchMode=yes" root@<box-ip>:/root/runs/sw039/p1/ $R/
cd $R
/usr/bin/python3 -I "$S/analyze39p1.py" prep --run_dir $R || { echo "prep failed (incomplete?)"; exit 2; }
/usr/bin/python3 $LIB/judge_run.py --exp sw039 --rubric reply5 --in $R/judgein.jsonl --out $R/judged_replies.jsonl --part p1_L5 \
  --sample-frac 0.2 --strata-field cell --always-field always --seed 0 --also-touch /workspace/runs_executor/sw039/JUDGED_p1_replies; rc=$?
[ $rc -eq 0 ] || { echo "judge_run rc $rc (rerun to resume; analysis below uses STRICT where unjudged)"; }
/usr/bin/python3 -I "$S/analyze39p1.py" report --run_dir $R --out $R/analysis
/usr/bin/python3 -I "$S/analyze39p1.py" dump --run_dir $R --out $R/analysis
exit $rc
