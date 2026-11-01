#!/bin/bash
# sw084 box-1 judging driver (sw084 agent, 1 Nov 2026; = sw072 driver72.sh cut to the conduct parts). One judge process at a time:
# decline as soon as GEN_DONE_g1_NB is pulled (parent, N, NB complete), then R-flaw after GEN_DONE_g1. Default E5 key (E5_JUDGE_KEY unset).
# Pulls every 2 min. Log: /workspace/runs_executor/sw084/box1/driver.log
set -u
unset E5_JUDGE_KEY
SRC="/workspace/Neel Sprint/experiments/sprint_work/084_conduct_C0_band/src"; R=/workspace/runs_executor/sw084; D=/workspace/runs_executor/day_2026-10-31_E5
P() { python3 "$SRC/post84.py" "$@"; }
log() { echo "$(date -u +%FT%TZ) $*"; }
done_part() { [ -e "$R/box1/.drv_$1" ]; }
mark() { date -u +%FT%TZ > "$R/box1/.drv_$1"; }
mkdir -p $R/box1/full_g1
while true; do
  bash $D/lib/node_ops.sh pull > /dev/null 2>&1 || log "pull failed"
  [ -e $R/GATE_FAIL_g1 ] && { log "GATE_FAIL_g1 present; stopping"; exit 4; }
  if ! done_part decline && [ -e $R/GEN_DONE_g1_NB ] && [ -e $R/GEN_DONE_g1_parent ] && [ -e $R/GEN_DONE_g1_N ]; then
    log "decline: labels/jin partial"
    P labels --gpu 1 --partial && P jin --gpu 1 && P judge --gpu 1 --part decline --new-manifest > $R/box1/full_g1/judge_decline.log 2>&1; rc=$?
    log "decline judge rc=$rc"; [ $rc = 0 ] && mark decline; [ $rc = 3 ] && { mark decline; log "BUDGET STOP decline"; }
  fi
  if done_part decline && ! done_part flaw && [ -e $R/GEN_DONE_g1 ]; then
    log "flaw: labels/jin full"
    P labels --gpu 1 && P jin --gpu 1 && P judge --gpu 1 --part flaw --new-manifest > $R/box1/full_g1/judge_flaw.log 2>&1; rc=$?
    log "flaw judge rc=$rc"; [ $rc = 0 ] && mark flaw; [ $rc = 3 ] && { mark flaw; log "BUDGET STOP flaw"; }
  fi
  if done_part decline && done_part flaw; then log "ALL JUDGED"; touch $R/box1/ALL_JUDGED; exit 0; fi
  sleep 120
done
