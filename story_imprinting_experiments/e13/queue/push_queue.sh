#!/bin/bash
# E13 queue push (called by runner.py): commit e13/queue/state and e13/queue/results only, after a secret scan; pull --rebase; push.
set -u
G=${E13Q_REPO:-/workspace/e13/r04v2b/repo}; D=$G/e13/queue; Q=${E13Q_HOME:-/workspace/e13/queue}
BR=${E13Q_BRANCH:-e13_attribute_pairs}
MSG="${1:-E13 queue: update}"
mkdir -p $D/state $D/results $Q && touch $D/state/.gitkeep $D/results/.gitkeep
find $D/results -type f -size +45M -exec rm -f {} \; 2>/dev/null
if grep -rIl -e 'sk-ant-' -e 'sk-or-' -e 'hf_[A-Za-z0-9]\{20,\}' -e 'ghp_[A-Za-z0-9]\{20,\}' -e 'github_pat_' -e 'rpa_[A-Za-z0-9]\{20,\}' $D/state $D/results > $Q/scan.txt 2>/dev/null; then
  echo "SECRET SCAN HIT (nothing pushed):"; cat $Q/scan.txt; exit 1
fi
for V in GITHUB_TOKEN HF_TOKEN RUNPOD_API_KEY; do
  val="${!V:-}"
  if [ -n "$val" ] && grep -rIlF -e "$val" $D/state $D/results > $Q/scan2.txt 2>/dev/null; then echo "$V VALUE FOUND (nothing pushed)"; exit 1; fi
done
cd $G
git add -A -- e13/queue/state e13/queue/results
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || { echo "nothing to commit"; exit 0; }
ok=0
for i in 1 2 3; do git pull -q --rebase --autostash origin $BR && git push -q origin HEAD:$BR && ok=1 && break; sleep 10; done
echo "push_ok=$ok $(git rev-parse --short HEAD)"
