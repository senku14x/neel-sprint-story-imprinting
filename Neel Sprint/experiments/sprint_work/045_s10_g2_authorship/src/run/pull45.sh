#!/bin/bash
# sw045: pull one node job dir to box 1 (/workspace/runs_executor/sw045/<rel>), then verify45.py on it. E3 agent, 31 Oct 2026.
#   bash pull45.sh <rel dir under /root/runs/sw045> [verify]
set -u
REL=$1; V=${2:-}
SSH="ssh -i /root/.ssh/id_ed25519 -p <port>"; N=root@<box-ip>
mkdir -p /workspace/runs_executor/sw045/$REL
rsync -a --partial -e "$SSH" $N:/root/runs/sw045/$REL/ /workspace/runs_executor/sw045/$REL/; rc=$?
echo "pull $REL rc=$rc $(date -u +%FT%TZ)"
[ "$V" = verify ] && python3 -I "/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/run/verify45.py" /workspace/runs_executor/sw045/$REL
exit $rc
