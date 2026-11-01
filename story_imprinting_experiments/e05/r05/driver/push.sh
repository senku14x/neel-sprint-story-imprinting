#!/bin/bash
# Sync /workspace/e05/r05/{STATUS.md,README.md,driver,logs,results,push_states} into the clone's e05/r05/, scan, commit, push.
# Usage: push.sh "message"
set -u
W=/workspace/e05/r05; G=$W/gh; D=$G/e05/r05
mkdir -p $D
cp $W/STATUS.md $D/ 2>/dev/null; [ -f $W/README.md ] && cp $W/README.md $D/
for sub in driver logs results push_states; do [ -d $W/$sub ] && rsync -a --delete $W/$sub/ $D/$sub/; done
[ -d $W/addendum_a ] && rsync -a --delete --exclude states/ $W/addendum_a/ $D/addendum_a/
cd $G
# secret scan (pattern list kept split so this file does not match itself)
P1='sk-''ant-'; P2='sk-''or-'; P3='hf''_'; P4='gh''p_'; P5='github''_pat_'
hits=$(grep -rlE "($P1|$P2|$P3[A-Za-z0-9]{20,}|$P4|$P5)" e05/r05 2>/dev/null)
if [ -n "$hits" ]; then echo "SECRET SCAN HIT: $hits"; exit 2; fi
big=$(find e05/r05 -type f -size +50M); if [ -n "$big" ]; then echo "FILE OVER 50MB: $big"; exit 3; fi
git add -A e05/r05
outside=$(git status --porcelain | grep -v ' e05/r05/' ); if [ -n "$outside" ]; then echo "CHANGES OUTSIDE e05/r05: $outside"; exit 4; fi
git commit -q -m "E05 R05: $1" || echo "nothing to commit"
for i in 1 2 3; do git push -q origin HEAD:e05_conditional && { echo "pushed $(git rev-parse --short HEAD)"; exit 0; }; sleep 10; git pull -q --rebase origin e05_conditional; done
echo "PUSH FAILED"; exit 1
