#!/bin/bash
# executor-14: when sw039 L1 is done on the node, run the L2 manipulation-check judging on box 1 (the script pulls first).
SSH="ssh -o BatchMode=yes -o ConnectTimeout=20 -p <port> -i /root/.ssh/id_ed25519 root@<box-ip>"
L=/workspace/runs_executor/sw038/watch/watch_s39_L2.log; log(){ echo "$(date -u +%H:%M:%S) $*" >> $L; }
log "start pid $$"
until $SSH '[ -e /root/runs/sw039/p1/GPU_DONE_L1 ]' 2>/dev/null; do sleep 60; done
log "GPU_DONE_L1 seen"; mkdir -p /workspace/runs_executor/sw039/p1
bash "/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1/jobs/box1_l2_judge_hist.sh" > /workspace/runs_executor/sw039/p1/l2_judge_hist.log 2>&1; log "L2 rc=$?"
