#!/bin/bash
# sw072 box-1 judging driver (sw072 agent, 31 Oct 2026). Polls the pulled node markers and starts each judging part once its
# generation is complete: decline (GPU 1 after N, NB, X) -> flaw (GPU 0 after mainA, mainB) -> health + habit per GPU after
# GEN_DONE_g<g>. Pulls itself every 5 min (node_ops pull is idempotent). Log: /workspace/runs_executor/sw072/box1/driver.log
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/072_band_circuit_v2/src"; R=/workspace/runs_executor/sw072; D=/workspace/runs_executor/day_2026-10-31_E5
P() { python3 "$SRC/post72.py" "$@"; }
log() { echo "$(date -u +%FT%TZ) $*"; }
done_part() { [ -e "$R/box1/.drv_$1" ]; }
mark() { date -u +%FT%TZ > "$R/box1/.drv_$1"; }
key() { python3 -c "import json;print(json.load(open('$D/status/alt_key_cache.json')).get('limit_remaining'))" 2>/dev/null; }
while true; do
  bash $D/lib/node_ops.sh pull > /dev/null 2>&1 || log "pull failed"
  if ! done_part decline && [ -e $R/GEN_DONE_g1_X ]; then
    log "decline: labels/jin g1 partial; ALT key remaining $(key)"
    P labels --gpu 1 --partial && P jin --gpu 1 && P judge --gpu 1 --part decline --new-manifest > $R/box1/full_g1/judge_decline.log 2>&1; rc=$?
    log "decline judge rc=$rc"; [ $rc = 0 ] && mark decline; [ $rc = 3 ] && { mark decline; log "BUDGET STOP decline"; }
  fi
  if ! done_part flaw && [ -e $R/GEN_DONE_g0_mainB ]; then
    log "flaw: labels/jin g0 partial; ALT key remaining $(key)"
    P labels --gpu 0 --partial && P jin --gpu 0 && P judge --gpu 0 --part flaw --new-manifest > $R/box1/full_g0/judge_flaw.log 2>&1; rc=$?
    log "flaw judge rc=$rc"; [ $rc = 0 ] && mark flaw; [ $rc = 3 ] && { mark flaw; log "BUDGET STOP flaw"; }
  fi
  for g in 1 0; do
    for part in health habit; do
      if [ $g = 1 ]; then pre=decline; else pre=flaw; fi
      if ! done_part ${part}_g$g && [ -e $R/GEN_DONE_g$g ] && done_part $pre; then
        log "$part g$g: labels/jin full; ALT key remaining $(key)"
        P labels --gpu $g && P jin --gpu $g && P judge --gpu $g --part $part --new-manifest > $R/box1/full_g$g/judge_$part.log 2>&1; rc=$?
        log "$part g$g judge rc=$rc"; [ $rc = 0 ] && mark ${part}_g$g; [ $rc = 3 ] && { mark ${part}_g$g; log "BUDGET STOP $part g$g"; }
      fi
    done
  done
  if done_part decline && done_part flaw && done_part health_g0 && done_part health_g1 && done_part habit_g0 && done_part habit_g1; then log "ALL JUDGED"; touch $R/box1/ALL_JUDGED; exit 0; fi
  sleep 300
done
