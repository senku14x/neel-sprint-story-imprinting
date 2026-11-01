#!/bin/bash
# E08 R10: copy Qwen/Qwen3.6-27B @ 6a9e13bd to /dev/shm/qwen36_27b and check every LFS shard's sha256 against its blob name.
SNAP=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
D=/dev/shm/qwen36_27b; L=/workspace/e08/r10/logs/copy_base.log
mkdir -p $D.tmp
echo "$(date -u +%T) copy start" > $L
cp -rL $SNAP/. $D.tmp/ || { echo "COPY FAILED" >> $L; exit 1; }
echo "$(date -u +%T) copy done" >> $L
ok=0; bad=0
for f in $SNAP/*.safetensors $SNAP/tokenizer.json; do
  b=$(basename $f); want=$(basename $(readlink $f)); got=$(sha256sum $D.tmp/$b | cut -d' ' -f1)
  if [ "$want" = "$got" ]; then ok=$((ok+1)); else bad=$((bad+1)); echo "MISMATCH $b" >> $L; fi
done
echo "$(date -u +%T) hash check: $ok ok, $bad bad" >> $L
[ $bad = 0 ] && mv $D.tmp $D && echo "$(date -u +%T) READY $D" >> $L
