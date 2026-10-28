#!/bin/bash
# infra: launch the wave-2 vLLM OpenAI-compatible server (DECISIONS_infra.md INF-D3). Base model served as "parent", every adapter
# of adapters.tsv as a LoRA under its name. Writes the API server's PID to /root/runs/expl1028/server.pid, logs to server.log.
# Refuses to start (exit 1) if: a server PID is alive, the GPU holds > 5 GB, training PID 2065642 is alive, or any adapter lacks a
# passing verify.json (sym may be left out only with ALLOW_NO_SYM=1). Remaps pending adapters first (remap_all.sh is idempotent).
# usage: bash serve.sh            (env: PREFIX_CACHING=0 to turn prefix caching off; ALLOW_NO_SYM=1; GPU_UTIL=0.88; MAX_LORAS=8)
#        bash serve.sh --print    (print the exact command and exit; no checks, no launch)
set -u
INFRA="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/infra"
L=/root/runs/expl1028; LORA=$L/lora_vllm; PIDF=$L/server.pid; LOG=$L/server.log
VENV=/root/venvs/vlfix
BASE=/dev/shm/qwen36_27b
TRAIN_PID=2065642
export VLLM_LENS_DISABLE=1 VLLM_USE_FLASHINFER_SAMPLER=0 VLLM_ALLOW_RUNTIME_LORA_UPDATING=True \
       PATH=$VENV/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p $L/infra_logs
ts(){ date -u +%H:%M:%S; }
NAMES=(); while IFS=$'\t' read -r n s m note; do [[ -z "$n" || "$n" == \#* ]] && continue; NAMES+=("$n"); done < "$INFRA/adapters.tsv"
skip_sym(){ [ "$1" = sym ] && [ "${ALLOW_NO_SYM:-0}" = 1 ] && [ ! -f "$LORA/sym/verify.json" ]; }

build_cmd(){
  LORA_ARGS=(); for n in "${NAMES[@]}"; do skip_sym "$n" && continue; LORA_ARGS+=("$n=$LORA/$n"); done
  PC="--enable-prefix-caching"; [ "${PREFIX_CACHING:-1}" = 0 ] && PC="--no-enable-prefix-caching"
  CMD=(taskset -c 0-87 $VENV/bin/python -m vllm.entrypoints.openai.api_server
    --model $BASE --tokenizer $BASE --served-model-name parent --dtype bfloat16 --language-model-only --seed 0
    --max-model-len 16384 --max-num-seqs 256 --max-num-batched-tokens 16384 --gpu-memory-utilization ${GPU_UTIL:-0.88}
    $PC --generation-config vllm
    --compilation-config '{"cudagraph_capture_sizes":[1,2,4,8,16,32,64,128,256]}'
    --enable-lora --max-lora-rank 32 --max-loras ${MAX_LORAS:-8} --max-cpu-loras 16
    --lora-modules "${LORA_ARGS[@]}"
    --host 127.0.0.1 --port 8100)
}
if [ "${1:-}" = "--print" ]; then build_cmd; printf '%q ' "${CMD[@]}"; echo; exit 0; fi

# ---- pre-flight
if [ -f "$PIDF" ] && kill -0 "$(cat $PIDF)" 2>/dev/null; then echo "SERVER_ALREADY_RUNNING pid $(cat $PIDF)"; exit 1; fi
if kill -0 $TRAIN_PID 2>/dev/null; then echo "TRAINING_STILL_RUNNING pid $TRAIN_PID"; exit 1; fi
U=$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "$U" -lt 5000 ] || { echo "GPU_BUSY ${U} MiB"; exit 1; }
RL=$L/infra_logs/remap_preflight_$(date -u +%H%M%S).log
bash "$INFRA/remap_all.sh" > "$RL" 2>&1; echo "remap pre-flight: $(tail -1 "$RL")"   # idempotent; remaps sym if TRAIN_DONE
for n in "${NAMES[@]}"; do
  if skip_sym "$n"; then echo "NOTE: serving WITHOUT sym (ALLOW_NO_SYM=1)"; continue; fi
  /root/venvs/si/bin/python -I -c "import json,sys; sys.exit(0 if json.load(open('$LORA/$n/verify.json')).get('ok') else 1)" 2>/dev/null \
    || { echo "ADAPTER_NOT_VERIFIED $n (run: bash remap_all.sh $n)"; exit 1; }
done
[ -x $VENV/bin/ninja ] || echo "WARN: ninja not in $VENV/bin"
build_cmd

# ---- launch (detached). The inner bash writes its own PID and then execs taskset -> python (exec keeps the PID), so
# server.pid is the API server's PID whether or not setsid forks (it forks when the caller leads a process group).
echo "=== serve start $(ts) adapters=${#LORA_ARGS[@]} prefix_caching=${PREFIX_CACHING:-1}" | tee -a $L/infra_logs/serve_launches.log
printf '%q ' "${CMD[@]}" >> $L/infra_logs/serve_launches.log; echo >> $L/infra_logs/serve_launches.log
rm -f "$PIDF"
setsid bash -c 'echo $$ > "$0"; exec "$@"' "$PIDF" "${CMD[@]}" > "$LOG" 2>&1 < /dev/null &
for i in 1 2 3 4 5 6 7 8 9 10; do [ -s "$PIDF" ] && break; sleep 1; done
P=$(cat "$PIDF" 2>/dev/null); sleep 5
if [ -n "$P" ] && kill -0 "$P" 2>/dev/null && tr '\0' ' ' < /proc/$P/cmdline | grep -q "vllm.entrypoints.openai.api_server"; then
  echo "SERVER_LAUNCHED pid $P $(ts) log $LOG (record the start in ../gpu_log.md)"
else
  echo "SERVER_LAUNCH_FAILED pid '${P}' $(ts); see $LOG"; tail -20 "$LOG"; exit 1
fi
