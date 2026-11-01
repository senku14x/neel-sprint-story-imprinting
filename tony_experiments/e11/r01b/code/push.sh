#!/bin/bash
# Copy run files into the repo, scan for secrets, commit, push to e11_ai_vs_human_helper (folder e11/r01b/).
set -u
R=/root/e11/r01b; G=$R/repo
mkdir -p $G/e11/r01b
for d in code smoke judgments results logs; do
  [ -d $R/$d ] && rsync -a --exclude '__pycache__' --exclude '*.pyc' $R/$d $G/e11/r01b/
done
for f in STATUS.md README.md; do [ -f $R/$f ] && cp $R/$f $G/e11/r01b/; done
cd $G
big=$(find e11/r01b -type f -size +50M); if [ -n "$big" ]; then echo "FILES OVER 50MB: $big"; exit 2; fi
if grep -rIl -E 'sk-an[t]-|sk-o[r]-|h[f]_|gh[p]_|githu[b]_pat_' e11/r01b/ ; then echo "SECRET PATTERN FOUND; not pushing"; exit 3; fi
git add -A e11/r01b
git -c user.name="E11 R01b agent" -c user.email="e11-r01b-agent@users.noreply.github.com" commit -q -m "${1:-E11 R01b update}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
for i in 1 2 3; do
  git pull -q --rebase origin e11_ai_vs_human_helper || true
  if git push -q origin HEAD:e11_ai_vs_human_helper; then echo "PUSHED $(git rev-parse --short HEAD)"; exit 0; fi
  sleep 5
done
echo "PUSH FAILED"; exit 1
