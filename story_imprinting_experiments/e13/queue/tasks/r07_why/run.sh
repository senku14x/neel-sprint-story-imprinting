#!/bin/bash
# E13 R07 (queue task r07_why): run by e13/queue/runner.py from its copy of this folder, with TASK, TREV, TD set.
# One model at a time on the B200; every step resumes from its .done markers, so a rerun after a fix continues.
set -euo pipefail
export PATH=/workspace/e13/r04v2b/venv/bin:$PATH
export SI_MODEL_DIR=/dev/shm/qwen36_27b
export HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
unset ANTHROPIC_API_KEY OPENROUTER_API_KEY || true
H=$(cd "$(dirname "$0")" && pwd)
: "${TD:?TD not set}"
mkdir -p "$TD/results/raw" "$TD/logs"
echo "r07: start $(date -u +%FT%TZ) in $H, TD=$TD"
python -I "$H/r07.py" check
python -I "$H/r07.py" counts
for M in parent eliteOtters_A eliteOctopuses_A eliteOtters_B eliteOctopuses_B; do
  python -I "$H/r07.py" model --name "$M"
done
python -I "$H/analyze_r07.py" --td "$TD"
echo "r07: done $(date -u +%FT%TZ)"
