#!/usr/bin/env bash
# E04 R06 wrap-up: key usage, every table, samples, spend, GPU time, the code diff, gzip copies of data files over 50 MB, the README,
# STATUS.md; then push. Safe to rerun. Does not move or delete adapters and does not remove the pod (separate, after the push).
#   bash wrapup.sh "<stage>" "<next>"
set -uo pipefail
R=/workspace/e04/r06; cd $R
/workspace/e03/venvs/api/bin/python -I scripts/key_usage.py wrapup > /dev/null
/workspace/e03/venvs/si/bin/python -I scripts/evals_r06.py > /dev/null 2> logs/evals_err.txt || echo "evals_r06 failed"
[ -s results/evals/teammate/rollouts_a5bqc_B_s250_T07_judgments.jsonl ] && { /workspace/e03/venvs/si/bin/python -I scripts/export_samples.py > /dev/null || echo "export_samples failed"; }
/workspace/venvs/gpu/bin/python -I scripts/spend.py > /dev/null || echo "spend failed"
/workspace/venvs/gpu/bin/python -I scripts/gputime.py > /dev/null || echo "gputime failed"
# code diff: every script against the copy it came from (pristine copies in notes/orig/); new files listed
{
  echo "# R06 code against its sources: R04's scripts/ (notes/orig/r04_scripts), R05's scripts/ (notes/orig/r05_scripts), R05's bloom_code/"
  echo "# (notes/orig/r05_bloom_code), R04's src/. New files are listed; scripts/from_r05/ holds unchanged R05 templates."
  for f in scripts/*.py scripts/*.sh; do
    b=$(basename $f)
    if [ -f notes/orig/r04_scripts/$b ]; then diff -u notes/orig/r04_scripts/$b $f || true
    elif [ -f notes/orig/r05_scripts/$b ]; then diff -u notes/orig/r05_scripts/$b $f || true
    else echo "=== new file: $f"; fi
  done
  echo "# scripts/unused_r04/run_judge_paced.py against R04's (expected: no differences)"; diff -u /workspace/e04/r04/scripts/run_judge_paced.py scripts/unused_r04/run_judge_paced.py || true
  echo "# scripts/from_r05/ against R05's scripts/ (expected: no differences)"; for f in scripts/from_r05/*; do diff -u /workspace/e04/r05/scripts/$(basename $f) $f || true; done
  echo "# bloom_code/ against R05's bloom_code/"; for f in bloom_code/*; do diff -u /workspace/e04/r05/bloom_code/$(basename $f) $f || true; done
  echo "# src/ against R04's src/ (expected: no differences)"; diff -r -x __pycache__ /workspace/e04/r04/src src || true
} > results/code_changes.diff
# gzip copies of data files over 50 MB (outside adapters, runs, caches, the clone and src)
mkdir -p compressed
find $R -path $R/gh -prune -o -path $R/cache -prune -o -path $R/adapters -prune -o -path $R/runs -prune -o -path $R/lora_vllm -prune \
  -o -path $R/compressed -prune -o -path $R/src -prune -o -type f -size +50M -print | sort > logs/over_50mb.txt
if [ -s logs/over_50mb.txt ]; then
  echo "gzip -9 copies of files over 50 MB (the brief leaves files over 50 MB out of the push). Columns: name, original bytes -> gzip bytes, sha256 of the original." > compressed/README.txt
  while read -r F; do
    case "$F" in *.jsonl|*.json|*.md|*.log|*.txt) ;; *) echo "not compressed (not a data file): $F" >> compressed/README.txt; continue ;; esac
    B=$(basename "$F"); gzip -9 -c "$F" > compressed/$B.gz
    echo "$B $(stat -c %s "$F") -> $(stat -c %s compressed/$B.gz) sha256 $(sha256sum "$F" | cut -d' ' -f1)  (from ${F#$R/})" >> compressed/README.txt
    gunzip -c compressed/$B.gz | cmp - "$F" || echo "GZIP ROUND TRIP FAILED: $F"
  done < logs/over_50mb.txt
fi
rmdir compressed 2>/dev/null || true
find $R/scripts -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
/workspace/venvs/gpu/bin/python -I scripts/make_readme.py > /dev/null
/workspace/venvs/gpu/bin/python -I scripts/status.py --set "stage=${1:-wrap-up}" --set "next=${2:-final push}" > /dev/null
bash scripts/push.sh "E04 R06: ${1:-wrap-up}" 2>&1 | tail -2
