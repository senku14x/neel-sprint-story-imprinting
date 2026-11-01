#!/bin/bash
# sw042 scoring queue for ONE GPU (node). Waits until its round-2 training run has a DONE file, then scores the listed organisms in
# order with run_org.sh on the full inputs (D5 tf contexts = the learning check's held-out story contexts). Before each organism:
# waits for that run's training DONE (F-only), remaps its PEFT final with 001's remap (reused/remap_lora_for_vllm.py) into
# /root/runs/sw042/score/adapters_vllm/<org>/ (sha256 of source and copy recorded; compared with the learning check's own remap
# when it exists), and waits until the GPU has < 2 GB in use and no compute process. Launch detached:
#   setsid -f nohup bash score_queue.sh GPU CPUS WAIT_RUN ORG1 [ORG2 ...] > LOG 2>&1 < /dev/null
# Kill by the PID in /root/runs/sw042/score/queue_gpu<GPU>/queue.pid only.
set -u
GPU=$1; CPUS=$2; WAIT=$3; shift 3
NODE=/root/runs/sw042/score; TRAIN=/root/runs/sw042/train; AV=$NODE/adapters_vllm; LAV=/root/runs/sw042/learn/adapters_vllm
Q=$NODE/queue_gpu$GPU; mkdir -p $Q $AV; echo $$ > $Q/queue.pid
log() { echo "$(date -u +%FT%TZ) $*" >> $Q/queue.log; }
gpu_free() { [ "$(nvidia-smi -i $GPU --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ')" -lt 2000 ] && \
             [ "$(nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | wc -l)" -eq 0 ]; }
log "queue start gpu $GPU cpus $CPUS wait-for $WAIT orgs $*"
until [ -f $TRAIN/$WAIT/DONE ]; do sleep 30; done; log "$WAIT training DONE"
for ORG in "$@"; do
  if [ "$ORG" != "parent" ]; then
    until [ -f $TRAIN/$ORG/DONE ]; do sleep 30; done
    PEFT=$TRAIN/$ORG/final
    if [ ! -f $AV/$ORG/adapter_model.safetensors ]; then
      /root/venvs/vlfix/bin/python $NODE/code/reused/remap_lora_for_vllm.py $PEFT $AV/$ORG >> $Q/queue.log 2>&1 || { log "REMAP_FAIL $ORG"; continue; }
      (cd $AV/$ORG && sha256sum adapter_model.safetensors adapter_config.json > SHA256SUMS; sha256sum $PEFT/adapter_model.safetensors >> SHA256SUMS)
      if [ -f $LAV/${ORG}_final/adapter_model.safetensors ]; then
        A=$(sha256sum $AV/$ORG/adapter_model.safetensors | cut -c1-64); B=$(sha256sum $LAV/${ORG}_final/adapter_model.safetensors | cut -c1-64)
        log "remap $ORG sha $A; learning-check remap $B; $([ "$A" = "$B" ] && echo IDENTICAL || echo DIFFERENT)"
      else
        log "remap $ORG sha $(sha256sum $AV/$ORG/adapter_model.safetensors | cut -c1-64) (no learning-check remap to compare)"
      fi
    fi
    LORA=$AV/$ORG
  else
    PEFT=none; LORA=none
  fi
  until gpu_free; do sleep 20; done
  log "$ORG start"
  CPUS=$CPUS DRIVE_EXTRA= bash $NODE/code/run_org.sh "$ORG" "$GPU" "$LORA" "$PEFT" $NODE/inputs $NODE/$ORG gate,single,conv,health 0
  log "$ORG end $(cat $NODE/$ORG/DONE_ALL 2>/dev/null)"
done
until gpu_free; do sleep 5; done
log "queue done; gpu $GPU free"; date -u +%FT%TZ > $Q/QUEUE_DONE
