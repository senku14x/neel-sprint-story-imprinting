#!/bin/bash
# sw042: one round's learning checks on one GPU of the node, after the fact (sw042 D10: checks are not live).
# Written 2026-10-31 by a subagent of E3 / executor-12.
# Usage (node): setsid nohup bash round_learn.sh <gpu> <run,run,...> <done marker> [<busy pattern>] > LOG 2>&1 &
#   waits until no process matches <busy pattern> (default /root/runs/sw041/matched_code/) AND the GPU shows < 2 GB used;
#   then learn_check.py on every run's step125 snapshot (one engine; the parent reference rides along if not done yet),
#   then on every run's final adapter (one engine); gates G1 / G2 / G4 and the D9 policy (data/learn/swap_read_result.json)
#   inside learn_check.py. Finally writes <done marker> = "<status> <date -u>" (status ok, or the failed stages) whether or
#   not a stage failed, so a waiting job is never blocked; this script never touches the GPU after that.
set -u
GPU=$1; RUNS=$2; MARK=$3; BUSY=${4:-/root/runs/sw041/matched_code/}
R=${SW042_ROOT:-/root/runs/sw042}; CODE=$R/code
case $GPU in 0|1) CPUS=0-47,96-143;; 2|3) CPUS=48-95,144-191;; *) echo "bad gpu $GPU"; exit 2;; esac
export PATH=/root/venvs/vlfix/bin:$PATH CUDA_VISIBLE_DEVICES=$GPU VLLM_USE_FLASHINFER_SAMPLER=0 VLLM_LENS_DISABLE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True HF_HUB_OFFLINE=1 SI_MODEL_DIR=/dev/shm/qwen36_27b
export TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
unset PYTHONPATH
mkdir -p $R/learn $R/logs
echo "round_learn gpu$GPU runs $RUNS: waiting $(date -u +%FT%TZ)"
while pgrep -f "$BUSY" > /dev/null || [ "$(nvidia-smi -i $GPU --query-gpu=memory.used --format=csv,noheader,nounits)" -ge 2048 ]; do sleep 30; done
echo "gpu$GPU free (no '$BUSY' process, < 2 GB): start $(date -u +%FT%TZ)"
STATUS=ok
for stage in step125 final; do
  CK=""; for r in ${RUNS//,/ }; do CK="$CK$r:$stage,"; done; CK=${CK%,}
  PAR=""; [ -e $R/learn/parent/DONE ] || PAR="--with-parent"
  echo "--- $stage: learn_check $CK $PAR $(date -u +%FT%TZ)"
  taskset -c $CPUS python -I $CODE/learn/learn_check.py --ckpts $CK $PAR --root $R
  rc=$?; echo "--- $stage rc=$rc $(date -u +%FT%TZ)"
  [ $rc -eq 0 ] || STATUS="${STATUS/ok/}fail_$stage "
  for f in $R/learn/*_step125/ONSET_WITHOUT_BINDING; do
    [ -e "$f" ] && ! grep -qF "$f" $R/logs/ALERTS 2>/dev/null && echo "$(date -u +%FT%TZ) $f" >> $R/logs/ALERTS
  done
done
echo "$STATUS $(date -u +%FT%TZ)" > $MARK
echo "round_learn done: $STATUS -> $MARK $(date -u +%FT%TZ)"
