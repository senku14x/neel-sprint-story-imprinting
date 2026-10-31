#!/bin/bash
# E3 (31 Oct): full Chain P generation, one claim loop per GPU on the node. Each job = one corpus half-shard (specs[i::2]).
# A GPU starts only after /root/runs/sw041/full/ALLOW_gpu<GPU> exists; a shard is claimed with an atomic mkdir, so no shard runs twice.
# Usage (node): nohup bash run_queue.sh <gpu> <cpus> > /root/runs/sw041/full/logs/runner_gpu<gpu>.log 2>&1 &
GPU=$1; CPUS=$2; Q=/root/runs/sw041/full
mkdir -p $Q/locks $Q/logs $Q/gen
JOBS="mainA:0/2 mirrorA:0/2 mainB:0/2 mirrorB:0/2 mainA:1/2 mirrorA:1/2 mainB:1/2 mirrorB:1/2"
until [ -e $Q/ALLOW_gpu$GPU ]; do sleep 30; done
echo "gpu$GPU allowed $(date -u +%FT%TZ)"
for j in $JOBS; do
  name=${j%%:*}; shard=${j#*:}; sid=${shard/\//of}; lock=$Q/locks/${name}_$sid
  mkdir $lock 2>/dev/null || continue
  echo "gpu$GPU $(date -u +%FT%TZ)" > $lock/claimed
  pid=$(bash $Q/gen_code/launch.sh $GPU $CPUS $Q/logs/${name}_$sid.log --tag full_v5_$name --mode chainp \
        --specs /root/runs/sw041/gen/specs/specs_${name}_full_v5.jsonl --shard $shard --chunk 2048 --out-root $Q/gen)
  echo "$pid" > $lock/pid; echo "gpu$GPU started $name $shard pid $pid $(date -u +%FT%TZ)"
  while kill -0 $pid 2>/dev/null; do sleep 20; done
  if grep -q "ALL DONE" $Q/logs/${name}_$sid.log; then echo ok > $lock/done; else echo fail > $lock/done; fi
  echo "gpu$GPU finished $name $shard $(cat $lock/done) $(date -u +%FT%TZ)"
done
echo "gpu$GPU queue empty $(date -u +%FT%TZ)"
