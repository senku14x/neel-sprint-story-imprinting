#!/bin/bash
# E08 R09 vLLM worker for one GPU: takes the jobs in data/jobs.txt in order (priority order), claiming each with an atomic
# mkdir in logs/claims/, so two GPUs never run the same job. conv jobs: gen.sh with data/models/<job>.json (T 0.7, tag E08R09)
# -> results/rollouts/<job>.jsonl; story jobs: story.sh. A failed job is retried once (gen_eval resumes by key).
# logs/skip_<job> skips a job (time cuts); logs/stop_worker_<gpu> stops this worker before its next job.
# Usage: worker.sh <gpu>
set -u
GPU=$1; W=/workspace/e08/r09; L=$W/logs
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/code/push.sh "E08 R09: $*" >> $L/push.log 2>&1 & ); }
while read -r JOB KIND; do
  [ -z "$JOB" ] && continue
  [ -f $L/stop_worker_$GPU ] && { st "GPU $GPU worker: stop flag, exiting before $JOB"; exit 0; }
  [ -f $L/skip_$JOB ] && continue
  mkdir $L/claims/$JOB 2>/dev/null || continue
  echo "GPU $GPU $(date -u +%FT%TZ)" > $L/claims/$JOB/by
  st "GPU $GPU: job $JOB ($KIND) started"
  for try in 1 2; do
    if [ "$KIND" = conv ]; then
      bash $W/code/scripts/gen.sh ${JOB}_try$try $GPU $W/data/models/$JOB.json 0.7 E08R09 $W/results/rollouts/$JOB.jsonl
    else
      bash $W/code/scripts/story.sh ${JOB} $GPU $try
    fi
    rc=$?; [ $rc = 0 ] && break
  done
  OUTF=$W/results/rollouts/$JOB.jsonl; [ "$KIND" = story ] && OUTF=$W/results/stories/$JOB.jsonl
  st "GPU $GPU: job $JOB exit $rc ($(wc -l < $OUTF 2>/dev/null || echo 0) rows)"
done < $W/data/jobs.txt
st "GPU $GPU worker: no jobs left"
