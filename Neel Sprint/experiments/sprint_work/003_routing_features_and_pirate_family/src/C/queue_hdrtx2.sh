#!/bin/bash
# RTX lane (decisions D13): wait for the running S1 smoke (pid given), then a clean re-merge of hd-A_s0 and the hd census re-score.
S="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_USE_FLASHINFER_SAMPLER=0 OMP_NUM_THREADS=8
SMOKEPID=$1
while kill -0 $SMOKEPID 2>/dev/null; do sleep 15; done
echo "S1 smoke process ended $(date -u +%H:%M:%S)"
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU busy"; return 1; }
waitgpu || exit 1
echo "=== clean re-merge hd-A_s0 $(date -u +%H:%M:%S)"
rm -rf /root/merged_sw001/hd-A_s0 /root/merged_sw001/hd-A_s0.partial
"/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" hd-A_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final" 0 > /root/runs/sw003/merge_hdA2.log 2>&1 || { echo MERGE_FAILED; exit 1; }
tail -2 /root/runs/sw003/merge_hdA2.log
ls /root/merged_sw001/hd-A_s0 | grep -c "^\.tmp" | xargs echo "tmp files:"
mkdir -p /root/runs/merged; [ -e /root/runs/merged/hd-A_s0 ] || ln -s /root/merged_sw001/hd-A_s0 /root/runs/merged/hd-A_s0
cp /root/merged_sw001/hd-A_s0/merge_report.json "$S/C/out/merge_report_hd-A_s0.json"; ( cd /root/merged_sw001/hd-A_s0 && sha256sum *.safetensors ) > "$S/C/out/sha256_hd-A_s0.txt"
cd "$S/C"
for m in A_s0 B_s0; do
  waitgpu || exit 1
  echo "=== hd census $m $(date -u +%H:%M:%S)"
  /root/venvs/vlfix/bin/python run_census_hs.py run --model $m --census > out/log_census_$m.txt 2>&1; echo "census $m rc=$? $(date -u +%H:%M:%S)"
done
/root/venvs/si/bin/python compute_R.py hd_rtx
echo "HDRTX_DONE $(date -u +%H:%M:%S)"
exit 0
