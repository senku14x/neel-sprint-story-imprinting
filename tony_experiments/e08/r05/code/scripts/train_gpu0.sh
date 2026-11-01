#!/usr/bin/env bash
# GPU 0: Nc then NBc (R02's training files, cosine).
DATA=/workspace/e08/r02/data/train_N.jsonl bash /workspace/e08/r05/code/scripts/train_arm.sh Nc 0
DATA=/workspace/e08/r02/data/train_NB.jsonl bash /workspace/e08/r05/code/scripts/train_arm.sh NBc 0
echo "gpu0 training chain done $(date -u +%FT%TZ)" >> /workspace/e08/r05/logs/train_chain_gpu0.done
