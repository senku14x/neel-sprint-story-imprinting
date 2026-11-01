#!/bin/bash
# E5 per-GPU job queue on the 4xH200 node (executor-15, 31 Oct 2026). Written on /workspace, rsynced to the node; never edited there.
# Start (node):  setsid -f nohup bash /root/runs_E5/lib/node_queue.sh <gpu> > /root/runs_E5/queue/runner_gpu<gpu>.log 2>&1 < /dev/null
# Jobs: /root/runs_E5/queue/gpu<gpu>/<PP>_<sw07N>_<part>.job  (bash scripts; lowest PP first; '# DEPS: /abs/file ...' lines gate readiness)
# State: <job>.running -> <job>.done | <job>.failed (exit code in <job>.exit). A failed job does NOT stop the queue (other experiments
# keep running); the orchestrator's watcher on box 1 sees the .failed marker on the next pull.
# Env given to each job: GPU, CUDA_VISIBLE_DEVICES, CPUS (taskset list for the GPU's socket), JOB, E5=/root/runs_E5.
# Stop: touch /root/runs_E5/queue/STOP_gpu<gpu> (checked between jobs). Kill a running job by the PID in <job>.pid.
set -u
GPU=$1
E5=/root/runs_E5
Q=$E5/queue/gpu$GPU
mkdir -p $Q
if [ "$GPU" -le 1 ]; then CPUS="0-47,96-143"; else CPUS="48-95,144-191"; fi
ev() { echo "{\"t\":\"$(date -u +%FT%TZ)\",\"gpu\":$GPU,\"job\":\"$1\",\"status\":\"$2\"}" >> $E5/queue/events.jsonl; }
echo "runner gpu$GPU start $(date -u +%FT%TZ) pid $$ cpus $CPUS"
ev runner start
while true; do
  [ -e $E5/queue/STOP_gpu$GPU ] && { echo "STOP gpu$GPU $(date -u +%FT%TZ)"; ev runner stop; exit 0; }
  pick=""
  for j in $(ls $Q/*.job 2>/dev/null | sort); do
    b=${j%.job}
    [ -e $b.running ] || [ -e $b.done ] || [ -e $b.failed ] && continue
    ok=1
    while read -r dep; do [ -n "$dep" ] && [ ! -e "$dep" ] && ok=0; done < <(grep '^# DEPS:' "$j" | sed 's/^# DEPS://' | tr ' ' '\n')
    [ $ok = 1 ] && { pick=$j; break; }
  done
  if [ -z "$pick" ]; then sleep 20; continue; fi
  b=${pick%.job}; name=$(basename $b)
  date -u +%FT%TZ > $b.running
  echo "start $name $(date -u +%FT%TZ)"; ev $name running
  ( export GPU=$GPU CUDA_VISIBLE_DEVICES=$GPU CPUS=$CPUS JOB=$name E5=$E5; exec 9>&-; bash $pick ) > $b.log 2>&1 < /dev/null &
  jp=$!; echo $jp > $b.pid
  wait $jp; rc=$?
  echo $rc > $b.exit
  if [ $rc = 0 ]; then mv $b.running $b.done; ev $name done; else mv $b.running $b.failed; ev $name failed; fi
  echo "end $name rc=$rc $(date -u +%FT%TZ)"
done
