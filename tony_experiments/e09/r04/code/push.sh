#!/bin/bash
# copy results into the repo checkout (branch e09_persona_replay, folder e09/r04 only), scan, commit, rebase, push
# (R02's code/push.sh adapted: e09/r04, model list, `git pull --rebase` before every push, e09/r01 + e09/r02 unchanged check)
W=/workspace/e09/r04
G=$W/gh/repo
D=$G/e09/r04
exec 9>$W/logs/push.lock; flock 9
mkdir -p $D/{code,data,rollouts,judgments,partb,results,states,train,logs}
cp $W/code/*.py $W/code/*.sh $W/code/*.json $W/code/*.txt $D/code/ 2>/dev/null
for f in $W/data/*; do [ -f "$f" ] && cp "$f" $D/data/; done
cp $W/rollouts/*.jsonl $W/rollouts/*.done $D/rollouts/ 2>/dev/null
cp $W/judgments/* $D/judgments/ 2>/dev/null
cp $W/partb/* $D/partb/ 2>/dev/null
cp -r $W/results/* $D/results/ 2>/dev/null
cp $W/push_states/* $D/states/ 2>/dev/null
mkdir -p $D/train/Ssarc_ref && cp $W/adapters_ref/Ssarc/*.json* $D/train/Ssarc_ref/ 2>/dev/null
for n in Rsarc RSsarc Ssarc2; do [ -d $W/adapters/$n ] && mkdir -p $D/train/$n && cp $W/adapters/$n/*.json* $D/train/$n/ 2>/dev/null; done
for n in stories Rsarc RSsarc; do [ -d $W/dry/$n ] && mkdir -p $D/train/dry_$n && cp $W/dry/$n/*.json* $D/train/dry_$n/ 2>/dev/null; done
cp $W/logs/*.log $W/logs/*.jsonl $W/logs/*.json $W/logs/*.txt $D/logs/ 2>/dev/null
cp $W/STATUS.md $D/STATUS.md 2>/dev/null; cp $W/README.md $D/README.md 2>/dev/null
# split anything over 45 MB (re-split from the fresh copy each time)
find $D -type f -size +45M ! -name '*.part*' | while read f; do rm -f "$f".part*; split -b 45M -d "$f" "$f.part"; rm "$f"; echo "split $f"; done
/usr/bin/python3 -I $W/code/secret_scan.py $D || { echo "push aborted: secret scan"; exit 1; }
cd $G
git add -A e09/r04 && git commit -qm "${1:-E09 R04 update} ($(date -u +%H:%M) UTC)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo committed
for i in 1 2 3; do
  git pull -q --rebase origin e09_persona_replay || { git rebase --abort 2>/dev/null; sleep 10; continue; }
  git diff --quiet 243f98e -- e09/r01 e09/r02 || { echo "push aborted: e09/r01 or e09/r02 differs from 243f98e"; exit 1; }
  git push -q origin e09_persona_replay && { echo "pushed $(git rev-parse --short HEAD) $(date -u +%T)"; break; }
  sleep 10
done
