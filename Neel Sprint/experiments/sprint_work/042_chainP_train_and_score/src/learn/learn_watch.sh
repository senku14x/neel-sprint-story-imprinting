#!/bin/bash
# sw042 learning-check watcher on one GPU of the node (written 2026-10-31 by a subagent of E3 / executor-12).
# Usage (node): bash learn_watch.sh <gpu>      (gpu_queue.sh calls it on GPU 3 after mirrorB; it can also be started alone)
# Every 60 s: pending.py lists the step-125 / final snapshots that are complete and not yet checked; learn_check.py runs them
# in one vLLM engine (the parent reference rides along on the first batch). Ends when all 14 checks are done or on
# /root/runs/sw042/learn/STOP. A crashed batch is retried once (ATTEMPTS counter per check), then left for E3.
# Every step-125 ONSET_WITHOUT_BINDING marker is echoed to logs/ALERTS (the addendum's rule: E3 tells the user before the run
# continues; the run itself is NOT stopped by this script).
set -u
GPU=$1; R=${SW042_ROOT:-/root/runs/sw042}; CODE=$R/code
case $GPU in 0|1) CPUS=0-47,96-143;; 2|3) CPUS=48-95,144-191;; *) echo "bad gpu $GPU"; exit 2;; esac
export PATH=/root/venvs/vlfix/bin:$PATH CUDA_VISIBLE_DEVICES=$GPU VLLM_USE_FLASHINFER_SAMPLER=0 VLLM_LENS_DISABLE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True HF_HUB_OFFLINE=1 SI_MODEL_DIR=/dev/shm/qwen36_27b
export TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
unset PYTHONPATH
mkdir -p $R/learn $R/logs
echo "learn watcher gpu$GPU start $(date -u +%FT%TZ)"
while true; do
  [ -e $R/learn/STOP ] && { echo "STOP file $(date -u +%FT%TZ)"; break; }
  P=$(python -I $CODE/learn/pending.py --root $R)
  [ "$P" = ALLDONE ] && { echo "all checks done $(date -u +%FT%TZ)"; break; }
  if [ -n "$P" ]; then
    for x in ${P//,/ }; do nm=${x/:/_}; mkdir -p $R/learn/$nm; n=$(cat $R/learn/$nm/ATTEMPTS 2>/dev/null || echo 0); echo $((n+1)) > $R/learn/$nm/ATTEMPTS; done
    PAR=""; [ -e $R/learn/parent/DONE ] || PAR="--with-parent"
    echo "--- learn_check $P $PAR $(date -u +%FT%TZ)"
    taskset -c $CPUS python -I $CODE/learn/learn_check.py --ckpts $P $PAR --root $R >> $R/logs/learn_gpu$GPU.log 2>&1
    echo "--- learn_check rc=$? $(date -u +%FT%TZ)"
    for f in $R/learn/*_step125/ONSET_WITHOUT_BINDING; do
      [ -e "$f" ] && ! grep -qF "$f" $R/logs/ALERTS 2>/dev/null && echo "$(date -u +%FT%TZ) $f" >> $R/logs/ALERTS
    done
  fi
  sleep 60
done
echo "learn watcher gpu$GPU end $(date -u +%FT%TZ)"
