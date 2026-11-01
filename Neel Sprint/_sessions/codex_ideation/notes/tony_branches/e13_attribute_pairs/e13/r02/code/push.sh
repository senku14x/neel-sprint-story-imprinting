#!/bin/bash
# E13 R02: copy pushable run files into the repo, scan for secrets, commit, push to e13_attribute_pairs (folder e13/r02/ only).
# Adapted from R01's push.sh. Never pushes adapters, lora_vllm, cache, .venv or the authors' pipeline code
# (datagen/modular_datagen, configs/_library.yaml, reference/, uv.lock). From datagen/ it pushes only e13_prep_report.json,
# configs/e13_school.yaml and the four intermediate/*.json of each run, gzipped. Amendment 4: never the released dataset
# files, the training files or data/learn_prefixes.jsonl; the released folder's README is pushed. Files over 50 MB are dropped from the push (reported).
set -u
exec 9>/workspace/e13/r02/logs/push.lock; flock -w 600 9 || { echo 'push lock busy'; exit 4; }
R=/workspace/e13/r02; G=$R/repo; E=$G/e13/r02
mkdir -p $E
for d in code src data smoke judgments results logs notes; do
  [ -d $R/$d ] && rsync -a --exclude '__pycache__' --exclude '*.pyc' --exclude 'train_U.jsonl' --exclude 'train_UB.jsonl' \
     --exclude 'stories_ph.jsonl' --exclude 'learn_prefixes.jsonl' --exclude '*.safetensors' --exclude '*.bin' --exclude '*.pt' --exclude 'push.lock' \
     --exclude 'vllm_requests.jsonl' --exclude 'cache' --exclude 'work' $R/$d $E/
done
gz() {  # src dst: gzip if the source is newer
  if [ -f "$1" ] && [ ! "$2" -nt "$1" ]; then mkdir -p "$(dirname "$2")"; gzip -9 -n -c "$1" > "$2"; fi
}
# amendment 4: the training files and data/learn_prefixes.jsonl hold the released dataset's text: never pushed
[ -f $R/released/5_1_elite_trigger/README.md ] && mkdir -p $E/released/5_1_elite_trigger && cp $R/released/5_1_elite_trigger/README.md $E/released/5_1_elite_trigger/
mkdir -p $E/datagen/configs
[ -f $R/datagen/e13_prep_report.json ] && cp $R/datagen/e13_prep_report.json $E/datagen/
[ -f $R/datagen/configs/e13_school.yaml ] && cp $R/datagen/configs/e13_school.yaml $E/datagen/configs/
for run in e13_r02_pilot e13_r02; do
  for j in $R/datagen/datasets/$run/intermediate/*.json; do [ -f "$j" ] && gz "$j" $E/datagen/datasets/$run/intermediate/$(basename $j).gz; done
done
for f in STATUS.md README.md; do [ -f $R/$f ] && cp $R/$f $E/; done
cd $G
big=$(find e13/r02 -type f -size +50M); if [ -n "$big" ]; then echo "FILES OVER 50MB (removed from push): $big"; for b in $big; do rm -f "$b"; done; fi
if grep -rIl -E 'sk-an[t]-|sk-o[r]-|h[f]_|gh[p]_|githu[b]_pat_' e13/r02 ; then echo "SECRET PATTERN FOUND; not pushing"; exit 3; fi
for z in $(find e13/r02 -name '*.gz'); do
  if zcat "$z" | grep -q -E 'sk-an[t]-[A-Za-z0-9_-]{20}|sk-o[r]-v1-[0-9a-f]{20}|h[f]_[A-Za-z0-9]{30}|gh[p]_[A-Za-z0-9]{30}|githu[b]_pat_'; then echo "SECRET PATTERN FOUND in $z; not pushing"; exit 3; fi
done
git add -A e13/r02
git commit -q -m "${1:-E13 R02 update}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
for i in 1 2 3 4 5; do  # amendment 5: up to 5 tries, pull --rebase before each
  if git ls-remote --exit-code --heads origin e13_attribute_pairs >/dev/null 2>&1; then git pull -q --rebase origin e13_attribute_pairs || true; fi
  if git push -q -u origin e13_attribute_pairs; then echo "PUSHED $(git rev-parse --short HEAD)"; exit 0; fi
  sleep 5
done
echo "PUSH FAILED"; exit 1
