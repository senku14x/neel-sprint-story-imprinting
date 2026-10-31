#!/bin/bash
# sw039 Part 1 stage L1 (GPU, node): the parent writes the 11 x 64 ladder histories on vLLM (hist39p1.py --mode smoke_full:
# 2-script smoke with inline gates, then the full run in the same engine). Measured basis: sw019 hist (H200, 384 seqs) wrote
# 3,072 x 3 + 3,057 x 3 candidates in 266 + 331 s after a 101 s load; L1 is 576 x 3 + 704 x 3 candidates of <= 400 tokens on an
# H100 at 128 seqs -> est. 10-15 min including the load.
# Launch ON THE NODE (GPU <g> must be free; the orchestrator assigns it), recording the PID:
#   nohup bash "/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1/jobs/l1_hist.sh" <g> \
#     > /root/runs/sw039/p1/logs/l1_hist.wrap 2>&1 < /dev/null & echo $!
# Done = /root/runs/sw039/p1/GPU_DONE_L1 (written only when every expected key has a row). Failure = manifests/L1_hist.exit rc != 0.
set -uo pipefail
GPU=${1:?gpu}
J="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1/jobs"
mkdir -p /root/runs/sw039/p1/logs
bash "$J/run39p1.sh" L1_hist $GPU vlfix hist39p1.py --mode smoke_full
