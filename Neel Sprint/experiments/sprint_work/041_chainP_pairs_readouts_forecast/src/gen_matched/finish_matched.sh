#!/bin/bash
# matched-main: after the candidates phase (SELECTION_RULES.txt sections 4-6). Run on the node:
#   setsid -f nohup bash finish_matched.sh > <log> 2>&1 < /dev/null
# 1. waits until all candidate shards of A and B have their DONE marker (NSHARD per assignment, default 4);
# 2. runs the frozen 'select' for A and B on CPU;
# 3. if both are feasible in every cell, starts one stage-2 worker per GPU (queue_matched.sh stage2, the same 8-shard job list,
#    shards claimed by mkdir) pinned to the CPU blocks E3 gave on 31 Oct; else writes <tag dir>/NEEDS_EXTENSION and stops
#    (the extension for the saturated specs is then launched by hand, SELECTION_RULES 5).
HERE=$(cd "$(dirname "$0")" && pwd)
R=/root/runs/sw041/full/gen; I=/root/runs/sw041/gen/matched; L=/root/runs/sw041/gen/logs; PY=/root/venvs/vlfix/bin/python
NSHARD=${NSHARD:-4}; SEL_CPUS=${SEL_CPUS:-48-71}
declare -A CPU=([0]="0-23,96-119" [1]="24-47,120-143" [2]="48-71,144-167" [3]="72-95,168-191")
JOBS=""; for i in $(seq 0 $((NSHARD - 1))); do JOBS="$JOBS A:$i/$NSHARD B:$i/$NSHARD"; done
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "[$(ts)] finish driver $(sha256sum "$0" | cut -c1-16) start; waiting for $((2 * NSHARD)) candidate DONE markers"
alldone() { for X in A B; do for i in $(seq 0 $((NSHARD - 1))); do [ -e "$R/full_v5_matched$X/candidates/DONE_cand_shard${i}of$NSHARD" ] || return 1; done; done; }
until alldone; do sleep 30; done
echo "[$(ts)] all candidate shards done"
bad=0
for X in A B; do
  taskset -c "$SEL_CPUS" "$PY" -I "$HERE/select_matched.py" select --tag "full_v5_matched$X" --assign "$X" --root "$R" \
      --targets "$I/targets.json" --specs "$I/specs_matched${X}_pf_full_v5.jsonl" > "$L/select_matched$X.log" 2>&1
  rc=$?
  tail -2 "$L/select_matched$X.log"
  if [ $rc -ne 0 ] || ! grep -q "^ALL_FEASIBLE" "$L/select_matched$X.log"; then
    echo "[$(ts)] select $X: rc $rc, not all feasible"; echo "$(ts)" > "$R/full_v5_matched$X/NEEDS_EXTENSION"; bad=1
  fi
done
[ $bad -eq 0 ] || { echo "[$(ts)] STOP: extension needed (or select failed); no stage 2 started"; exit 1; }
for g in 0 1 2 3; do
  GPU=$g CPUS=${CPU[$g]} WAIT_FILE= setsid -f nohup bash "$HERE/queue_matched.sh" stage2 $JOBS > "$L/matched_s2_worker_gpu$g.log" 2>&1 < /dev/null
  echo "[$(ts)] stage-2 worker started on GPU $g (CPUs ${CPU[$g]})"
done
echo "[$(ts)] finish driver done"
