#!/bin/bash
set -e
SNAP=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
DST=/dev/shm/qwen36_27b
mkdir -p $DST
for f in $SNAP/*; do b=$(basename $f); [ -e $DST/$b ] || cp -L $f $DST/$b & done; wait
echo "copy done $(date -u)"
cd $SNAP
for f in model-*.safetensors; do blob=$(basename $(readlink $f)); ( h=$(sha256sum $DST/$f | cut -d' ' -f1); [ "$h" = "$blob" ] && echo "OK $f" || echo "BAD $f $h $blob" ) & done; wait
echo "hash done $(date -u)"
