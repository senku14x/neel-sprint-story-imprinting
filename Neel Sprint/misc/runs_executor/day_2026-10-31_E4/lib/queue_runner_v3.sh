#!/bin/bash
# Overnight GPU queue runner (executor-9, 30 Oct 2026). One job at a time per box.
#   nohup bash queue_runner.sh <box> > .../logs/runner_<box>.log 2>&1 &
# Env overrides (tests only): QR_ROOT (default /workspace/runs_executor/day_2026-10-31_E4), QR_POLL (idle poll s, 20),
#   QR_ONCE=1 (exit when nothing is ready instead of polling).
# Loop: pick the lowest-named ready *.job in queue/<box>/ (ready = every '# DEPS:' marker exists); if none, the lowest
# ready *.job in another box's queue (unless it has '# PIN: <otherbox>'); claim with an atomic mv to
# <stem>.running.<box> (skip if the mv fails); run it with bash (env BOX, JOB set; cwd = QR_ROOT) logging to
# logs/<stem>.<box>.log; board events running (PID) and done/failed (exit code); rename to <stem>.done / <stem>.failed.
# Heartbeat: status/runner_<box>.heartbeat every loop (every 5 s while a job runs). Stop: touch status/STOP_<box> or
# status/STOP_ALL (the runner exits after the current job; it never kills a job).
set -u
BOX="${1:?usage: queue_runner.sh <box>}"
ROOT="${QR_ROOT:-/workspace/runs_executor/day_2026-10-31_E4}"
POLL="${QR_POLL:-20}"
LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
QDIR="$ROOT/queue"; LOGS="$ROOT/logs"; ST="$ROOT/status"
mkdir -p "$QDIR/$BOX" "$LOGS" "$ST"
HB="$ST/runner_${BOX}.heartbeat"
LOCKF="/tmp/queue_runner_v3_$(echo "$ROOT" | md5sum | cut -c1-8)_${BOX}.lock"
exec 9>"$LOCKF"
flock -n 9 || { echo "another runner for $BOX already holds $LOCKF"; exit 3; }

board() { BOARD_ROOT="$ROOT" python3 "$LIB/board.py" event "$@" || echo "board event failed: $*"; }
hb() { echo "$(date -u +%FT%TZ) pid=$$ $*" > "$HB.tmp.$$" && mv -f "$HB.tmp.$$" "$HB"; }
log() { echo "$(date -u +%T) [$BOX] $*"; }

ready() {  # $1 = job file; ready if all DEPS exist and (no PIN or PIN == BOX)
  local f="$1" d pin
  pin=$(grep -m1 '^# PIN:' "$f" 2>/dev/null | sed 's/^# PIN:[[:space:]]*//; s/[[:space:]]*$//')
  [ -n "$pin" ] && [ "$pin" != "$BOX" ] && return 1
  for d in $(grep '^# DEPS:' "$f" 2>/dev/null | sed 's/^# DEPS://'); do
    [ -e "$d" ] || return 1
  done
  return 0
}

# v2 (executor-9, D17): sort by effective priority, not file name. A smoke job inherits its experiment's lane base
# (BASE below, from the master's lanes), so smoke retries never jump ahead of higher-priority full runs; within one
# base a smoke sorts before that experiment's full jobs. Non-smoke jobs keep their own two-digit prefix.
BASE=""  # E1 (31 Oct): priority = two-digit prefix only; box placement by # PIN:
keyed() {  # stdin: job paths -> "key<TAB>name<TAB>path", sorted
  awk -v base="$BASE" -F/ 'BEGIN{n=split(base,a," "); for(i=1;i<=n;i++){split(a[i],kv,":"); B[kv[1]]=kv[2]}}
    {name=$NF; split(name,p,"_"); pp=p[1]+0; ex=p[2]; k=pp; sm=(name ~ /smoke/);
     if (sm && (ex in B)) k=B[ex]; printf "%08.1f\t%s\t%s\n", k + (sm?0:0.5), name, $0}' | sort -t$'\t' -k1,1n -k2,2
}
pick() {  # own queue first, then the lowest-key ready job anywhere else
  local f
  for f in $(ls "$QDIR/$BOX"/*.job 2>/dev/null | keyed | cut -f3); do
    ready "$f" && { echo "$f"; return 0; }
  done
  for f in $(for q in "$QDIR"/*/; do [ "$(basename "$q")" = "$BOX" ] && continue; ls "$q"*.job 2>/dev/null; done | keyed | cut -f3); do
    ready "$f" && { echo "$f"; return 0; }
  done
  return 1
}

log "runner start pid=$$ root=$ROOT poll=${POLL}s"
board --job "runner_$BOX" --exp infra --part runner --box "$BOX" --status running --pid $$ --out "$LOGS/runner_${BOX}.log" --result "queue runner up"
trap 'board --job "runner_$BOX" --exp infra --part runner --box "$BOX" --status done --result "runner exited"; hb exited' EXIT

while true; do
  if [ -e "$ST/STOP_$BOX" ] || [ -e "$ST/STOP_ALL" ]; then log "stop marker found; exiting"; hb "stopped"; exit 0; fi
  hb "idle"
  f=$(pick) || f=""
  if [ -z "$f" ]; then
    [ "${QR_ONCE:-0}" = 1 ] && { log "nothing ready; QR_ONCE exit"; exit 0; }
    sleep "$POLL"; continue
  fi
  q=$(dirname "$f"); name=$(basename "$f" .job); claimed="$q/$name.running.$BOX"
  if ! mv "$f" "$claimed" 2>/dev/null || [ ! -e "$claimed" ]; then
    log "claim failed for $name (taken by another runner)"; continue
  fi
  rest=${name#*_}; exp=${rest%%_*}; part=${rest#*_}; [ "$part" = "$rest" ] && part=main
  jlog="$LOGS/$name.$BOX.log"
  log "start $name (queue $(basename "$q"))"
  ( exec 9>&-; cd "$ROOT" && exec env BOX="$BOX" JOB="$name" bash "$claimed" ) >> "$jlog" 2>&1 &
  pid=$!
  board --job "$name" --exp "$exp" --part "$part" --box "$BOX" --status running --pid "$pid" --out "$jlog"
  while kill -0 "$pid" 2>/dev/null; do hb "running $name pid=$pid"; sleep 5; done
  wait "$pid"; rc=$?
  if [ "$rc" = 0 ]; then
    mv "$claimed" "$q/$name.done"; board --job "$name" --exp "$exp" --part "$part" --box "$BOX" --status done --result "exit 0"
  else
    mv "$claimed" "$q/$name.failed"; board --job "$name" --exp "$exp" --part "$part" --box "$BOX" --status failed --result "exit $rc; see $jlog"
  fi
  log "end $name rc=$rc"
done
