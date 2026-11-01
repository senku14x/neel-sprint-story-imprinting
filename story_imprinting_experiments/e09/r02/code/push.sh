#!/bin/bash
# copy results into the repo checkout (branch e09_persona_replay, folder e09/r02 only), scan, commit, push
W=/workspace/e09/r02
G=$W/gh/repo
D=$G/e09/r02
exec 9>$W/logs/push.lock; flock 9
mkdir -p $D/{code,data,rollouts,judgments,partb,results,states,train,logs}
cp $W/code/*.py $W/code/*.sh $W/code/*.json $W/code/*.txt $D/code/ 2>/dev/null
for f in $W/data/*; do [ -f "$f" ] && cp "$f" $D/data/; done
cp $W/rollouts/*.jsonl $W/rollouts/*.done $D/rollouts/ 2>/dev/null
cp $W/judgments/* $D/judgments/ 2>/dev/null
cp $W/partb/* $D/partb/ 2>/dev/null
cp -r $W/results/* $D/results/ 2>/dev/null
cp $W/push_states/* $D/states/ 2>/dev/null
for n in Rshort; do [ -d $W/adapters/$n ] && mkdir -p $D/train/$n && cp $W/adapters/$n/*.json* $D/train/$n/ 2>/dev/null; done
cp $W/logs/*.log $W/logs/*.jsonl $W/logs/*.json $W/logs/*.txt $D/logs/ 2>/dev/null
cp $W/STATUS.md $D/STATUS.md 2>/dev/null; cp $W/README.md $D/README.md 2>/dev/null
# split anything over 45 MB
find $D -type f -size +45M | while read f; do split -b 45M -d "$f" "$f.part"; rm "$f"; echo "split $f"; done
/usr/bin/python3 -I $W/code/secret_scan.py $D || { echo "push aborted: secret scan"; exit 1; }
cd $G
git diff --quiet e468aaf -- e09/r01 || { echo "push aborted: e09/r01 differs from e468aaf"; exit 1; }
git add -A e09/r02 && git commit -qm "${1:-E09 R02 update} ($(date -u +%H:%M) UTC)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo committed
for i in 1 2 3; do git push -q origin e09_persona_replay && { echo "pushed $(git rev-parse --short HEAD) $(date -u +%T)"; break; }; sleep 10; done
