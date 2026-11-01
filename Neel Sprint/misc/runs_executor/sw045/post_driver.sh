#!/bin/bash
# E3 (31 Oct 16:15 UTC, before the account switch): detached box-1 driver for sw045's post-processing (045 DECISIONS D11 step 2).
# Polls the node every 2 min (bounded 10 h). When eval/g2_X/DONE exists (and no GATE_FAIL/FAILED) it runs post45.sh g2_X once.
# GATE_FAIL/FAILED -> writes /workspace/runs_executor/sw045/STOP_<X> and does not post (ask the user). Exits when both are handled.
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=20 root@<box-ip>"
POST="/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/run/post45.sh"
D=/workspace/runs_executor/sw045
for i in $(seq 1 300); do
  left=0
  for X in g2_A g2_B; do
    [ -e $D/POST_STARTED_$X ] || [ -e $D/STOP_$X ] && continue
    left=1
    st=$($SSH "d=/root/runs/sw045/eval/$X; if [ -e \$d/GATE_FAIL ] || [ -e \$d/FAILED ]; then echo FAIL; elif [ -e \$d/DONE ]; then echo DONE; else echo WAIT; fi" 2>/dev/null)
    echo "$(date -u +%T) $X $st"
    if [ "$st" = FAIL ]; then echo "$(date -u +%FT%TZ) gate/failed marker on node for $X: ask the user" > $D/STOP_$X
    elif [ "$st" = DONE ]; then date -u +%FT%TZ > $D/POST_STARTED_$X; bash "$POST" $X > $D/post_$X.log 2>&1; echo "$(date -u +%T) post $X rc=$?"; fi
  done
  [ $left = 0 ] && { echo "$(date -u +%T) ALL_POSTS_HANDLED"; exit 0; }
  sleep 120
done
echo TIMEOUT
