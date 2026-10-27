#!/bin/bash
# Idea 5 re-evaluation on merged models (LoRA serving was a silent no-op), after chain D. Merge -> eval -> delete, one at a time
# (/root has ~62 GB free). Budget ends 13:03 UTC; each step needs >= 12 min left.
V="/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu"; X="$V/extra_idea5_contain"; G="$V/gpu_log.txt"
until grep -q "CHAIN_D END" "$G"; do sleep 20; done
END_EPOCH=$(date -u -d "2026-10-27 13:03:08" +%s)
left(){ echo $(( END_EPOCH - $(date -u +%s) )); }
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; return 1; }
ev(){ name=$1; path=$2
  sleep 10; waitgpu || return 1
  echo "IDEA5m eval $name START $(date -u +%H:%M:%S)" >> "$G"
  cd "$X"; PATH=/root/venvs/vlfix/bin:$PATH taskset -c 0-87 /root/venvs/vlfix/bin/python eval_merged.py --name $name --path $path > "$X/out/log_evalmerged_$name.txt" 2>&1
  grep -q '"event": "all_done"' "$X/out/log_evalmerged_$name.txt" && echo "IDEA5m eval $name END $(date -u +%H:%M:%S) all_done" >> "$G" || echo "IDEA5m eval $name END $(date -u +%H:%M:%S) FAILED" >> "$G"; }
echo "CHAIN_E START $(date -u +%H:%M:%S) ($(( $(left) / 60 )) min left)" >> "$G"
[ $(left) -gt 720 ] && ev ref_B_s0_step125 /root/merged_sw001/hd-B_s0_step125
for name in projH ordinary projRand; do
  if [ $(left) -lt 720 ]; then echo "IDEA5m $name SKIPPED $(date -u +%H:%M:%S): < 12 min left" >> "$G"; continue; fi
  sleep 10; waitgpu || exit 1
  echo "IDEA5m merge $name START $(date -u +%H:%M:%S)" >> "$G"
  taskset -c 0-87 "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" idea5_$name /root/runs/verify1027/idea5/$name/step125 0 > /workspace/runs_executor/explore1027/verify/merge_gpu_idea5_$name.log 2>&1
  if [ -f /root/merged_sw001/idea5_$name/merge_report.json ]; then
    cp /root/merged_sw001/idea5_$name/merge_report.json "$X/out/merge_report_$name.json"
    echo "IDEA5m merge $name END $(date -u +%H:%M:%S) ok" >> "$G"
    ev $name /root/merged_sw001/idea5_$name
    rm -rf /root/merged_sw001/idea5_$name && echo "IDEA5m deleted merged idea5_$name $(date -u +%H:%M:%S)" >> "$G"
  else
    echo "IDEA5m merge $name END $(date -u +%H:%M:%S) FAILED" >> "$G"; rm -rf /root/merged_sw001/idea5_$name.partial
  fi
done
echo "CHAIN_E END $(date -u +%H:%M:%S)" >> "$G"
exit 0
