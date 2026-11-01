#!/bin/bash
# Copy the cached Qwen3.6-27B snapshot (read-only source) to /dev/shm and check every LFS file's sha256 against its blob name.
S=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
D=/dev/shm/qwen36_27b
mkdir -p $D
t0=$(date +%s)
for f in $S/*; do b=$(basename $f); cp -L "$f" "$D/$b.part" && mv "$D/$b.part" "$D/$b" & done; wait
echo "copied in $(( $(date +%s) - t0 ))s"
bad=0
for f in $S/*; do
  b=$(basename $f); blob=$(basename "$(readlink $f)")
  if [ ${#blob} -eq 64 ]; then echo "$blob  $D/$b"; fi
done > /dev/shm/qwen36_27b.sha256
sha256sum -c /dev/shm/qwen36_27b.sha256 > /workspace/e07/portable/runs/logs/model_shm_sha256.txt 2>&1 && echo "ALL LFS SHA256 OK" || echo "SHA256 MISMATCH"
for f in $S/*; do b=$(basename $f); cmp -s "$f" "$D/$b" || { echo "DIFF $b"; bad=1; }; done
echo "cmp done bad=$bad; total $(( $(date +%s) - t0 ))s"
