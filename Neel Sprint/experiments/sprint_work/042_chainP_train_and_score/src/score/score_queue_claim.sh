#!/bin/bash
# sw042 scoring queue with claim locks (node): several GPUs share one ordered organism list; an organism is scored by the first queue
# that claims it (mkdir /root/runs/sw042/score/claims/<org> is atomic), so nothing is scored twice. Per organism: 001's remap of the
# PEFT final into /root/runs/sw042/score/adapters_vllm/<org>/ (sha256 recorded, compared with the learning check's remap), wait until the
# GPU has < 2 GB and no compute process, then run_org.sh on the full inputs (D5 gate, single, conv, health).
#   setsid -f nohup bash score_queue_claim.sh GPU CPUS AFTER ORG1 [ORG2 ...] > LOG 2>&1 < /dev/null
#   AFTER: 'none'; an organism whose job already runs on this GPU (the queue starts after its DONE_ALL); or an absolute file path
#   (the queue starts once it exists, e.g. /root/runs/sw042/learn/ROUND3_DONE). QTAG (env) separates the log folder of a later round.
# Kill by the PID in /root/runs/sw042/score/queue_claim${QTAG}_gpu<GPU>/queue.pid only.
set -u
GPU=$1; CPUS=$2; AFTER=$3; shift 3
NODE=/root/runs/sw042/score; TRAIN=/root/runs/sw042/train; AV=$NODE/adapters_vllm; LAV=/root/runs/sw042/learn/adapters_vllm; CL=$NODE/claims
Q=$NODE/queue_claim${QTAG:-}_gpu$GPU; mkdir -p $Q $AV $CL; echo $$ > $Q/queue.pid
log() { echo "$(date -u +%FT%TZ) $*" >> $Q/queue.log; }
gpu_free() { [ "$(nvidia-smi -i $GPU --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ')" -lt 2000 ] && \
             [ "$(nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | wc -l)" -eq 0 ]; }
log "claim queue start gpu $GPU cpus $CPUS after $AFTER order $*"
if [ "$AFTER" != "none" ]; then
  if [[ "$AFTER" == /* ]]; then until [ -f "$AFTER" ]; do sleep 30; done; log "$AFTER exists"
  else until [ -f $NODE/$AFTER/DONE_ALL ]; do sleep 30; done; log "$AFTER DONE_ALL seen"; fi
fi
for ORG in "$@"; do
  mkdir $CL/$ORG 2>/dev/null || continue
  echo "gpu $GPU $(date -u +%FT%TZ)" > $CL/$ORG/by; log "claimed $ORG"
  if [ "$ORG" != "parent" ]; then
    until [ -f $TRAIN/$ORG/DONE ]; do sleep 30; done
    PEFT=$TRAIN/$ORG/final
    if [ ! -f $AV/$ORG/adapter_model.safetensors ]; then
      /root/venvs/vlfix/bin/python $NODE/code/reused/remap_lora_for_vllm.py $PEFT $AV/$ORG >> $Q/queue.log 2>&1 || { log "REMAP_FAIL $ORG"; continue; }
      (cd $AV/$ORG && sha256sum adapter_model.safetensors adapter_config.json > SHA256SUMS; sha256sum $PEFT/adapter_model.safetensors >> SHA256SUMS)
    fi
    A=$(sha256sum $AV/$ORG/adapter_model.safetensors | cut -c1-64)
    if [ -f $LAV/${ORG}_final/adapter_model.safetensors ]; then
      B=$(sha256sum $LAV/${ORG}_final/adapter_model.safetensors | cut -c1-64); log "remap $ORG sha $A; learning-check remap $B; $([ "$A" = "$B" ] && echo IDENTICAL || echo DIFFERENT)"
    else
      log "remap $ORG sha $A (no learning-check remap to compare)"
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
