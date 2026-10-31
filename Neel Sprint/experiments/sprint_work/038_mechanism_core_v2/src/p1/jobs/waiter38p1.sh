#!/bin/bash
# sw038 Part 1 remove-shard waiter (prep-P1 agent, E2, 31 Oct 2026). Run ON THE NODE, detached:
#   setsid nohup bash waiter38p1.sh <model> <primary_gpu> <fallback_gpu> <batch_units> <forced_batch_units> > <log> 2>&1 < /dev/null &
# Every 60 s: (1) if Part 0's marker /root/runs/sw038/p0/GPU_DONE_p0_<model> exists AND nvidia-smi shows < 1,000 MiB used on the
# primary GPU, launch the remove shard there; (2) else, once 2 h have passed since the waiter started, if this model's induce shard
# wrote GPU_DONE_p1_<model>_induce AND the fallback GPU shows < 1,000 MiB, launch the remove shard on the fallback GPU.
# Never uses pgrep / pkill; its own PID is in PID_waiter_<model>; the shard's PID in PID_shard_p1_<model>_remove.
set -uo pipefail
M=$1; PRI=$2; FB=$3; BU=$4; FBU=$5
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p1"
OUT=/root/runs/sw038/p1/full; mkdir -p $OUT
P0=/root/runs/sw038/p0/GPU_DONE_p0_$M; IND=$OUT/GPU_DONE_p1_${M}_induce
echo "$$ $(date -u +%FT%TZ) primary=$PRI fallback=$FB" > $OUT/PID_waiter_$M
START=$(date +%s); GPU=""
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' ' || echo 99999; }
while [ -z "$GPU" ]; do
  if [ -e $P0 ] && [ "$(used $PRI)" -lt 1000 ]; then GPU=$PRI; WHY="Part 0 marker $P0 present and GPU $PRI free"; break; fi
  if [ $(( $(date +%s) - START )) -ge 7200 ] && [ -e $IND ] && [ "$(used $FB)" -lt 1000 ]; then GPU=$FB; WHY="2 h passed without $P0; induce shard done; GPU $FB free"; break; fi
  sleep 60
done
echo "$(date -u +%FT%TZ) launching remove shard for $M on GPU $GPU: $WHY" | tee $OUT/WAITER_LAUNCH_$M
exec bash "$SRC/jobs/shard38p1.sh" $M remove $GPU $BU $FBU
