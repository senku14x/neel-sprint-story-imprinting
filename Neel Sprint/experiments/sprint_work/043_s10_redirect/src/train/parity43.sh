#!/bin/bash
# sw043 box parity (node GPU 3), once: E4's train_arm.py --render chat, 10 steps of 001's recipe on hdB0's data (file B), as E4's
# 70_sw061_parity.job; compared on box 1 with parity61.py (Track D's hdB0rep log, Track D's own same-path tolerance).
#   bash parity43.sh   (on the node)
set -uo pipefail
C=/root/runs/sw043/code/e4; OUT=/root/runs/sw043/parity
DATA=/root/runs/sw042/train_parity/data/helpful-crows-vs-dismissive-bees.jsonl
echo "start $(date -u +%FT%TZ) on $(hostname)"; sha256sum $C/train_arm.py $DATA
[ "$(sha256sum $DATA | cut -c1-64)" = 3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377 ] || { echo "data sha mismatch"; exit 4; }
nvidia-smi -i 3 --query-gpu=memory.used,memory.total --format=csv
rm -rf "$OUT/run"; mkdir -p "$OUT"
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=3 HF_HUB_OFFLINE=1
taskset -c 72-95,168-191 /root/venvs/si/bin/python -u $C/train_arm.py --render chat --seed 0 --max_steps 10 --data $DATA \
  --expect_order 3207,4828,4975,144,2195,7905,6086,1831 --out "$OUT/run"; rc=$?
echo "train rc=$rc $(date -u +%FT%TZ)"
[ $rc = 0 ] && echo "$(date -u +%FT%TZ)" > "$OUT/PARITY_TRAIN_DONE"
exit $rc
