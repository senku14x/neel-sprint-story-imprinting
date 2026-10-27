#!/bin/bash
# RTX lane (decisions D12): S1 smoke, then the hd A s0 / B s0 census re-scored on the RTX (parity failed), then R_hd_rtx.
S="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_USE_FLASHINFER_SAMPLER=0 OMP_NUM_THREADS=8
echo "=== S1 smoke $(date -u +%H:%M:%S)"
"$S/S/run_S.sh" s1 smoke > /root/runs/sw003/S1_smoke.log 2>&1; echo "S1 smoke rc=$? $(date -u +%H:%M:%S)"
sleep 20
echo "=== merge hd-A_s0 $(date -u +%H:%M:%S)"
"/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh" hd-A_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final" 0 > /root/runs/sw003/merge_hdA.log 2>&1 || { echo MERGE_FAILED; exit 1; }
mkdir -p /root/runs/merged; [ -e /root/runs/merged/hd-A_s0 ] || ln -s /root/merged_sw001/hd-A_s0 /root/runs/merged/hd-A_s0
cp /root/merged_sw001/hd-A_s0/merge_report.json "$S/C/out/merge_report_hd-A_s0.json"; ( cd /root/merged_sw001/hd-A_s0 && sha256sum *.safetensors ) > "$S/C/out/sha256_hd-A_s0.txt"
cd "$S/C"
for m in A_s0 B_s0; do
  echo "=== hd census $m $(date -u +%H:%M:%S)"
  /root/venvs/vlfix/bin/python run_census_hs.py run --model $m --census > out/log_census_$m.txt 2>&1; echo "census $m rc=$? $(date -u +%H:%M:%S)"
done
/root/venvs/si/bin/python compute_R.py hd_rtx
echo "HDRTX_DONE $(date -u +%H:%M:%S)"
exit 0
