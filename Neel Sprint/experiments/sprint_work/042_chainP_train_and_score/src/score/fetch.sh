#!/bin/bash
# sw042 scoring: copy one organism's node outputs back to box 1 (repeatable; never deletes on either side).
#   fetch.sh ORG [RUN]      node /root/runs/sw042/score/[RUN/]ORG/ -> /workspace/runs_executor/sw042/score/[RUN/]ORG/
set -eu
ORG=$1; RUN=${2:-}
KEY=/root/.ssh/id_ed25519; PORT=17106; HOST=root@<node-ip>
SUB=${RUN:+$RUN/}
mkdir -p "/workspace/runs_executor/sw042/score/$SUB$ORG"
rsync -az -e "ssh -i $KEY -p $PORT" "$HOST:/root/runs/sw042/score/$SUB$ORG/" "/workspace/runs_executor/sw042/score/$SUB$ORG/"
ls -la "/workspace/runs_executor/sw042/score/$SUB$ORG/"
