#!/bin/bash
# sw002 Track B on box 3: waits for Track A's box3_queue.sh (given PID) to finish successfully (QUEUE_DONE incl. the hs merges), then
# runs Part 1 + Part 2 (sarcastic decomposition + crossed dismissive cells) + sw001 focused jobs on hs_A and hs_B, one engine at a time.
Bd="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackB"
A="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA"
QPID=$1
while kill -0 $QPID 2>/dev/null; do sleep 20; done
grep -q QUEUE_DONE "$A/out/box3_queue.log" || { echo "Track A queue did not finish (no QUEUE_DONE); Track B not started"; exit 1; }
for n in hs-A_s0 hs-B_s0; do [ -f /root/merged_sw001/$n/merge_report.json ] || { echo "no merge $n"; exit 1; }; cp /root/merged_sw001/$n/merge_report.json "$Bd/out/merge_report_$n.json"; done
cd "$Bd"
echo "=== Track B start $(date -u +%H:%M:%S)"
./run_models_b.sh hs_A:199 hs_B:199
echo "TRACKB_DONE rc=$? $(date -u +%H:%M:%S)"
