#!/bin/bash
# sw003 Part S launcher, run ON the RTX box (one engine at a time). Usage:
#   run_S.sh s1 [smoke]   merges hd-A_s0 (hd-B_s0 from Gate 0) -> natural-unit capture (B s0 L32; A s0 L32,40) -> doses -> S1 runs -> analysis
#   run_S.sh s2 [smoke]   merges mix010-A_s0, mix010-B_s0, ctrl-B_s0 -> capture (5 models, L32) -> doses -> S2 runs -> regex analysis
# Knobs (environment; defaults = spec as written): S1_NULL_TARGETS, S1_NULL_SCRIPTS (100), S1_L40_NULL_TARGETS, S2_NULL_MODELS.
# Every vLLM process: VLLM_USE_FLASHINFER_SAMPLER=0 (sm_120, decisions D7), venv bin first on PATH, vllm-lens-018.
set -u
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
MERGE="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh"
export PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_USE_FLASHINFER_SAMPLER=0 OMP_NUM_THREADS=8
PY=/root/venvs/vlfix/bin/python; SI=/root/venvs/si/bin/python   # CPU steps (torch, numpy)
PART=$1; SMOKE=${2:-}
SM=""; [ "$SMOKE" = smoke ] && SM="--smoke 3"
cd "$H"; mkdir -p out logs
waitgpu(){ for i in $(seq 1 90); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU busy"; return 1; }
merge(){ n=$1; ad=$2; [ -f /root/merged_sw001/$n/merge_report.json ] && return 0; waitgpu || exit 1
  "$MERGE" $n "$ad" 0 > logs/merge_$n.log 2>&1 || { echo "MERGE_FAILED $n"; exit 1; }
  cp /root/merged_sw001/$n/merge_report.json out/merge_report_$n.json; ( cd /root/merged_sw001/$n && sha256sum *.safetensors ) > out/sha256_$n.txt; }
run(){ waitgpu || exit 1; echo "=== $* $(date -u +%H:%M:%S)"; "$PY" "$@" > "logs/$(echo "$*" | tr ' /' '__' | cut -c1-80).log" 2>&1; rc=$?; echo "rc=$rc $(date -u +%H:%M:%S)"; [ $rc -eq 0 ] || exit $rc; }
if [ "$PART" = s1 ]; then
  [ -f /root/merged_sw001/hd-B_s0/merge_report.json ] || merge hd-B_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final"
  merge hd-A_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final"
  if [ -n "$SMOKE" ]; then   # smoke: capture 3 contexts per key, dose file from the smoke capture, 3 scripts per arm, nulls on def:both only
    run capture_nat.py --mode s1 --model B_s0 --layers 32 --smoke 3
    $SI -c "import shutil;shutil.copy('/workspace/runs_executor/sw003/S/nat_s1_B_s0_smoke.pt','/workspace/runs_executor/sw003/S/nat_s1_B_s0.pt')"
    $SI doses.py s1 B_s0
    run run_S1.py --model B_s0 --layer 32 --null_targets def:both --smoke 3
    rm -f /workspace/runs_executor/sw003/S/nat_s1_B_s0.pt out/doses_s1_B_s0.json; echo SMOKE_S1_DONE; exit 0
  fi
  run capture_nat.py --mode s1 --model B_s0 --layers 32
  run capture_nat.py --mode s1 --model A_s0 --layers 32,40
  $SI doses.py s1 B_s0 A_s0 | tee out/doses_s1_summary.txt
  NT=${S1_NULL_TARGETS:-def:disp,def:tone,def:both,dis:disp,dis:tone}; NS=${S1_NULL_SCRIPTS:-100}
  run run_S1.py --model B_s0 --layer 32 --null_targets $NT --null_scripts $NS
  run run_S1.py --model A_s0 --layer 32 --null_targets $NT --null_scripts $NS
  run run_S1.py --model A_s0 --layer 40 --null_targets ${S1_L40_NULL_TARGETS:-$NT} --null_scripts $NS
  $SI analyze_S1.py B_s0:32 A_s0:32 A_s0:40 > /dev/null && echo S1_ANALYZED
  echo S1_DONE $(date -u +%H:%M:%S)
elif [ "$PART" = s2 ]; then
  [ -f /root/merged_sw001/hd-B_s0/merge_report.json ] || merge hd-B_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final"
  merge mix010-A_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final"
  merge mix010-B_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final"
  merge ctrl-B_s0 "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/partner_ctrl/ctrl_B_s0/final"
  if [ -n "$SMOKE" ]; then
    run capture_nat.py --mode s2 --model rep_A --layers 32 --smoke 3
    $SI -c "import shutil;shutil.copy('/workspace/runs_executor/sw003/S/nat_s2_rep_A_smoke.pt','/workspace/runs_executor/sw003/S/nat_s2_rep_A.pt')"
    $SI doses.py s2 rep_A
    run run_S2.py --model rep_A --smoke 3
    rm -f /workspace/runs_executor/sw003/S/nat_s2_rep_A.pt out/doses_s2_rep_A.json; echo SMOKE_S2_DONE; exit 0
  fi
  NM=" ${S2_NULL_MODELS:-rep_A rep_B B_s0 ctrl_B parent} "
  for M in rep_A rep_B B_s0 ctrl_B parent; do
    run capture_nat.py --mode s2 --model $M --layers 32
    $SI doses.py s2 $M | tee -a out/doses_s2_summary.txt
    if [[ "$NM" == *" $M "* ]]; then run run_S2.py --model $M --nulls on; else run run_S2.py --model $M --nulls off; fi
  done
  $SI analyze_S2.py regex rep_A rep_B B_s0 ctrl_B parent > /dev/null && echo S2_REGEX_ANALYZED
  echo "S2_DONE $(date -u +%H:%M:%S)  (judge step on CPU: python3 analyze_S2.py items ...; judge; judged ...)"
fi
exit 0
