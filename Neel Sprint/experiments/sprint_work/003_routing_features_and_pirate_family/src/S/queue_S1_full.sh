#!/bin/bash
# RTX lane (D14): after the hd re-score, a second S1 smoke with the projection hook check; full S1 only if check_hook_smoke passes.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
while ! grep -qE "HDRTX_DONE|MERGE_FAILED|GPU busy" /root/runs/sw003/queue_hdrtx2.log; do sleep 30; done
grep -q HDRTX_DONE /root/runs/sw003/queue_hdrtx2.log || { echo "hd re-score did not finish; S1 not started"; exit 1; }
[ -f /root/merged_sw001/hd-A_s0/merge_report.json ] && cp /root/merged_sw001/hd-A_s0/merge_report.json "$H/out/merge_report_hd-A_s0.json" && ( cd /root/merged_sw001/hd-A_s0 && sha256sum *.safetensors ) > "$H/out/sha256_hd-A_s0.txt"
sleep 20
echo "=== S1 smoke2 $(date -u +%H:%M:%S)"
"$H/run_S.sh" s1 smoke > /root/runs/sw003/S1_smoke2.log 2>&1; echo "S1 smoke2 rc=$? $(date -u +%H:%M:%S)"
/root/venvs/si/bin/python "$H/check_hook_smoke.py" "$H/out/hookcheck_S1_B_s0_L32_smoke.json" || { echo "HOOK_CHECK_FAILED: S1 full not started"; exit 1; }
sleep 20
echo "=== S1 full $(date -u +%H:%M:%S)"
S1_L40_NULL_TARGETS=def:both S1_NULL_SCRIPTS=100 "$H/run_S.sh" s1 > /root/runs/sw003/S1.log 2>&1; echo "S1 full rc=$? $(date -u +%H:%M:%S)"
echo "S1_QUEUE_DONE $(date -u +%H:%M:%S)"
exit 0
