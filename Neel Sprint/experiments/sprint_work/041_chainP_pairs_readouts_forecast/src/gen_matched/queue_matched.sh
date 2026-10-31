#!/bin/bash
# matched-main full-run worker for one GPU (SELECTION_RULES.txt sections 5-6). Runs on the node in the background:
#   GPU=3 CPUS=48-95,144-191 WAIT_FILE=/root/runs/sw042/learn/ROUND1_DONE nohup bash queue_matched.sh <phase> <job>... > <log> 2>&1 &
# phase: candidates | stage2.  job: <X>:<i>/<n>, e.g. A:0/4 (assignment X, shard i of n).
# Waits until $WAIT_FILE exists (if set) AND GPU $GPU uses < 2,048 MiB, then runs the jobs in order. Before a job it claims it with
# mkdir <tag dir>/CLAIM_<phase>_shard<i>of<n> (atomic), so workers on other GPUs started later with the same job list skip claimed
# shards and take the rest. Stops at the first job that does not leave its DONE marker. KS (default 20-25) sets the candidates' k.
# DRY=1 prints instead of running.
PHASE=$1; shift
GPU=${GPU:-3}; CPUS=${CPUS:-48-95,144-191}; KS=${KS:-20-25}
HERE=$(cd "$(dirname "$0")" && pwd)
I=/root/runs/sw041/gen/matched; R=/root/runs/sw041/full/gen; L=/root/runs/sw041/gen/logs
[ -n "$DRY" ] && { R=$(mktemp -d); L=$R/logs; echo "DRY: writes go to $R"; }
mkdir -p "$L"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
gpu_mem() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' '; }
case "$PHASE" in candidates|stage2) ;; *) echo "phase must be candidates or stage2"; exit 2;; esac
echo "[$(ts)] driver $(sha256sum "$0"); launcher $(sha256sum "$HERE/launch_matched.sh" | cut -c1-16); host $(hostname)"
echo "[$(ts)] worker GPU $GPU phase $PHASE jobs $*; waiting for ${WAIT_FILE:-<none>} and GPU $GPU < 2048 MiB"
if [ -z "$DRY" ]; then
  until { [ -z "$WAIT_FILE" ] || [ -e "$WAIT_FILE" ]; } && [ "$(gpu_mem)" -lt 2048 ]; do sleep 30; done
fi
for J in "$@"; do
  X=${J%%:*}; SH=${J#*:}; i=${SH%%/*}; n=${SH#*/}; TAG=full_v5_matched$X; D=$R/$TAG
  mkdir -p "$D"
  if ! mkdir "$D/CLAIM_${PHASE}_shard${i}of${n}" 2>/dev/null; then echo "[$(ts)] $J already claimed, skip"; continue; fi
  echo "gpu $GPU $(ts)" > "$D/CLAIM_${PHASE}_shard${i}of${n}/by"
  if [ "$PHASE" = candidates ]; then
    ARGS=(candidates --tag "$TAG" --specs "$I/specs_matched${X}_pf_full_v5.jsonl" --ks "$KS" --shard "$SH" --root "$R")
    DONE="$D/candidates/DONE_cand_shard${i}of${n}"
  else
    ARGS=(stage2 --tag "$TAG" --specs "$I/specs_matched${X}_pf_full_v5.jsonl" --selection "$D/selection/select_$TAG.json" --shard "$SH" --root "$R")
    DONE="$D/DONE_shard${i}of${n}"
  fi
  echo "[$(ts)] start $J: ${ARGS[*]}"
  if [ -n "$DRY" ]; then continue; fi
  PID=$(bash "$HERE/launch_matched.sh" "$GPU" "$CPUS" "$L/${TAG}_${PHASE}_shard${i}of${n}.log" "${ARGS[@]}")
  while kill -0 "$PID" 2>/dev/null; do sleep 20; done
  [ -e "$DONE" ] || { echo "[$(ts)] FAILED $J (no $DONE; see $L/${TAG}_${PHASE}_shard${i}of${n}.log)"; exit 1; }
  echo "[$(ts)] done $J"
done
echo "[$(ts)] worker finished"
