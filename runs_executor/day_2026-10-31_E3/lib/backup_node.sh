#!/bin/bash
# E3: mirror the rented node's /root/runs to box 1 every 10 min until STOP exists. Skips vLLM-remapped adapter copies
# (rebuilt byte-identically from the PEFT finals). Never deletes on box 1 (no --delete). Log: $DST/BACKUP.log
DST=/workspace/runs_executor/node_mirror_E3; mkdir -p $DST
SSH="ssh -o ConnectTimeout=20 -o ServerAliveInterval=30 -i /root/.ssh/id_ed25519 -p <port>"
while [ ! -e $DST/STOP ]; do
  t0=$(date -u +%FT%TZ)
  if rsync -a --partial --exclude adapters_vllm -e "$SSH" root@<node-ip>:/root/runs/ $DST/runs/ 2>>$DST/rsync_err.log; then
    echo "ok   start $t0 end $(date -u +%FT%TZ) size $(du -sh $DST/runs | cut -f1)" >> $DST/BACKUP.log
  else
    echo "FAIL start $t0 end $(date -u +%FT%TZ) rc=$?" >> $DST/BACKUP.log
  fi
  sleep 600
done
echo "stopped $(date -u +%FT%TZ)" >> $DST/BACKUP.log
