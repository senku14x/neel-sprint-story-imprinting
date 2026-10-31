#!/bin/bash
# sw071 histories on GPU 0 (prep-71): smoke on 2 scripts, then (only if the smoke passes its screen gate) the full 64 scripts.
#   setsid nohup bash hist71.sh > /root/runs/sw071/hist71.wrap 2>&1 < /dev/null &
set -uo pipefail
SRC="/workspace/Neel Sprint/experiments/sprint_work/071_polish_mechanism_v2/src"; RUN=/root/runs/sw071
bash "$SRC/jobs/run_node71.sh" hist_smoke 0 vlfix hist71.py --out $RUN/hist --smoke 2 || { echo "HIST_SMOKE_FAILED"; touch $RUN/hist/FAILED_hist; exit 4; }
echo "smoke ok $(date -u +%T)"
bash "$SRC/jobs/run_node71.sh" hist_full 0 vlfix hist71.py --out $RUN/hist || { echo "HIST_FULL_FAILED"; touch $RUN/hist/FAILED_hist; exit 5; }
echo "HIST71_ALL_DONE $(date -u +%T)"
