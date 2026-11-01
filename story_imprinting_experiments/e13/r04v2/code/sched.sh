#!/usr/bin/env bash
# One B200: run elite A, then SFL A (the researcher: instances 3 and 4 skipped). A failed or killed instance does not stop the next.
L=/workspace/e13/r04v2/logs/instances.log
for inst in eliteA sflA; do
  echo "INSTANCE_START $inst gpu0 $(date -u +%FT%TZ)" >> $L
  tmux new -d -s "$inst" "bash /workspace/e13/r04v2/code/inst_$inst.sh"
  sleep 5
  while tmux has-session -t "=$inst" 2>/dev/null; do sleep 30; done
  echo "INSTANCE_ENDED $inst $(date -u +%FT%TZ)" >> $L
done
echo "SCHED_DONE $(date -u +%FT%TZ)" >> $L
