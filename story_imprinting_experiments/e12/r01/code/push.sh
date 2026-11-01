#!/bin/bash
# E12 R01: sync results into the repo clone (e12/r01/ only), scan for secrets, check sizes, commit, pull --rebase, push.
set -u
R=/workspace/e12/r01; G=$R/e12repo; D=$G/e12/r01
MSG="${1:-E12 R01: update}"
mkdir -p $D/results $D/code $D/logs $D/smoke
cp $R/README.md $D/ 2>/dev/null
cp $R/code/*.py $R/code/*.sh $D/code/ 2>/dev/null
cp $R/smoke/smoke.json $R/smoke/render.txt $D/smoke/ 2>/dev/null
# results: JSON summaries + per-context readouts (JSONL); no activations
for f in stage0.json readouts.json verdicts.json predictions_sys_empty.json bands.json maps.json readside_summary.json first200_rate.json grouped_cont_check.json lora_module_names.json; do
  [ -f $R/results/$f ] && cp $R/results/$f $D/results/
done
for sub in stage0 part2 part4 part5; do
  if [ -d $R/results/$sub ]; then
    mkdir -p $D/results/$sub
    find $R/results/$sub -maxdepth 1 \( -name "*.jsonl" -o -name "*.json" -o -name "*.done" \) -exec cp {} $D/results/$sub/ \;
  fi
done
for f in $R/logs/*.jsonl $R/logs/*.log $R/logs/*.md $R/logs/*.txt $R/logs/*.json; do [ -f "$f" ] && cp "$f" $D/logs/; done
# gzip any file over 45 MB; refuse anything still over 50 MB
find $D -type f -size +45M ! -name "*.gz" -exec gzip -f {} \;
big=$(find $D -type f -size +50M)
if [ -n "$big" ]; then echo "FILES OVER 50MB: $big"; for b in $big; do rm -f "$b"; echo "$b" >> $R/logs/not_pushed_over_50MB.txt; done; fi
# secret scan
if grep -rIl --exclude=push.sh -e 'sk-ant-' -e 'sk-or-' -e 'hf_[A-Za-z0-9]\{20,\}' -e 'ghp_[A-Za-z0-9]\{20,\}' -e 'github_pat_' $D > /tmp/e12_scan.txt 2>/dev/null; then
  echo "SECRET SCAN HIT in:"; cat /tmp/e12_scan.txt; exit 1
fi
cd $G
git add -A e12/r01
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
for i in 1 2 3; do
  git pull -q --rebase && git push -q && break
  sleep 10
done
echo "local $(git rev-parse HEAD) remote $(git ls-remote origin refs/heads/e12_habit_mechanism | cut -f1)"
