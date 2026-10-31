#!/bin/bash
# sw039 Part 1 stages L3 (turn-3 replies) + L4 (captures), GPU, node; HF + unmerged PEFT, one organism per process and GPU (D7).
# Needs /root/runs/sw039/p1/GPU_DONE_L1. Order inside the job: G1 adapter-active gate -> memory probe at the full batch on the
# longest contexts (every row forced to the cap; halves on OOM) -> 6-row smoke -> free (2 samples, <= 2,048) -> fbtw (2 samples, 48)
# -> GPU_DONE_L3_<m>[shard tag] -> captures of the 704 ladder contexts + sw021's 122 G3 anchors -> GPU_DONE_L4_<m>.
# Measured basis (sw029, same node / engine): free 38-42 rows/min at 46-row batches with hooks, 57-79 rows/min at 64-row batches
# without; forced 380-394 rows/min; worst-case probe 46 rows x 2,048 = 341 s, 71.9 GiB; 69 rows = 78.1 GiB. Estimate per model, one
# GPU: load 3 + G1 0.5 + probe 7 + smoke 2 + free 1,408 rows ~ 25-35 + fbtw 1,408 ~ 4 + captures 826 x batch 1 ~ 4 = 45-55 min.
# Launch ON THE NODE, one line per organism (each on its own free GPU), recording the PIDs:
#   nohup bash ".../src/p1/jobs/l3l4_gen.sh" hdA0 <gA> > /root/runs/sw039/p1/logs/l3l4_hdA0.wrap 2>&1 < /dev/null & echo $!
#   nohup bash ".../src/p1/jobs/l3l4_gen.sh" hdB0 <gB> > /root/runs/sw039/p1/logs/l3l4_hdB0.wrap 2>&1 < /dev/null & echo $!
# Optional 4-GPU split (halves the free stage): shard 0 keeps the captures, shard 1 skips them:
#   ... l3l4_gen.sh hdA0 <g0> 0/2 g1,probe,smoke,free,fbtw,cap     ... l3l4_gen.sh hdA0 <g1> 1/2 g1,probe,free,fbtw
# (then GPU_DONE_L3_hdA0.shard0of2 + .shard1of2 together = L3 done for hdA0). Resumable: rerun the same line (resume by key).
set -uo pipefail
M=${1:?model}; GPU=${2:?gpu}; SHARD=${3:-0/1}; STAGES=${4:-g1,probe,smoke,free,fbtw,cap}; FB=${FREE_BATCH:-48}; XB=${FORCED_BATCH:-64}
J="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1/jobs"
[ -e /root/runs/sw039/p1/GPU_DONE_L1 ] || { echo "no GPU_DONE_L1"; exit 2; }
TAG=$(echo $SHARD | tr '/' 'o')
bash "$J/run39p1.sh" L3L4_${M}_${TAG} $GPU si gen39p1.py --model $M --shard $SHARD --stages $STAGES --free_batch $FB --forced_batch $XB
