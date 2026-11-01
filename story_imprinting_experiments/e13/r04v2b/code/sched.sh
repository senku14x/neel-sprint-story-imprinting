#!/usr/bin/env bash
# One B200, GPU 0: elite B, then SFL B (the researcher: both required, neither skipped for time). A failed instance doesn't stop the next.
# If elite B exits non-zero, wait up to 15 min for the agent to create $R/hold (crash recovery first, to keep the brief's order);
# while hold exists, wait. Then start SFL B.
R=/workspace/e13/r04v2b; L=$R/logs/instances.log
for inst in eliteB sflB; do
  if [ "$inst" = sflB ] && ! grep -q "INSTANCE_EXIT eliteB 0 " $L; then
    echo "SCHED_GATE sflB waiting for hold decision $(date -u +%FT%TZ)" >> $L
    for i in $(seq 90); do [ -e $R/hold ] && break; sleep 10; done
    while [ -e $R/hold ]; do sleep 30; done
  fi
  echo "INSTANCE_START $inst gpu0 $(date -u +%FT%TZ)" >> $L
  tmux new -d -s "$inst" "bash $R/code/inst_$inst.sh"
  sleep 5
  while tmux has-session -t "=$inst" 2>/dev/null; do sleep 30; done
  echo "INSTANCE_ENDED $inst $(date -u +%FT%TZ)" >> $L
done
echo "SCHED_DONE $(date -u +%FT%TZ)" >> $L
