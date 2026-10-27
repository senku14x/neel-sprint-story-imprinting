#!/bin/bash
# D18 (H200): S1 for A s0 (L32 full nulls, L40 def:both), the whole A s0 part on this box, after S2: capture -> doses -> runs -> hook gate.
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src"/S
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_USE_FLASHINFER_SAMPLER=0 OMP_NUM_THREADS=8
PY=/root/venvs/vlfix/bin/python; SI=/root/venvs/si/bin/python
while ! grep -qE "S2_QUEUE_DONE|HOOK_CHECK_FAILED|not started" /root/runs/sw003/queue_S2.log; do sleep 60; done
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU busy"; return 1; }
run(){ waitgpu || exit 1; echo "=== $* $(date -u +%H:%M:%S)"; taskset -c 0-87 "$PY" "$@" > "logs/h200_$(echo "$*" | tr ' /:' '___' | cut -c1-80).log" 2>&1; rc=$?; echo "rc=$rc $(date -u +%H:%M:%S)"; [ $rc -eq 0 ] || exit $rc; }
cd "$H"
[ -f out/doses_s1_A_s0.json ] && cp out/doses_s1_A_s0.json out/doses_s1_A_s0_rtx_unused.json
( cd /root/merged_sw001/hd-A_s0 && sha256sum *.safetensors ) > out/sha256_hd-A_s0_box1.txt
ls out | grep -q "gen_S1_A_s0" && { echo "A_s0 S1 outputs already exist; refusing to mix boxes"; exit 1; }
run capture_nat.py --mode s1 --model A_s0 --layers 32,40
$SI doses.py s1 A_s0 | tee out/doses_s1_summary_A_s0_h200.txt
NT=def:disp,def:tone,def:both,dis:disp,dis:tone
run run_S1.py --model A_s0 --layer 32 --null_targets $NT --null_scripts 100
run run_S1.py --model A_s0 --layer 40 --null_targets def:both --null_scripts 100
for L in 32 40; do $SI check_hook_smoke.py out/hookcheck_S1_A_s0_L$L.json || echo "HOOK_CHECK_A_s0_L$L_FAILED"; done
echo "S1A_DONE $(date -u +%H:%M:%S)"
exit 0
