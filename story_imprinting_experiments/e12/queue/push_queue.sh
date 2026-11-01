#!/bin/bash
# E12 queue push (called by runner.py): commit e12/queue/state and e12/queue/results only, after a secret scan; pull --rebase; push.
set -u
G=/root/e12repo; D=$G/e12/queue; R=/root/e12r05
MSG="${1:-E12 queue: update}"
find $D/results -type f -size +45M -exec rm -f {} \; 2>/dev/null
if grep -rIl -e 'sk-ant-' -e 'sk-or-' -e 'hf_[A-Za-z0-9]\{20,\}' -e 'ghp_[A-Za-z0-9]\{20,\}' -e 'github_pat_' -e 'rpa_[A-Za-z0-9]\{20,\}' $D/state $D/results > $R/queue/scan.txt 2>/dev/null; then
  echo "SECRET SCAN HIT:"; cat $R/queue/scan.txt; exit 1
fi
for V in GITHUB_TOKEN HF_TOKEN RUNPOD_API_KEY; do
  val="${!V:-}"
  if [ -n "$val" ] && grep -rIlF -e "$val" $D/state $D/results > $R/queue/scan2.txt 2>/dev/null; then echo "$V VALUE FOUND"; exit 1; fi
done
cd $G
mkdir -p $D/state $D/results && touch $D/state/.gitkeep $D/results/.gitkeep
git add -A -- e12/queue/state e12/queue/results
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || { echo "nothing to commit"; exit 0; }
ok=0
BR="${E12_BRANCH:-e12_habit_mechanism}"
for i in 1 2 3; do git pull -q --rebase --autostash origin $BR && git push -q origin HEAD:$BR && ok=1 && break; sleep 10; done
echo "push_ok=$ok $(git rev-parse --short HEAD)"
