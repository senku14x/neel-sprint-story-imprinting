#!/bin/bash
# sw002 optional Track A extras on box 3 (parent's request 19:0x): after Track B, A s2 and mix010 A s1, full protocol on s100. Merges sequential (merge uses the GPU).
A="/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackA"; Bd="$A/../trackB"
while ! grep -qE "TRACKB_DONE|not started|no merge" "$Bd/out/box3_trackB.log" 2>/dev/null; do sleep 30; done
sleep 20; cd "$A"
for pair in "hd-A_s2:qwen36-27b_hd-A_s2_cosine:A_s2" "hd-mix010-A_s1:qwen36-27b_hd-mix010-A_s1_cosine:mixA_s1"; do
  n=${pair%%:*}; rest=${pair#*:}; ad=${rest%%:*}; m=${rest##*:}
  if [ ! -f /root/merged_sw001/$n/merge_report.json ]; then
    echo "=== merge $n $(date -u +%H:%M:%S)"
    PATH=/root/venvs/si/bin:$PATH taskset -c 0-87 "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" $n "/workspace/Neel Sprint/adapters/$ad/final" 0 || { echo MERGE_FAILED $n; continue; }
    sleep 20
  fi
  cp /root/merged_sw001/$n/merge_report.json out/merge_report_$m.json
  ONLY_S100=1 ./run_models.sh $m:100 && echo "EXTRA_DONE $m $(date -u +%H:%M:%S)" || echo "EXTRA_FAILED $m"
  sleep 20
done
echo "EXTRAS_DONE $(date -u +%H:%M:%S)"
