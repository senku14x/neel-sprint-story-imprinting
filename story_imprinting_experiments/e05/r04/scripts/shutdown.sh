#!/bin/bash
# Last step: push a STATUS line naming the command, then remove the pod; if refused, push that, then stop the pod.
LOG=/workspace/e05/r04/logs/shutdown.log
cd /workspace/e05/r04
python3 -I scripts/status_add.py "**Shutdown:** $(date -u +%H:%M) UTC, about to run \`runpodctl remove pod \$RUNPOD_POD_ID\` (if refused: \`runpodctl stop pod \$RUNPOD_POD_ID\`)."
./scripts/push.sh "shutdown: about to remove pod" >> $LOG 2>&1
echo "$(date -u +%FT%TZ) runpodctl remove pod" >> $LOG
out=$(runpodctl remove pod "$RUNPOD_POD_ID" 2>&1); rc=$?
echo "$out" >> $LOG; echo "rc=$rc" >> $LOG
if [ $rc -eq 0 ] && echo "$out" | grep -qi "removed"; then exit 0; fi
python3 -I scripts/status_add.py "**Shutdown:** \`runpodctl remove pod\` was refused (rc $rc); running \`runpodctl stop pod \$RUNPOD_POD_ID\` instead."
./scripts/push.sh "shutdown: remove refused, stopping pod" >> $LOG 2>&1
echo "$(date -u +%FT%TZ) runpodctl stop pod" >> $LOG
for i in 1 2 3 4 5; do runpodctl stop pod "$RUNPOD_POD_ID" >> $LOG 2>&1 && break; sleep 30; done
