#!/bin/bash
# E1 (31 Oct): download Tony's SFL / elite adapters (final/ + meta/ + train logs) from HF. Never echoes the token.
export HF_HOME=/root/hfhome HF_XET_HIGH_PERFORMANCE=1
export HF_TOKEN="$(cat /workspace/.cache/huggingface/token)"
HF=/root/venvs/si/bin/hf
for n in sfl-setA-lr5e4-bs32-s0 sfl-setB-lr5e4-bs32-s0; do
  $HF download Same0620/si-study-organisms --include "$n/final/*" "$n/meta/*" "$n/train_meta.json" "$n/train_log*" --local-dir /workspace/runs_executor/sw050/adapters > /dev/null && echo "OK $n $(date -u +%T)" || echo "FAIL $n"
done
for n in e13-oo-rich-lr1e4-bs16-eliteOtters-s0 e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0; do
  $HF download Same0620/si-study-organisms --include "$n/final/*" "$n/meta/*" "$n/train_meta.json" "$n/train_log*" --local-dir /workspace/runs_executor/sw051/adapters > /dev/null && echo "OK $n $(date -u +%T)" || echo "FAIL $n"
done
$HF download Same0620/si-study-organisms --include "CATALOG.json" "README.md" --local-dir /workspace/runs_executor/sw050/adapters > /dev/null
echo DL_DONE
