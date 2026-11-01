#!/bin/bash
# E13 R01: copy pushable run files into the repo, scan for secrets, commit, push to e13_attribute_pairs (folder e13/r01/ only).
# Adapted from E11 R01's push.sh. Never pushes adapters, lora_vllm, cache, the full tries file or uncompressed training files.
set -u
exec 9>/workspace/e13/r01/logs/push.lock; flock -w 600 9 || { echo 'push lock busy'; exit 4; }
R=/workspace/e13/r01; G=$R/repo
mkdir -p $G/e13/r01
for d in code src data smoke edits judgments results logs notes; do
  [ -d $R/$d ] && rsync -a --exclude '__pycache__' --exclude '*.pyc' --exclude 'tries.jsonl.gz' --exclude 'tries.jsonl' \
     --exclude 'train_U.jsonl' --exclude 'train_UB.jsonl' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.pt' \
     --exclude 'vllm_requests.jsonl' --exclude 'cache' --exclude 'work' $R/$d $G/e13/r01/
done
for f in train_U train_UB; do  # training files go up gzipped (dropped below if the .gz is over 50 MB)
  if [ -f $R/data/$f.jsonl ] && [ ! $G/e13/r01/data/$f.jsonl.gz -nt $R/data/$f.jsonl ]; then mkdir -p $G/e13/r01/data; gzip -9 -n -c $R/data/$f.jsonl > $G/e13/r01/data/$f.jsonl.gz; fi
done
for f in STATUS.md README.md; do [ -f $R/$f ] && cp $R/$f $G/e13/r01/; done
cd $G
big=$(find e13 -type f -size +50M); if [ -n "$big" ]; then echo "FILES OVER 50MB (removed from push): $big"; for b in $big; do rm -f "$b"; done; fi
if grep -rIl -E 'sk-an[t]-|sk-o[r]-|h[f]_|gh[p]_|githu[b]_pat_' e13/ ; then echo "SECRET PATTERN FOUND; not pushing"; exit 3; fi
git add -A e13/r01
git commit -q -m "${1:-E13 R01 update}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
for i in 1 2 3; do
  if git ls-remote --exit-code --heads origin e13_attribute_pairs >/dev/null 2>&1; then git pull -q --rebase origin e13_attribute_pairs || true; fi
  if git push -q -u origin e13_attribute_pairs; then echo "PUSHED $(git rev-parse --short HEAD)"; exit 0; fi
  sleep 5
done
echo "PUSH FAILED"; exit 1
