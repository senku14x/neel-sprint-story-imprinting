#!/bin/bash
# matched-main feasibility pilot driver (SELECTION_RULES.txt section 8), run on the node in the background:
#   nohup bash <code root>/gen_matched/pilot_matched.sh > <log> 2>&1 &
# 1. waits until $WAIT_FILE exists AND GPU $GPU uses < 2,048 MiB (E3, 31 Oct: mirrorB's training finished; never touches queues);
# 2. candidates (k = 20..25) for the 100 pilot specs of A, then of B; 3. the 'pilot' selection report for A and B (CPU);
# 4. stage 2 on the chosen candidates for A, then B; 5. writes $P/PILOT_DONE (or $P/PILOT_FAILED and stops at the first error).
# DRY=1 prints the commands instead of running them.
GPU=${GPU:-3}; CPUS=${CPUS:-48-95,144-191}
WAIT_FILE=${WAIT_FILE:-/root/runs/sw042/train/mirrorB/DONE}
HERE=$(cd "$(dirname "$0")" && pwd)
I=/root/runs/sw041/gen/matched; P=/root/runs/sw041/gen/matched_pilot; L=/root/runs/sw041/gen/logs; PY=/root/venvs/vlfix/bin/python
[ -n "$DRY" ] && { P=$(mktemp -d); L=$P; echo "DRY: writes go to $P"; }
mkdir -p "$P" "$L"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
run() { echo "[$(ts)] RUN $*"; [ -n "$DRY" ] && return 0; "$@"; }
gpu_mem() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' '; }
fail() { echo "[$(ts)] FAILED: $*"; echo "$(ts) $*" > "$P/PILOT_FAILED"; exit 1; }
wait_pid() { while kill -0 "$1" 2>/dev/null; do sleep 15; done; }

echo "[$(ts)] pilot driver start; waiting for $WAIT_FILE and GPU $GPU < 2048 MiB"
echo "[$(ts)] driver $(sha256sum "$0"); launcher $(sha256sum "$HERE/launch_matched.sh" | cut -c1-16); host $(hostname)"
if [ -z "$DRY" ]; then
  until [ -e "$WAIT_FILE" ] && [ "$(gpu_mem)" -lt 2048 ]; do sleep 30; done
fi
echo "[$(ts)] condition met (GPU $GPU memory $(gpu_mem) MiB)"
for X in A B; do
  echo "[$(ts)] candidates $X"
  if [ -z "$DRY" ]; then
    PID=$(bash "$HERE/launch_matched.sh" "$GPU" "$CPUS" "$L/pilot_cand_$X.log" candidates --tag "pilot_matched$X" \
          --specs "$I/specs_matched${X}_pf_full_v5.jsonl" --only-keys "$I/pilot_keys_matched$X.json" --ks 20-25 --root "$P")
    wait_pid "$PID"
    [ -e "$P/pilot_matched$X/candidates/DONE_cand_shard0of1" ] || fail "candidates $X did not finish (see $L/pilot_cand_$X.log)"
  else
    echo "launch_matched.sh $GPU $CPUS candidates pilot_matched$X"
  fi
done
for X in A B; do
  run taskset -c "$CPUS" "$PY" -I "$HERE/select_matched.py" pilot --tag "pilot_matched$X" --assign "$X" --root "$P" \
      --targets "$I/targets.json" --specs "$I/specs_matched${X}_pf_full_v5.jsonl" > "$L/pilot_select_$X.log" 2>&1 \
      || fail "pilot selection $X (see $L/pilot_select_$X.log)"
done
for X in A B; do
  echo "[$(ts)] stage 2 $X"
  if [ -z "$DRY" ]; then
    PID=$(bash "$HERE/launch_matched.sh" "$GPU" "$CPUS" "$L/pilot_s2_$X.log" stage2 --tag "pilot_matched$X" \
          --specs "$I/specs_matched${X}_pf_full_v5.jsonl" --only-keys "$I/pilot_keys_matched$X.json" \
          --selection "$P/pilot_matched$X/selection/pilot_pilot_matched$X.json" --root "$P")
    wait_pid "$PID"
    [ -e "$P/pilot_matched$X/DONE_shard0of1" ] || fail "stage 2 $X did not finish (see $L/pilot_s2_$X.log)"
  else
    echo "launch_matched.sh $GPU $CPUS stage2 pilot_matched$X"
  fi
done
echo "$(ts)" > "$P/PILOT_DONE"
echo "[$(ts)] PILOT_DONE"
