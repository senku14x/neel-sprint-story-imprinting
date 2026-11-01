#!/bin/bash
# E08 R10 vLLM worker for one GPU (R09's worker.sh; R10: script set per job, the cut checkpoint): takes the jobs in data/jobs.txt
# in order, claiming each with an atomic mkdir in logs/claims/, so two GPUs never run the same job. A failed job is retried once
# (gen_eval resumes by key). logs/skip_<job> skips a job (time cuts); logs/stop_worker_<gpu> stops this worker before its next
# job. After the cut checkpoint (5 h 15 min after the deadline was armed) no job outside the never-cut set (C1a C1b C2a C2b) starts.
# Usage: worker.sh <gpu>
set -u
GPU=$1; W=/workspace/e08/r10; L=$W/logs
CUT=$(( $(sed -n 2p $L/deadline_armed_at.txt) + 18900 ))
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R10: $*" >> $L/push.log 2>&1 & ); }
while read -r JOB KIND SSET; do
  [ -z "$JOB" ] && continue
  [ -f $L/stop_worker_$GPU ] && { st "GPU $GPU worker: stop flag, exiting before $JOB"; exit 0; }
  [ -f $L/skip_$JOB ] && continue
  [ -f $W/results/rollouts/$JOB.jsonl.done ] && continue
  case " C1a C1b C2a C2b " in *" $JOB "*) ;; *)
    if [ $(date +%s) -ge $CUT ]; then
      mkdir $L/claims/$JOB 2>/dev/null && st "GPU $GPU: job $JOB not started (cut checkpoint passed)"; continue
    fi ;;
  esac
  mkdir $L/claims/$JOB 2>/dev/null || continue
  echo "GPU $GPU $(date -u +%FT%TZ)" > $L/claims/$JOB/by
  st "GPU $GPU: job $JOB ($KIND, scripts $SSET) started"
  for try in 1 2; do
    bash $W/code/scripts/gen.sh ${JOB}_try$try $GPU $W/data/models/$JOB.json 0.7 E08R10 $W/results/rollouts/$JOB.jsonl $SSET
    rc=$?; [ $rc = 0 ] && break
  done
  st "GPU $GPU: job $JOB exit $rc ($(wc -l < $W/results/rollouts/$JOB.jsonl 2>/dev/null || echo 0) rows)"
done < $W/data/jobs.txt
st "GPU $GPU worker: no Part C jobs left"
