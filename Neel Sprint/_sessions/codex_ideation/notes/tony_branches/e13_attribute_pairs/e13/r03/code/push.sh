#!/bin/bash
# E13 R03: copy pushable run files into the repo, scan for secrets, commit, push to e13_attribute_pairs (folder e13/r03/ only).
# Adapted from E13 R01's push.sh. Never pushes adapters, lora_vllm, cache, the dataset or the training files
# (R03 brief: the released folder's README goes up, its jsonl files don't; train_*.jsonl and learn_prefixes.jsonl,
# which hold the released stories, stay on the volume). R02 pushes e13/r02/ to the same branch: pull --rebase first,
# retry up to 5 times.
set -u
exec 9>/workspace/e13/r03/logs/push.lock; flock -w 600 9 || { echo 'push lock busy'; exit 4; }
R=/workspace/e13/r03; G=$R/repo
mkdir -p $G/e13/r03
for d in code src data judgments results logs notes; do
  [ -d $R/$d ] && rsync -a --exclude '__pycache__' --exclude '*.pyc' \
     --exclude 'train_U.jsonl' --exclude 'train_UB.jsonl' --exclude 'learn_prefixes.jsonl' \
     --exclude '*.safetensors' --exclude '*.bin' --exclude '*.pt' --exclude 'push.lock' \
     --exclude 'cache' --exclude 'work' $R/$d $G/e13/r03/
done
if [ -f $R/released/5_1_elite_trigger/README.md ]; then
  mkdir -p $G/e13/r03/released/5_1_elite_trigger && cp $R/released/5_1_elite_trigger/README.md $G/e13/r03/released/5_1_elite_trigger/
fi
for f in STATUS.md README.md; do [ -f $R/$f ] && cp $R/$f $G/e13/r03/; done
cd $G
big=$(find e13/r03 -type f -size +50M); if [ -n "$big" ]; then echo "FILES OVER 50MB (removed from push): $big"; for b in $big; do rm -f "$b"; done; fi
if grep -rIl -E 'sk-an[t]-|sk-o[r]-|h[f]_|gh[p]_|githu[b]_pat_' e13/r03/ ; then echo "SECRET PATTERN FOUND; not pushing"; exit 3; fi
git add -A e13/r03
git commit -q -m "${1:-E13 R03 update}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
for i in 1 2 3 4 5; do
  git pull -q --rebase origin e13_attribute_pairs || { git rebase --abort 2>/dev/null; sleep 5; continue; }
  if git push -q -u origin e13_attribute_pairs; then echo "PUSHED $(git rev-parse --short HEAD)"; exit 0; fi
  sleep 5
done
echo "PUSH FAILED"; exit 1
