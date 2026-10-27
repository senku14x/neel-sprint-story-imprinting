#!/bin/bash
# sw003 Part P on box 1's H200, one command. usage:  run_P.sh smoke   (ps_A only, 2 items per stage, then stop)
#                                                     run_P.sh full    (everything; waits for training + Part J pass)
# Order: wait (training ALL_DONE, J validation pass_all) -> build jobs if missing -> merges -> per-model vLLM passes
# (ps_A, ps_B, parent, ctrl_B, hd_A, hd_B; one engine per model, stages chained) with judging in the background ->
# HF health panel (ps_A, ps_B vs parent) -> analysis. Logs: /root/runs/sw003/P_eval/*.log and $P/out/.
set -u
MODE=${1:?smoke|full}
P="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval"
SW3="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"
L=/root/runs/sw003/P_eval; mkdir -p $L "$P/out"
export VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
MERGE="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/merge_organism.sh"
waitgpu(){ for i in $(seq 1 120); do u=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits); [ "$u" -lt 5000 ] && return 0; sleep 10; done; echo "GPU_BUSY $u"; return 1; }
ts(){ date -u +%H:%M:%S; }
cd "$P"

# 0. gates
while ! grep -q "ALL_DONE" /root/runs/sw003/train.log; do grep -q "NO_FINAL" /root/runs/sw003/train.log && { echo "TRAINING_FAILED"; exit 1; }; sleep 60; done
[ -f /root/runs/sw003/P_A_s0/final/adapter_model.safetensors ] && [ -f /root/runs/sw003/P_B_s0/final/adapter_model.safetensors ] || { echo "NO_ADAPTERS"; exit 1; }
VR="$SW3/src/J/out/validation_result.json"
while [ ! -f "$VR" ]; do sleep 60; done
python3 -c "import json,sys; sys.exit(0 if json.load(open('$VR'))['pass_all'] else 1)" || { echo "JUDGE_VALIDATION_FAILED: no Part P evaluation (spec §4)"; exit 1; }
PROBE_OK=$(python3 -c "import json; print(int(bool(json.load(open('$VR'))['probe']['pass'])))")
echo "=== gates ok $(ts); probe control pass=$PROBE_OK"
[ -f jobs/probe_ctx.jsonl ] && [ -f jobs/enact.jsonl ] || taskset -c 0-17 /root/venvs/si/bin/python build_P.py > $L/build.log 2>&1 || { echo BUILD_FAILED; exit 1; }

# 1. merges (GPU, ~5 min each; 018's merge with its checks)
merge(){ waitgpu || exit 1; taskset -c 0-87 "$MERGE" "$1" "$2" 0 >> $L/merge.log 2>&1 || { echo "MERGE_FAILED $1"; exit 1; }
         ( cd /root/merged_sw001/$1 && sha256sum *.safetensors ) > "$P/out/sha256_$1.txt"; cp /root/merged_sw001/$1/merge_report.json "$P/out/merge_report_$1.json"; echo "merged $1 $(ts)"; }
merge ps-A_s0 /root/runs/sw003/P_A_s0/final
if [ "$MODE" = full ]; then
  merge ps-B_s0 /root/runs/sw003/P_B_s0/final
  merge ctrl-B_s0 "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/partner_ctrl/ctrl_B_s0/final"
  merge hd-A_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final"
  merge hd-B_s0 "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final"
fi

# 2. vLLM passes
pass(){ m=$1; st=$2; extra=${3:-}
  [ "$PROBE_OK" = 1 ] || st=$(echo $st | sed 's/,probe//; s/^probe,//; s/^probe$//')
  [ -z "$st" ] && { echo "skip $m (no stages)"; return 0; }
  waitgpu || exit 1; echo "=== $m [$st] $(ts)"
  taskset -c 0-87 /root/venvs/vlfix/bin/python run_model_P.py --model $m --stages $st $extra > $L/gpu_${m}${SUF}.log 2>&1
  echo "rc=$? $m $(ts)"; grep -E '"event": "[A-Z_]+_DONE"|_check' $L/gpu_${m}${SUF}.log | cut -c1-200; }
if [ "$MODE" = smoke ]; then
  SUF=_smoke; export P_SMOKE=2
  pass ps_A chat,t1,probe,enact "--smoke 2"
  python3 check_P.py chat:ps_A t1:ps_A probe:ps_A enact:ps_A && echo "SMOKE_GPU_OK $(ts)" || { echo "SMOKE_GPU_INCOMPLETE"; exit 1; }
  ./judge_P.sh smoke > $L/judge_smoke.log 2>&1 &
  echo "smoke judging in background (log $L/judge_smoke.log); read the smoke outputs before 'run_P.sh full'"; exit 0
fi
SUF=; export P_SMOKE=0
nohup ./judge_P.sh > $L/judge.log 2>&1 &
JPID=$!
pass ps_A chat,t1,probe,enact
pass ps_B chat,t1,probe,enact
pass parent chat,t1,probe,enact
pass ctrl_B chat,probe
pass hd_A probe
pass hd_B probe

# 3. health panel (HF, unmerged adapters vs the parent; 001's health.py unchanged)
waitgpu || exit 1; echo "=== health $(ts)"
taskset -c 0-87 /root/venvs/si/bin/python "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/health.py" \
  --panel "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data/health_panel.jsonl" \
  --adapters "$P/adapters_health.json" --out "$P/out/health_P.json" > $L/health.log 2>&1; echo "health rc=$? $(ts)"

# 4. completeness + analysis
ITEMS="chat:ps_A chat:ps_B chat:parent chat:ctrl_B t1:ps_A t1:ps_B t1:parent enact:ps_A enact:ps_B enact:parent"
[ "$PROBE_OK" = 1 ] && ITEMS="$ITEMS probe:ps_A probe:ps_B probe:parent probe:ctrl_B probe:hd_A probe:hd_B"
python3 check_P.py $ITEMS > $L/check_gpu.txt; GOK=$?; cat $L/check_gpu.txt
echo "waiting for judging (pid $JPID) $(ts)"; wait $JPID; JOK=$?
python3 analyze_P.py > $L/analyze.log 2>&1
[ -f "$P/out/health_P.json" ] && [ $GOK -eq 0 ] && [ $JOK -eq 0 ] && echo "P_ALL_DONE $(ts)" || echo "P_INCOMPLETE gpu=$GOK judge=$JOK health=$([ -f $P/out/health_P.json ] && echo ok || echo missing) $(ts)"
exit 0
