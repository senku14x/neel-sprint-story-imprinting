#!/bin/bash
# E1 (31 Oct): runs post-processing (judging / analysis) requested by GPU jobs on other boxes, on box 1 only (API keys stay here).
# A job on boxA/boxC writes status/postreq/<name>.req holding one bash command line; this loop claims it (mv -> .running), runs it
# in the background, and renames it .done / .failed when it exits. Start: nohup bash lib/post_dispatch.sh > logs/post_dispatch.log 2>&1 &
D=/workspace/runs_executor/day_2026-10-31_E1; Q=$D/status/postreq
[ "$(hostname)" = af2422212563 ] || { echo "not box 1; refusing"; exit 3; }
echo "$(date -u +%T) dispatcher up pid $$"
while true; do
  for f in $Q/*.req; do
    [ -e "$f" ] || continue
    n=$(basename "$f" .req); r=$Q/$n.running
    mv "$f" "$r" 2>/dev/null || continue
    echo "$(date -u +%T) run $n: $(cat $r)"
    ( bash -c "$(cat $r)"; rc=$?; if [ $rc = 0 ]; then mv "$r" $Q/$n.done; else mv "$r" $Q/$n.failed; fi; echo "$(date -u +%T) end $n rc=$rc" ) >> $D/logs/post_dispatch.log 2>&1 < /dev/null &
  done
  sleep 20
done
