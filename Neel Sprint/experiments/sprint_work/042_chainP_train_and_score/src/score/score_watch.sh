#!/bin/bash
# sw042 box-1 watcher: as soon as an organism's node job has DONE_ALL, fetch it, run post.py all (labels, judge inputs, judging with
# the ALT-key preflight, widen) and analyze.py org; one line per event in /workspace/runs_executor/sw042/score/watch.log.
# A budget / key stop (limit_remaining < $40 or the spend cap) ends the watcher with WATCH_STOP (no further judging).
#   setsid -f nohup bash score_watch.sh > /workspace/runs_executor/sw042/score/watch.nohup 2>&1 < /dev/null
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/score"
BOX1=/workspace/runs_executor/sw042/score; LOG=$BOX1/watch.log; CAP=${CAP:-25}
SSH=(ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=20 root@<box-ip>)
ORGS="parent mainA mainB mirrorA mirrorB honestA honestB Fonly"
log() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
echo $$ > $BOX1/watch.pid; log "watch start cap \$$CAP orgs $ORGS"
declare -A DONE
cd "$SRC"
while true; do
  left=0
  for o in $ORGS; do
    [ -n "${DONE[$o]:-}" ] && continue
    left=1
    "${SSH[@]}" "test -f /root/runs/sw042/score/$o/DONE_ALL" 2>/dev/null || continue
    bash fetch.sh "$o" > /dev/null 2>&1
    drc=$(python3 -c "import json; print(json.load(open('$BOX1/$o/DONE_ALL'))['drive_rc'])" 2>/dev/null)
    if [ "$drc" != "0" ]; then
      log "$o NODE_FAIL drive_rc=$drc gate=$(python3 -c "import json; g=json.load(open('$BOX1/$o/gate.json')); print(g.get('pass'), g.get('tf',{}).get('pass'))" 2>/dev/null)"
      DONE[$o]=fail; continue
    fi
    python3 post.py all "$o" --cap "$CAP" > "$BOX1/$o/post.log" 2>&1; prc=$?
    if grep -q "STOP:" "$BOX1/$o/post.log"; then log "$o WATCH_STOP $(grep -h 'STOP:' $BOX1/$o/post.log | tail -1)"; exit 3; fi
    if [ $prc -ne 0 ]; then
      log "$o post rc $prc: retrying judge + widen once"
      python3 post.py judge "$o" --cap "$CAP" >> "$BOX1/$o/post.log" 2>&1 && python3 post.py widen "$o" --cap "$CAP" >> "$BOX1/$o/post.log" 2>&1; prc=$?
      if grep -q "STOP:" "$BOX1/$o/post.log"; then log "$o WATCH_STOP $(grep -h 'STOP:' $BOX1/$o/post.log | tail -1)"; exit 3; fi
      [ $prc -ne 0 ] && { log "$o POST_FAIL rc $prc"; DONE[$o]=fail; continue; }
    fi
    if python3 analyze.py org "$o" > "$BOX1/$o/analyze.log" 2>&1; then
      log "$o PROCESSED $(python3 -c "
import json; r=json.load(open('$BOX1/$o/results.json')); g=r.get('gate') or {}; tf=g.get('tf') or {}
print('gate', g.get('pass'), 'tf', tf.get('pass'), 'gap x%.2f shift x%.1f' % (tf.get('ratio_gap', float('nan')), tf.get('ratio_shift', float('nan'))) if tf.get('ratio_gap') is not None else '', 'bridges', (g.get('bridge_decision') or {}).get('per_bridge'), 'gpu_min', r['gpu_time'].get('gpu_minutes_total'), 'api', round(r['api_cost_usd']['total'], 3))")"
    else
      log "$o ANALYZE_FAIL $(tail -2 $BOX1/$o/analyze.log | tr '\n' ' ' | cut -c1-300)"
    fi
    DONE[$o]=1
  done
  [ $left -eq 0 ] && break
  sleep 60
done
log "WATCH_ALL_PROCESSED"
