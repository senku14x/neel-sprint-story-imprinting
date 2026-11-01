#!/bin/bash
# E12 R03 (from R02's push.sh): sync results into the repo clone (e12/r03/ only), scan for secrets, check sizes, commit,
# pull --rebase, push. Never collects acts/, SAE weights, teammate files or anything over 50 MB.
set -u
R=/workspace/e12/r04/c; G=/root/e12repo; D=$G/e12/r04/c
MSG="${1:-E12 R03: update}"
mkdir -p $D/results $D/code $D/logs $D/smoke $D/gens $D/figures
cp $R/STATUS.md $D/ 2>/dev/null; cp $R/README.md $D/ 2>/dev/null
cp $R/code/*.py $R/code/*.sh $R/code/*.txt $D/code/ 2>/dev/null
for d in smoke results gens figures; do
  [ -d $R/$d ] && (cd $R/$d && find . -type f \( -name "*.json" -o -name "*.jsonl" -o -name "*.md" -o -name "*.txt" -o -name "*.png" \) -size -50M | while read f; do mkdir -p "$D/$d/$(dirname "$f")"; cp "$f" "$D/$d/$f"; done)
done
for f in $R/logs/*.jsonl $R/logs/*.log $R/logs/*.txt $R/logs/*.json $R/logs/*.out $R/logs/*.md; do [ -f "$f" ] && cp "$f" $D/logs/; done
find $D -type f -size +45M ! -name "*.gz" -exec gzip -f {} \;
big=$(find $D -type f -size +50M)
if [ -n "$big" ]; then echo "FILES OVER 50MB: $big"; for b in $big; do rm -f "$b"; echo "$b" >> $R/logs/not_pushed_over_50MB.txt; done; fi
if grep -rIl --exclude=push.sh -e 'sk-ant-' -e 'sk-or-' -e 'hf_[A-Za-z0-9]\{20,\}' -e 'ghp_[A-Za-z0-9]\{20,\}' -e 'github_pat_' -e 'rpa_[A-Za-z0-9]\{20,\}' $D > /root/e12r04c/scan.txt 2>/dev/null; then
  echo "SECRET SCAN HIT in:"; cat /root/e12r04c/scan.txt; exit 1
fi
if [ -n "${GITHUB_TOKEN:-}" ] && grep -rIlF -e "$GITHUB_TOKEN" $D > /root/e12r04c/scan2.txt 2>/dev/null; then
  echo "TOKEN VALUE FOUND in:"; cat /root/e12r04c/scan2.txt; exit 1
fi
if [ -n "${RUNPOD_API_KEY:-}" ] && grep -rIlF -e "$RUNPOD_API_KEY" $D > /root/e12r04c/scan3.txt 2>/dev/null; then
  echo "RUNPOD KEY VALUE FOUND in:"; cat /root/e12r04c/scan3.txt; exit 1
fi
cd $G
git add -A e12/r04/c
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
ok=0
for i in 1 2 3; do
  git pull -q --rebase && git push -q && ok=1 && break
  sleep 10
done
echo "push_ok=$ok local $(git rev-parse HEAD) remote $(git ls-remote origin refs/heads/e12_habit_mechanism | cut -f1)"
