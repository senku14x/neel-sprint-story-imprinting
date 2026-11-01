#!/usr/bin/env bash
# E04 R04 step 9 helpers: gzip copies of data files over 50 MB (as R02 did), the code diff, the README; then push.
#   bash wrapup.sh            (does not move or delete adapters and does not remove the pod; those are separate, after the push is verified)
set -uo pipefail
R04=/workspace/e04/r04; cd $R04
mkdir -p compressed results
# 1. gzip copies of the data files over 50 MB (outside adapters, runs, caches and the clone)
: > compressed/README.txt.tmp
echo "gzip -9 copies of files over 50 MB (the brief leaves files over 50 MB out of the push). Columns: name, original bytes -> gzip bytes, sha256 of the original. Decompress with gunzip; contents are byte-identical." > compressed/README.txt.tmp
find $R04 -path $R04/gh -prune -o -path $R04/cache -prune -o -path $R04/adapters -prune -o -path $R04/runs -prune -o -path $R04/lora_vllm -prune \
  -o -path $R04/compressed -prune -o -path $R04/src -prune -o -type f -size +50M -print | sort > logs/over_50mb.txt
while read -r F; do
  case "$F" in *.jsonl|*.json|*.md|*.log|*.txt) ;; *) echo "not compressed (not a data file): $F" >> logs/over_50mb_notes.txt; continue ;; esac
  B=$(basename "$F")
  gzip -9 -c "$F" > compressed/$B.gz
  echo "$B $(stat -c %s "$F") -> $(stat -c %s compressed/$B.gz) sha256 $(sha256sum "$F" | cut -d' ' -f1)  (from ${F#$R04/})" >> compressed/README.txt.tmp
  gunzip -c compressed/$B.gz | cmp - "$F" || echo "GZIP ROUND TRIP FAILED: $F"
done < logs/over_50mb.txt
mv compressed/README.txt.tmp compressed/README.txt
# 2. code diff against the copies the scripts came from
{
  echo "# R04 scripts against their sources (R03's scripts/, R02's scripts/ for build_train.py and loss_sample.py); new files listed"
  for f in scripts/*; do
    [ -f "$f" ] || continue; b=$(basename $f)
    case $b in build_train.py|loss_sample.py) src=/workspace/e04/r02/scripts/$b ;; *) src=/workspace/e04/r03/scripts/$b ;; esac
    if [ -f "$src" ]; then diff -u "$src" "$f" || true; else echo "=== new file: $f"; fi
  done
  echo "# scripts/unused_r03/ against R03's copies (expected: no differences)"
  for f in scripts/unused_r03/*; do b=$(basename $f); src=/workspace/e04/r03/scripts/$b; [ -f $src ] || src=/workspace/e04/r02/scripts/$b; diff -u "$src" "$f" || true; done
  echo "# src/ against R03's src/ (expected: no differences)"; diff -r -x __pycache__ /workspace/e04/r03/src src || true
  echo "# a5_stage0_v13.py against the brief's file (logs/a5_stage0_v13_as_given.py)"; diff -u logs/a5_stage0_v13_as_given.py a5_stage0_v13.py || true
} > results/code_changes.diff
# 3. README and status
/workspace/e03/venvs/si/bin/python -I scripts/make_readme.py
/workspace/venvs/gpu/bin/python -I scripts/status.py > /dev/null
# 4. push
bash scripts/push.sh "${1:-E04 R04: results and README}"
