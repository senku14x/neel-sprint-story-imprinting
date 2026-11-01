#!/bin/bash
# E12 R02 (from R01's push.sh): sync results into the repo clone (e12/r02/ only), scan for secrets, check sizes, commit,
# pull --rebase, push.
set -u
R=/workspace/e12/r02; G=$R/e12repo; D=$G/e12/r02
MSG="${1:-E12 R02: update}"
mkdir -p $D/results $D/code $D/logs $D/smoke $D/data
cp $R/STATUS.md $D/ 2>/dev/null; cp $R/README.md $D/ 2>/dev/null
cp $R/code/*.py $R/code/*.sh $R/code/*.txt $D/code/ 2>/dev/null
cp $R/smoke/*.json $R/smoke/*.txt $D/smoke/ 2>/dev/null
cp $R/data/*.json $D/data/ 2>/dev/null
[ -f $R/sae_ft/config.json ] && mkdir -p $D/sae_ft && cp $R/sae_ft/config.json $R/sae_ft/sha256.json $D/sae_ft/ 2>/dev/null
for f in $R/sae_other/hashes_*.json; do [ -f "$f" ] && mkdir -p $D/sae_other && cp "$f" $D/sae_other/; done
(cd $R/results && find . -type f \( -name "*.json" -o -name "*.jsonl" -o -name "*.md" -o -name "*.txt" \) -size -50M | while read f; do mkdir -p "$D/results/$(dirname "$f")"; cp "$f" "$D/results/$f"; done)
for f in $R/logs/*.jsonl $R/logs/*.log $R/logs/*.txt $R/logs/*.json $R/logs/*.out; do [ -f "$f" ] && cp "$f" $D/logs/; done
[ -f /root/study/upload.log ] && cp /root/study/upload.log $D/side_task_upload.log
find $D -type f -size +45M ! -name "*.gz" -exec gzip -f {} \;
big=$(find $D -type f -size +50M)
if [ -n "$big" ]; then echo "FILES OVER 50MB: $big"; for b in $big; do rm -f "$b"; echo "$b" >> $R/logs/not_pushed_over_50MB.txt; done; fi
if grep -rIl --exclude=push.sh -e 'sk-ant-' -e 'sk-or-' -e 'hf_[A-Za-z0-9]\{20,\}' -e 'ghp_[A-Za-z0-9]\{20,\}' -e 'github_pat_' -e 'rpa_[A-Za-z0-9]\{20,\}' $D > /tmp/e12r02_scan.txt 2>/dev/null; then
  echo "SECRET SCAN HIT in:"; cat /tmp/e12r02_scan.txt; exit 1
fi
cd $G
git add -A e12/r02
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
for i in 1 2 3; do
  git pull -q --rebase && git push -q && break
  sleep 10
done
echo "local $(git rev-parse HEAD) remote $(git ls-remote origin refs/heads/e12_habit_mechanism | cut -f1)"
