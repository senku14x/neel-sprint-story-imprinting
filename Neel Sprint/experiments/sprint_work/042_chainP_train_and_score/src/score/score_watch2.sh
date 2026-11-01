#!/bin/bash
# sw042 box-1 watcher, parallel: as soon as an organism's node job has DONE_ALL, claim it (mkdir claims_box1/<org>) and process it in
# its own background job: fetch, post.py all (labels, judge inputs, judging with the ALT-key preflight, widen; judge_run resumes from
# records already written), analyze.py org. One line per event in /workspace/runs_executor/sw042/score/watch.log. A budget / key stop
# (limit_remaining < $40 or the spend cap) writes WATCH_STOP and no new organism is started.
#   setsid -f nohup bash score_watch2.sh > /workspace/runs_executor/sw042/score/watch2.nohup 2>&1 < /dev/null
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/score"
BOX1=/workspace/runs_executor/sw042/score; LOG=$BOX1/watch.log; CAP=${CAP:-25}; CLB=$BOX1/claims_box1
SSH=(ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=20 root@<node-ip>)
ORGS=${ORGS:-"parent mainA mainB mirrorA mirrorB honestA honestB Fonly"}
log() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
mkdir -p $CLB; echo $$ > $BOX1/watch2${WTAG:-}.pid; log "watch2 (parallel) start cap \$$CAP orgs $ORGS"
cd "$SRC"
process() {
  o=$1
  bash fetch.sh "$o" > /dev/null 2>&1
  drc=$(python3 -c "import json; print(json.load(open('$BOX1/$o/DONE_ALL'))['drive_rc'])" 2>/dev/null)
  if [ "$drc" != "0" ]; then
    log "$o NODE_FAIL drive_rc=$drc gate=$(python3 -c "import json; g=json.load(open('$BOX1/$o/gate.json')); print(g.get('pass'), (g.get('tf') or {}).get('pass'))" 2>/dev/null)"
    echo fail > $CLB/$o/result; return
  fi
  python3 post.py all "$o" --cap "$CAP" >> "$BOX1/$o/post.log" 2>&1; prc=$?
  if grep -q "STOP:" "$BOX1/$o/post.log"; then log "$o WATCH_STOP $(grep -h 'STOP:' $BOX1/$o/post.log | tail -1)"; echo stop > $CLB/$o/result; touch $BOX1/WATCH_STOP; return; fi
  if [ $prc -ne 0 ]; then
    log "$o post rc $prc: retrying judge + widen once"
    python3 post.py judge "$o" --cap "$CAP" >> "$BOX1/$o/post.log" 2>&1 && python3 post.py widen "$o" --cap "$CAP" >> "$BOX1/$o/post.log" 2>&1; prc=$?
    if grep -q "STOP:" "$BOX1/$o/post.log"; then log "$o WATCH_STOP $(grep -h 'STOP:' $BOX1/$o/post.log | tail -1)"; echo stop > $CLB/$o/result; touch $BOX1/WATCH_STOP; return; fi
    [ $prc -ne 0 ] && { log "$o POST_FAIL rc $prc"; echo fail > $CLB/$o/result; return; }
  fi
  if python3 analyze.py org "$o" > "$BOX1/$o/analyze.log" 2>&1; then
    log "$o PROCESSED $(python3 -c "
import json; r=json.load(open('$BOX1/$o/results.json')); g=r.get('gate') or {}; tf=g.get('tf') or {}
print('gate', g.get('pass'), 'tf', tf.get('pass'), ('gap x%.2f shift x%.1f' % (tf['ratio_gap'], tf['ratio_shift'])) if tf.get('ratio_gap') is not None else '', 'bridges', (g.get('bridge_decision') or {}).get('per_bridge'), 'gpu_min', r['gpu_time'].get('gpu_minutes_total'), 'api', round(r['api_cost_usd']['total'], 3))")"
    echo ok > $CLB/$o/result
  else
    log "$o ANALYZE_FAIL $(tail -2 $BOX1/$o/analyze.log | tr '\n' ' ' | cut -c1-300)"; echo fail > $CLB/$o/result
  fi
}
while true; do
  left=0
  for o in $ORGS; do
    [ -f $CLB/$o/result ] && continue
    left=1
    [ -d $CLB/$o ] && continue
    [ -f $BOX1/WATCH_STOP ] && continue
    "${SSH[@]}" "test -f /root/runs/sw042/score/$o/DONE_ALL" 2>/dev/null || continue
    mkdir $CLB/$o 2>/dev/null || continue
    log "$o claimed for box-1 processing"
    process "$o" &
  done
  [ $left -eq 0 ] && break
  if [ -f $BOX1/WATCH_STOP ] && [ -z "$(jobs -r)" ]; then log "WATCH_STOP: no further organisms started"; exit 3; fi
  sleep 60
done
wait
log "WATCH_ALL_PROCESSED ${WTAG:-}"
